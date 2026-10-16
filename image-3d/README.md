# LS Image 3D Studio

Tool web tiếng Việt, nhập PNG/JPG/WEBP và tạo mô hình phù điêu 3D có mặt trước, mặt sau và thành kín. Độ sáng ảnh điều khiển độ nổi; đây không phải AI tái tạo vật thể đầy đủ từ một ảnh. Không cần GPU, API key, tài khoản hay tải ảnh lên server.

## Chạy

Từ thư mục repository:

```sh
python -m http.server 8080 --bind 127.0.0.1 --directory image-3d
```

Mở trình duyệt trên máy chạy tool ở cổng 8080. Không mở trực tiếp index.html bằng file:// vì ứng dụng dùng JavaScript modules. Trong cloud cần cơ chế chuyển tiếp cổng của nền tảng; onboarding không cung cấp preview loopback.

1. Chọn ảnh hoặc kéo vào ô nhập, hoặc bấm **Mở ảnh mẫu**.
2. Chỉnh độ nổi, độ dày, độ chi tiết và đảo sáng/tối.
3. Kéo chuột để xoay, cuộn để zoom, chuột phải để di chuyển.
4. Tải GLB (hình khối + ảnh màu), hoặc STL (hình khối không màu). File STL không có đơn vị: đặt kích thước trong slicer và kiểm tra trước khi in.

Ảnh giới hạn 15 MB / 40 triệu pixel. Model có cạnh dài 100 đơn vị. Ảnh trong suốt được ghép nền trắng để lấy độ nổi; đường viền mô hình vẫn hình chữ nhật. Độ sâu từ độ sáng chỉ là hiệu ứng phù điêu, không phải khoảng cách vật lý suy ra từ ảnh.

Three.js 0.180.0 được lưu trong vendor để chạy không cần CDN; giấy phép MIT kèm theo. Không có thư viện Python cần cài. Các file Voice Studio hiện có không bị thay đổi.
