# LS Pixel Studio — các phiên bản

## V1

Sửa lỗi Windows `UnicodeEncodeError: 'charmap' codec can't encode character` khi worker in tiếng Việt vào log. Server truyền UTF-8 cho worker, worker và ứng dụng AI cấu hình stdout/stderr UTF-8 trước khi nạp model. Thông báo lỗi không còn mặc định quy mọi lỗi thành thiếu RAM hoặc lỗi mạng.

Cập nhật: đóng tool, giải nén ZIP V1 và copy nội dung vào thư mục bản cũ, thay thế file trùng. Giữ `.venv`, `.cache`, `outputs` và `.data`. Không cần chạy lại INSTALL-WINDOWS.bat vì không đổi dependencies. Mở lại START-STUDIO.bat và tạo lại model. Kiểm thử tự động đã xác nhận worker hoàn tất với stdout ban đầu là cp1252, dùng inference giả lập; chưa xác minh inference thật trên Windows/GPU người dùng.
