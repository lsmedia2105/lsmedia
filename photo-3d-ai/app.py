"""Single-image AI reconstruction, local UI; TripoSR inference, not relief."""
import gc
import os
from pathlib import Path
import threading
import uuid

ROOT = Path(__file__).resolve().parent
os.environ.setdefault('HF_HOME', str(ROOT / '.cache' / 'huggingface'))
os.environ.setdefault('U2NET_HOME', str(ROOT / '.cache' / 'rembg'))
os.environ.setdefault('GRADIO_ANALYTICS_ENABLED', 'False')
import gradio as gr
import numpy as np
from PIL import Image, ImageOps
import rembg
import torch
from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground

OUTPUTS = ROOT / 'outputs'
OUTPUTS.mkdir(exist_ok=True)
LOCK = threading.Lock()
PROFILES = {'Tiết kiệm RAM / VRAM': (96, 512), 'Cân bằng': (160, 2048), 'Chi tiết cao': (256, 4096)}
MODEL = None
DEVICE = None
BG_SESSION = None

def unload():
    global MODEL, DEVICE, BG_SESSION
    with LOCK:
        MODEL = DEVICE = BG_SESSION = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    return 'Đã giải phóng model khỏi bộ nhớ.'

def prepare_image(path, cut_background):
    with Image.open(path) as original:
        if original.width * original.height > 40_000_000:
            raise gr.Error('Ảnh quá lớn. Hãy dùng ảnh dưới 40 triệu pixel.')
        image = ImageOps.exif_transpose(original).convert('RGBA')
    image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    if cut_background:
        global BG_SESSION
        if BG_SESSION is None:
            BG_SESSION = rembg.new_session('u2netp', providers=['CPUExecutionProvider'])
        image = remove_background(image, BG_SESSION)
    alpha = np.array(image.getchannel('A'))
    if np.max(alpha) == 0:
        raise gr.Error('Ảnh không còn vật thể sau tách nền. Hãy tắt tách nền hoặc đổi ảnh.')
    image = resize_foreground(image, .85)
    arr = np.asarray(image).astype(np.float32) / 255
    rgb = arr[:, :, :3] * arr[:, :, 3:4] + .5 * (1-arr[:, :, 3:4])
    return Image.fromarray(np.uint8(np.clip(rgb, 0, 1) * 255))

def generate(path, profile, device_mode, cut_background, progress=gr.Progress()):
    global MODEL, DEVICE
    if not path:
        raise gr.Error('Chọn ảnh một vật thể trước.')
    if Path(path).stat().st_size > 15 * 1024 * 1024:
        raise gr.Error('Ảnh tối đa 15 MB.')
    if profile not in PROFILES or device_mode not in ('Tự động', 'CPU'):
        raise gr.Error('Cấu hình không hợp lệ.')
    device = 'cuda:0' if device_mode == 'Tự động' and torch.cuda.is_available() else 'cpu'
    resolution, chunk = PROFILES[profile]
    with LOCK:
        try:
            progress(.05, desc='Chuẩn bị ảnh / tải model tách nền ở lần đầu…')
            image = prepare_image(path, cut_background)
            if MODEL is None or DEVICE != device:
                MODEL = None
                gc.collect()
                if torch.cuda.is_available(): torch.cuda.empty_cache()
                progress(.12, desc='Tải TripoSR lần đầu (nhiều GB), cần Internet…')
                candidate = TSR.from_pretrained('stabilityai/TripoSR', config_name='config.yaml', weight_name='model.ckpt')
                candidate.to(device)
                candidate.eval()
                MODEL, DEVICE = candidate, device
            MODEL.renderer.set_chunk_size(chunk)
            progress(.35, desc=f'AI đang dựng vật thể trên {device}. CPU có thể mất nhiều phút…')
            with torch.inference_mode():
                codes = MODEL([image], device=device)
                progress(.65, desc='Trích xuất bề mặt 3D và màu…')
                mesh = MODEL.extract_mesh(codes, has_vertex_color=True, resolution=resolution)[0]
            if not len(mesh.vertices) or not len(mesh.faces):
                raise gr.Error('AI chưa tìm thấy bề mặt. Hãy thử ảnh rõ một vật, ít nền.')
            folder = OUTPUTS / uuid.uuid4().hex
            folder.mkdir()
            glb, obj, stl = (folder / ('model.' + ext) for ext in ('glb','obj','stl'))
            mesh.export(glb); mesh.export(obj); mesh.export(stl)
            image.save(folder / 'input.png')
            progress(1, desc='Hoàn tất')
            return str(glb), str(glb), str(obj), str(stl), f'Hoàn tất trên {device} · {len(mesh.vertices):,} đỉnh · {len(mesh.faces):,} mặt. Mở GLB trong Blender để giữ màu.'
        except torch.OutOfMemoryError:
            MODEL = DEVICE = None
            gc.collect()
            if torch.cuda.is_available(): torch.cuda.empty_cache()
            raise gr.Error('Hết bộ nhớ. Chọn Tiết kiệm RAM / VRAM; nếu vẫn lỗi chọn CPU. Độ chi tiết thấp chỉ giảm bộ nhớ bước tạo lưới, không giảm kích thước model AI.')
        except gr.Error:
            raise
        except Exception as exc:
            raise gr.Error(f'Chưa tạo được model: {type(exc).__name__}: {exc}. Kiểm tra Internet tải model, RAM và cửa sổ chạy tool.') from exc

hardware = f'NVIDIA: {torch.cuda.get_device_name(0)}' if torch.cuda.is_available() else 'Đang dùng CPU — chưa phát hiện NVIDIA CUDA khả dụng'
with gr.Blocks(title='LS Photo → 3D AI', theme=gr.themes.Soft()) as demo:
    gr.Markdown('# LS Photo → 3D AI\nNhập ảnh **một vật thể** → TripoSR dựng hình khối mọi phía → xuất file mở trong Blender. AI phải đoán phần khuất, không đảm bảo giống vật thật hoặc đúng kích thước.')
    gr.Markdown(f'**Thiết bị:** {hardware}')
    with gr.Row():
        with gr.Column():
            photo = gr.Image(type='filepath', label='Ảnh vật thể · PNG / JPG / WEBP', sources=['upload'])
            quality = gr.Dropdown(list(PROFILES), value='Tiết kiệm RAM / VRAM', label='Cấu hình')
            device = gr.Radio(['Tự động', 'CPU'], value='Tự động', label='Thiết bị (card không đủ bộ nhớ: chọn CPU)')
            cut = gr.Checkbox(value=True, label='Tự tách nền (model nhỏ u2netp, chạy CPU)')
            run = gr.Button('Tạo vật thể 3D bằng AI', variant='primary')
            release = gr.Button('Giải phóng bộ nhớ model')
        with gr.Column():
            preview = gr.Model3D(label='Xoay xem vật thể 3D', height=480)
            status = gr.Textbox(label='Trạng thái', interactive=False)
            with gr.Row():
                glb_file = gr.File(label='GLB · giữ màu')
                obj_file = gr.File(label='OBJ · hình khối')
                stl_file = gr.File(label='STL · in 3D')
    gr.Markdown('Chọn ảnh rõ, thấy trọn một vật, nền đơn giản. Lần đầu tải trọng số AI nhiều GB. Không gửi ảnh tới API AI; model chạy tại máy. Máy yếu nên có ít nhất 16 GB RAM (khuyến nghị, không bảo đảm). GPU dưới mức bộ nhớ cần thiết có thể vẫn lỗi: chuyển CPU. File lưu trong `outputs`; tự xóa khi không cần. Đây chưa phải trình chỉnh sửa mesh như Blender.')
    run.click(generate, [photo, quality, device, cut], [preview, glb_file, obj_file, stl_file, status], concurrency_limit=1, concurrency_id='model')
    release.click(unload, outputs=status, concurrency_limit=1, concurrency_id='model')

if __name__ == '__main__':
    demo.queue(max_size=4).launch(server_name='127.0.0.1', server_port=7860, inbrowser=True, share=False, allowed_paths=[str(OUTPUTS)])
