"""Local studio server. No third-party dependencies required for the editor."""
import base64
import binascii
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import threading
import uuid
import webbrowser
import urllib.request

ROOT = Path(__file__).resolve().parent
DATA = ROOT / '.data'
DATA.mkdir(exist_ok=True)
JOBS = {}
LOCK = threading.Lock()
ENGINE = ROOT.parent / 'photo-3d-ai'

def engine_python():
    name = 'Scripts/python.exe' if sys.platform == 'win32' else 'bin/python'
    for folder in [ENGINE / '.venv', ROOT.parent / '.venv-photo3d']:
        candidate = folder / name
        if candidate.is_file(): return candidate
    return None

def run_job(job_id, folder, profile, kind="character"):
    job = JOBS[job_id]
    try:
        job.update(status='running', message='Đang tải model / dựng 3D. CPU có thể mất nhiều phút. Xem cửa sổ chạy tool.')
        worker_env = os.environ.copy()
        worker_env.update(PYTHONUTF8='1', PYTHONIOENCODING='utf-8:backslashreplace')
        with (folder / 'engine.log').open('w', encoding='utf-8') as log:
            result = subprocess.run([str(engine_python()), '-X', 'utf8', str(ROOT / 'worker.py'), str(folder), profile, kind], cwd=ENGINE, stdout=log, stderr=subprocess.STDOUT, env=worker_env)
        if result.returncode != 0 or not (folder / 'model.glb').is_file():
            tail = (folder / 'engine.log').read_text(encoding='utf-8', errors='replace')[-1600:]
            raise RuntimeError(tail)
        message='Đã dựng model AI. Bấm vào sàn để đặt trong cảnh.'
        if kind=='scene':
            report=json.loads((folder/'report.json').read_text(encoding='utf-8'))
            message=f"Đã dựng cảnh: {report['objects']} vật thể riêng; {report['skipped']} vật bỏ qua; {len(report['warnings'])} vật lỗi. " + report['note']
        job.update(status='done', message=message, kind=kind, url=f'/models/{job_id}')
    except Exception as exc:
        detail = str(exc)[-1600:]
        hint = 'Worker gặp lỗi. Xem chi tiết bên dưới.'
        if 'UnicodeEncodeError' in detail:
            hint = 'Lỗi mã hóa log trên Windows. Hãy cập nhật bản V1 và mở lại tool.'
        elif 'OutOfMemory' in detail or 'MemoryError' in detail:
            hint = 'Thiếu bộ nhớ khi dựng AI. Đóng ứng dụng khác hoặc dùng cấu hình tiết kiệm.'
        job.update(status='error', message=hint + ' ' + detail)

def run_plan_job(job_id, folder, character=False):
    job=JOBS[job_id]
    job.update(status='running',message='Model thị giác local đang đọc bố cục ảnh. CPU có thể chậm nhiều phút…')
    try:
        from scene_plan import from_image
        plan=from_image(folder/'input.png',character=character)
        (folder/'plan.json').write_text(json.dumps(plan,ensure_ascii=False),encoding='utf-8')
        job.update(status='done',kind='proxy',plan=plan,message=f"Đã đọc bố cục {len(plan['objects'])} thành phần. Các mô hình là khối đại diện, không phải mesh chi tiết giống vật gốc.")
    except Exception as exc:job.update(status='error',message=str(exc))

def run_camera_job(job_id,prompt,subjects):
    JOBS[job_id].update(status='running',message='AI local đang phân tích prompt góc máy…')
    try:
        from camera_ai import plan
        shots=plan(prompt,subjects)
        JOBS[job_id].update(status='done',kind='camera',shots=shots,message=f'AI đã tạo {len(shots)} góc máy. Có thể chỉnh tay tiếp.')
    except Exception as exc:JOBS[job_id].update(status='error',message=str(exc))

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def send_json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path == '/api/diagnostics':
            model=os.environ.get('LS_VISION_MODEL','qwen2.5vl:3b')
            result={'ollama':False,'model':model,'model_available':False,'triposr_environment':engine_python() is not None}
            try:
                opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
                with opener.open('http://127.0.0.1:11434/api/tags',timeout=2) as response:tags=json.load(response)
                result['ollama']=True
                result['model_available']=any(item.get('name')==model or item.get('model')==model for item in tags.get('models',[]))
                result['message']='Đã tìm thấy model local. Trạng thái này chưa kiểm tra inference.' if result['model_available'] else 'Ollama đang chạy nhưng chưa có model. Chạy SETUP-VISION-V2.bat để tải.'
            except Exception:
                result['message']='Chưa kết nối được Ollama local. Cài/mở Ollama rồi chạy SETUP-VISION-V2.bat. Camera offline và preset vẫn dùng bình thường.'
            self.send_json(200,result);return
        if self.path == '/api/status':
            self.send_json(200, {'ai_installed': engine_python() is not None, 'device_note': 'RX 580 dùng CPU cho AI; trình xem 3D dùng WebGL.'}); return
        if self.path.startswith('/api/jobs/'):
            job = JOBS.get(self.path.removeprefix('/api/jobs/'))
            self.send_json(200 if job else 404, job or {'message':'Không tìm thấy tác vụ'}); return
        if self.path.startswith('/models/'):
            job_id = self.path.removeprefix('/models/')
            if len(job_id) != 32 or any(c not in '0123456789abcdef' for c in job_id): self.send_error(404); return
            path = DATA / job_id / 'model.glb'
            if not path.is_file(): self.send_error(404); return
            self.send_response(200); self.send_header('Content-Type','model/gltf-binary'); self.send_header('Content-Length',str(path.stat().st_size)); self.end_headers(); self.wfile.write(path.read_bytes()); return
        # Keep job inputs/logs and Python source off static routes.
        if self.path.split('?')[0] not in ['/', '/index.html', '/app.js', '/style.css', '/proxy.js', '/avatars.js', '/presets.js', '/camera-tools.js', '/examples/mars-reference.json', '/examples/characters-poses.json'] and not (self.path.startswith('/vendor/') and '..' not in self.path and self.path.endswith('.js')):
            self.send_error(404); return
        super().do_GET()
    def do_POST(self):
        if self.path not in ['/api/generate','/api/camera']: self.send_error(404); return
        if self.headers.get('Sec-Fetch-Site') == 'cross-site': self.send_error(403); return
        origin = self.headers.get('Origin')
        if origin and origin not in ['http://127.0.0.1:8090','http://localhost:8090']: self.send_error(403); return
        if self.headers.get('Content-Type','').split(';')[0] != 'application/json': self.send_error(415); return

        try:
            length = int(self.headers.get('Content-Length','0'))
            if not 0 < length <= 22*1024*1024: raise ValueError('Ảnh tối đa 15 MB')
            body = json.loads(self.rfile.read(length))
            if self.path=='/api/camera':
                prompt=body.get('prompt');subjects=body.get('subjects')
                if length>256*1024 or not isinstance(prompt,str) or not 0<len(prompt.strip())<=3000 or not isinstance(subjects,list) or len(subjects)>200:raise ValueError('Prompt hoặc danh sách chủ thể không hợp lệ')
                with LOCK:
                    if any(j['status'] in ['queued','running'] for j in JOBS.values()):
                        self.send_json(409, {'message':'Đang có tác vụ AI. Chờ hoàn tất rồi thử lại.'});return
                    job_id=uuid.uuid4().hex;JOBS[job_id]={'status':'queued','message':'Đang chờ AI đặt camera…'}
                threading.Thread(target=run_camera_job,args=(job_id,prompt,subjects),daemon=True).start()
                self.send_json(202,{'id':job_id});return
            profile = body.get('profile','low')
            kind = body.get('kind','character')
            if kind not in ['character','scene','proxy','avatar']: raise ValueError('Loại ảnh không hợp lệ')
            if profile not in ['low','medium']: raise ValueError('Cấu hình không hợp lệ')
            if kind not in ['proxy','avatar'] and not engine_python():
                self.send_json(409, {'message':'Chạy photo-3d-ai/INSTALL-WINDOWS.bat để cài AI trước.'}); return
            raw = base64.b64decode(body['image'].split(',',1)[-1], validate=True)
            if not raw or len(raw)>15*1024*1024: raise ValueError('Ảnh tối đa 15 MB')
            with LOCK:
                if any(j['status'] in ['queued','running'] for j in JOBS.values()):
                    self.send_json(409, {'message':'Đang có tác vụ AI. Chờ tác vụ hiện tại hoàn tất.'}); return
                job_id = uuid.uuid4().hex; folder = DATA / job_id; folder.mkdir()
                (folder / 'input.png').write_bytes(raw)
                JOBS[job_id] = {'status':'queued','message':'Đang chờ dựng model…'}
            threading.Thread(target=run_plan_job if kind in ['proxy','avatar'] else run_job,args=(job_id,folder,kind=='avatar') if kind in ['proxy','avatar'] else (job_id,folder,profile,kind),daemon=True).start()
            self.send_json(202, {'id':job_id})
        except (ValueError,KeyError,TypeError,binascii.Error) as exc: self.send_json(400, {'message':str(exc)})

if __name__ == '__main__':
    print('LS Scene Studio: http://127.0.0.1:8090', flush=True)
    server = ThreadingHTTPServer(('127.0.0.1',8090), Handler)
    webbrowser.open('http://127.0.0.1:8090')
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
