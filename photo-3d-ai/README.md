# LS Photo → 3D AI

Nhập ảnh một vật thể, dùng **TripoSR** tạo mesh 3D đầy đủ, xem xoay và xuất GLB / OBJ / STL để mở trong Blender. Khác với `image-3d` (phù điêu), tool này chạy model AI suy luận phần khuất. Không phải editor Blender; không đảm bảo độ chính xác mặt sau, kích thước, topology hoặc khả năng in ngay. GLB giữ vertex color, không phải texture UV.

## Windows

1. Cài **Python 3.11 64-bit** từ python.org, bật Python Launcher khi cài.
2. Giải nén repository, mở thư mục **photo-3d-ai**.
3. Nhấp **INSTALL-WINDOWS.bat**, chờ tải thư viện (nhiều GB). Chỉ làm lần đầu hoặc khi cập nhật dependencies.
4. Nhấp **START-WINDOWS.bat**. Trình duyệt mở giao diện; nếu không tự mở, vào `http://127.0.0.1:7860` trên máy chạy tool. Giữ cửa sổ lệnh mở.
5. Upload ảnh, giữ cấu hình **Tiết kiệm RAM / VRAM**, bấm **Tạo vật thể 3D bằng AI**. Lần đầu tải model từ Hugging Face và model tách nền từ GitHub.
6. Tải GLB; trong Blender chọn File → Import → glTF 2.0. OBJ/STL cũng có sẵn; STL không có màu hoặc đơn vị vật lý.

## Máy yếu

- Mặc định lưới 96, chunk 512, một tác vụ mỗi lần; không tạo video hoặc bake texture tốn VRAM.
- TripoSR upstream báo khoảng 6 GB VRAM ở thiết lập mặc định. Chế độ nhỏ giảm bộ nhớ trích xuất lưới, **không bảo đảm model chạy được trên GPU 2–4 GB**. Không dùng FP16 chưa kiểm chứng.
- Chọn **CPU** nếu GPU thiếu VRAM hoặc driver không tương thích. CPU chậm hơn đáng kể, vẫn cần nhiều RAM. Khuyến nghị ít nhất 16 GB RAM, đóng ứng dụng khác; yêu cầu thực tế phụ thuộc ảnh/profile/hệ thống.
- Có nút giải phóng model. Khi OOM, model được dỡ; chọn CPU và tạo lại.
- Tách nền bằng u2netp CPU; có thể tắt nếu đã chuẩn bị ảnh nền đơn giản. Ảnh một vật thể rõ nét cho kết quả tốt hơn ảnh cả căn phòng.
- Nếu NVIDIA không được nhận: cập nhật driver hỗ trợ CUDA 12.1 hoặc dùng CPU. Không cần CUDA Toolkit / Visual Studio để build marching cubes.

## Linux / macOS CPU

Python 3.10–3.12 (3.11 khuyến nghị):

```sh
cd photo-3d-ai
python setup.py
.venv/bin/python app.py
```

## Model, quyền riêng tư, giới hạn xác minh

Ảnh xử lý tại máy, không gọi API AI trả phí; không tạo public link. File kết quả lưu `outputs/`; cache model ở `.cache/`. Cần Internet ban đầu: download.pytorch.org, pypi.org, files.pythonhosted.org, huggingface.co cùng host tải trọng số chuyển hướng của Hugging Face, và GitHub/release assets để tải rembg. Không tắt TLS khi gặp lỗi mạng.

TripoSR upstream MIT, nguồn VAST-AI-Research/TripoSR commit `107cefdc244c39106fa830359024f6a2f1c78871`. Thư mục `tsr/` được lấy từ bản đó; `tsr/models/isosurface.py` thay torchmcubes bằng scikit-image CPU để không cần biên dịch CUDA. Giữ thứ tự trục grid xyz của TripoSR. Bản quyền trong TRIPOSR-LICENSE. Đọc model card stabilityai/TripoSR và giấy phép các model phụ trước khi dùng thương mại.

Máy phát triển hiện không có GPU và truy cập Hugging Face bị chặn HTTP 403, nên **chưa xác minh inference AI thật hoặc mức VRAM/RAM thực tế**. Không coi kiểm thử adapter / giao diện là bằng chứng chất lượng AI. Windows launcher cần kiểm tra trên máy Windows thật.

## Kiểm tra phát triển

Đã cài PyTorch 2.5.1 CPU và dependencies trên Linux/Python 3.12; `pip check` đạt. Ba test đạt: marching cubes giữ đúng trục và tạo bề mặt kín, chuẩn hóa ảnh + xuất/đọc lại GLB/OBJ/STL với **AI giả lập**, và từ chối input trống. Server Gradio chạy và trả cấu hình upload ảnh / model viewer qua HTTP. Các kiểm tra này chưa thay thế inference model thật hoặc kiểm tra Windows/GPU.

```sh
.venv/bin/python -m unittest discover -s tests -v
```
