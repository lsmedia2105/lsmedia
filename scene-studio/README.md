# LS Scene Studio — ảnh tham chiếu, model AI và dựng cảnh

Studio web local cho workflow previz: lấy ảnh làm tham chiếu, dựng vật thể AI, bố trí nhân vật và bối cảnh, lưu góc máy, xuất ảnh/GLB.

## Mở đúng tool trên Windows

1. Cài **Python 3.11 64-bit** từ python.org, giữ Python Launcher khi cài.
2. Giải nén toàn bộ repository; nhấp **START-STUDIO.bat** ở thư mục ngoài cùng. Giữ cửa sổ lệnh mở. Nếu trình duyệt không tự mở, vào `http://127.0.0.1:8090` trên máy chạy tool.
3. Để dùng AI, chạy **photo-3d-ai/INSTALL-WINDOWS.bat** một lần rồi mở lại studio. Cài AI tải nhiều GB; editor vẫn chạy không cần cài thư viện AI.

## Nhân vật hoặc đồ vật từ ảnh

1. Chuyển sang **Ảnh → 3D**, chọn ảnh PNG/JPG/WEBP dưới 15 MB / 40 triệu pixel.
2. Kéo chuột khoanh một nhân vật/đồ vật, hoặc bấm **Toàn ảnh**.
3. Chọn **Nhân vật / đồ vật**, bấm **Dựng vùng ảnh bằng AI**.
4. Worker thực sự gọi TripoSR trong virtualenv hiện có, tách nền và xuất mesh GLB. Không thay thế bằng ảnh nổi hoặc model mẫu khi AI lỗi. Nếu lỗi, tool hiển thị lỗi để xử lý.
5. Sau khi AI hoàn tất, bấm lên sàn để đặt model. Chọn W/E/R hoặc nhập thông số bên phải để chỉnh.

Phần khuất do AI đoán; model chưa có rig/xương, không có cam kết nhận diện đúng mặt hoặc giữ chính xác trang phục. AI lần đầu tải trọng số từ Hugging Face. Worker dùng CPU cho RX 580 Windows; giảm lưới/chunk không làm model nhỏ đi. Khuyến nghị ít nhất 16 GB RAM, không bảo đảm đủ cho mọi tác vụ.

## Dựng bối cảnh theo ảnh

1. Chọn ảnh cả bối cảnh và loại **Bối cảnh nhiều vật thể**.
2. Khoanh riêng một đồ vật/công trình nhìn rõ → dựng AI → bấm đặt vào cảnh. Lặp lại cho các vật cần dựng.
3. Thêm nền, tường, cột hoặc GLB có sẵn từ thư viện. Dùng **Đặt ảnh thành bảng tham chiếu 2D** để đối chiếu bố cục khi sắp xếp. Bảng ảnh được ghi nhãn rõ là 2D.
4. Chỉnh vị trí, góc xoay, tỉ lệ, màu; nhân bản, ẩn/hiện, xóa. **Tách nhóm** để chỉnh từng bộ phận nếu model nhập hoặc bối cảnh mẫu là group.

**Giới hạn:** chưa có AI phân tách tự động toàn cảnh, đo độ sâu/kích thước chính xác hoặc tự đặt đúng mọi vật từ một ảnh. Người dùng khoanh và bố trí từng phần. TripoSR vốn tạo một vật thể, không phải model chuyên dựng cả căn phòng; vật bị che và kiến trúc phức tạp có thể tạo sai. Không gọi việc đặt ảnh phẳng là tạo bối cảnh 3D.

## Góc máy, dự án và xuất file

- Kéo trái: orbit; chuột phải: pan; cuộn: zoom. Q: orbit, W: di chuyển, E: xoay, R: tỉ lệ. Các phím tắt không kích hoạt khi đang gõ thông số.
- Chỉnh hướng nắng, tiêu cự; lưu góc máy theo tên. Gọi lại bằng danh sách bên phải.
- Bật nhãn tên từng vật để thêm hướng dẫn trong ảnh chụp; không đưa nhãn vào GLB.
- **Chụp góc máy** xuất PNG 1920×1080, không kèm lưới/gizmo.
- **Xuất GLB** xuất các vật đang hiện, mở trong Blender bằng File → Import → glTF 2.0. GLB có model/màu; camera bookmark và ánh sáng editor không được xuất GLB.
- **Lưu dự án** tải `.ls3d`, chứa hình khối, vật liệu, ảnh và các góc máy. **Mở dự án** để tiếp tục. Không tự lưu: lưu trước khi đóng trang. AI đang chạy bị mất trạng thái giao diện nếu reload; worker vẫn chạy tới khi hoàn tất hoặc server dừng.
- Model GLB nhập được chuẩn hóa cạnh dài khoảng 2 m để dễ đặt; cần chỉnh lại tỉ lệ, không phải số đo thật từ ảnh.

## Máy AMD RX 580

Editor dùng WebGL trên AMD/NVIDIA; không yêu cầu CUDA. AI chạy CPU riêng, có thể chậm nhiều phút và dùng nhiều RAM. Không giả lập hỗ trợ CUDA/DirectML trên RX 580. Đóng app khác khi dựng AI. Worker thoát sau mỗi lần tạo để trả bộ nhớ cho hệ điều hành. Kết quả/ảnh xử lý ở `scene-studio/.data/`, các bản xuất engine ở `photo-3d-ai/outputs/`; có thể xóa khi không cần.

## Kiểm tra và giới hạn xác minh

Đã kiểm tra bằng Chromium headless: thêm khối/bối cảnh, đặt vật thể, đổi mode, nhập thông số, bookmark, lưu/mở lại dự án có texture, nhập/xuất GLB và xuất PNG. Không có lỗi JavaScript trong luồng kiểm tra. Bốn test backend kiểm tra routes, input, hàng đợi, và báo kết quả/lỗi worker với subprocess giả lập. Engine TripoSR có ba test adapter/pipeline riêng với inference giả lập.

**Chưa xác minh inference AI thật, chất lượng model, hiệu năng RX 580 hoặc Windows:** máy cloud không có GPU và bị chặn Hugging Face HTTP 403. Kiểm tra phần editor không chứng minh inference chạy thành công trên máy người dùng. Nếu AI báo lỗi tải model, kiểm tra Internet tới Hugging Face và các host tải trọng số; không tắt TLS.

Linux chạy editor bằng `python scene-studio/server.py` từ gốc repository. Chạy test: `python -m unittest discover -s scene-studio/tests -v`. Engine AI cần Python và dependencies hướng dẫn trong `photo-3d-ai/README.md`.

Three.js 0.180.0 MIT nằm trong `vendor/`, giữ giấy phép THREE-LICENSE.txt. Engine TripoSR và giấy phép được lưu ở `photo-3d-ai/`.
