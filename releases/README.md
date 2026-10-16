# LS Pixel Studio — các phiên bản

## V3

Preset IndexedDB có phân loại, tìm/đổi tên/xóa/xuất/nhập file; lưu cả cảnh. Nhập GLB có khớp tương thích tự hiện bảng pose; thêm pose sẵn, đầu và điều khiển hai bên độc lập. Camera tĩnh riêng với lens/cảm biến/FOV, gizmo camera, prompt offline hoặc Ollama, đánh số/thứ tự shot, xuất PNG theo tỉ lệ và ZIP storyboard có contact sheet/metadata. Không đổi dependencies Python so với V2; ffLate JavaScript đã kèm giấy phép. Xem `scene-studio/README-V3.md` để biết điều kiện và giới hạn AI (không phải tái tạo ảnh chính xác, chưa xác minh inference thật).

## V2

Thêm nhập bố cục JSON do ChatGPT/Claude viết; 18 mẫu thành phần trạm Sao Hỏa theo ảnh tham chiếu; năm kiểu nhân vật đại diện có khớp và điều khiển đứng/ngồi/cúi/gập tay chân. Mặc định ảnh được đưa vào luồng dựng bố cục mô phỏng, không phải TripoSR một vật. Có tùy chọn Ollama thị giác local để đọc ảnh thành bố cục (cần cài Ollama + tải model, chưa kiểm thử inference thật). Thư viện mẫu không tái tạo chính xác nhân vật gốc. Bộ cài Python AI không đổi dependencies; không cần cài lại TripoSR nếu đã dùng V1.

## V1

Sửa lỗi Windows `UnicodeEncodeError: 'charmap' codec can't encode character` khi worker in tiếng Việt vào log. Server truyền UTF-8 cho worker, worker và ứng dụng AI cấu hình stdout/stderr UTF-8 trước khi nạp model. Thông báo lỗi không còn mặc định quy mọi lỗi thành thiếu RAM hoặc lỗi mạng.

Cập nhật: đóng tool, giải nén ZIP V1 và copy nội dung vào thư mục bản cũ, thay thế file trùng. Giữ `.venv`, `.cache`, `outputs` và `.data`. Không cần chạy lại INSTALL-WINDOWS.bat vì không đổi dependencies. Mở lại START-STUDIO.bat và tạo lại model. Kiểm thử tự động đã xác nhận worker hoàn tất với stdout ban đầu là cp1252, dùng inference giả lập; chưa xác minh inference thật trên Windows/GPU người dùng.
