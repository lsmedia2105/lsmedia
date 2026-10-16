# LS Pixel Studio — ảnh tham chiếu, model AI và dựng cảnh

Studio web local cho workflow previz: lấy ảnh làm tham chiếu, dựng vật thể AI, bố trí nhân vật và bối cảnh, lưu góc máy, xuất ảnh/GLB.

## Giao diện studio

![Giao diện LS Pixel Studio](preview.png)

Bố cục theo video tham khảo: kho model phân nhóm/tìm kiếm ở trái; viewport 3D ở giữa; tab **Vật thể / Camera / AI / Shot** ở phải; thanh **Orbit / Di chuyển / Xoay / Tỉ lệ / Monitor** phía dưới. Monitor là render 16:9 thật của góc camera hiện tại, cập nhật định kỳ; phím M bật/tắt. HUD hiển thị tiêu cự và độ cao. Project mở dự án, Nhập chọn GLB, Xuất tải GLB, Lưu dự án tải `.ls3d`.

Bấm vật thể hoặc tên trong danh sách để hiện gizmo; kéo trục màu để di chuyển, E để xoay và R đổi kích thước. Có viền chọn, nhập thông số, nhãn previz và tên tiếng Anh cho AI. Hoàn tác/làm lại cảnh bằng hai nút trên cùng hoặc Ctrl+Z / Ctrl+Shift+Z (giữ tối đa 10 trạng thái; không hoàn tác camera/bookmark).

Kho có ba cảnh hình khối mẫu, gồm **Sân lễ & cổng đền** với nhân vật đại diện và ba góc máy. Đây là model thủ tục tự dựng, **không phải bộ nhân vật hay tài sản gốc trong video**. Dùng nhập GLB hoặc AI ảnh để thêm tài nguyên của bạn. Nút “Chữ previz” bật nhãn trong viewport và ảnh xuất.

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

## Dựng bối cảnh từ toàn ảnh bằng AI

1. Chọn ảnh và loại **Bối cảnh nhiều vật thể**. Bấm **Dựng toàn ảnh bối cảnh bằng AI**; chế độ này dùng toàn ảnh, không dùng vùng khoanh.
2. Depth Anything Small ước lượng độ sâu tương đối. Mask2Former COCO instance tìm các đồ vật nhận diện được. Mỗi vật được đưa qua TripoSR để dựng mesh, rồi đặt theo vị trí/độ sâu ước lượng trong ảnh.
3. Chế độ tiết kiệm dựng tối đa 3 đồ vật; chế độ cao hơn tối đa 6. Các model lần lượt chạy CPU, giải phóng model tách vật/độ sâu trước khi nạp TripoSR. Có thể mất nhiều thời gian và RAM; chưa đo trên RX 580.
4. Các mesh được đưa vào studio thành đối tượng riêng để chọn và kéo ngay. Nền được dựng thành mesh màu theo độ sâu, bỏ bề mặt của các vật đã dựng thành công. Vật lỗi giữ trên nền; trạng thái báo số vật dựng được, số bỏ qua và số lỗi.
5. Chỉnh vị trí/tỉ lệ và thêm model hoặc khối để hoàn thiện. Bấm một vật là hiện trục kéo, chọn E/R để xoay/đổi kích thước. Khung viền xanh xác định vật đang chọn. Nếu model là nhóm, dùng **Tách nhóm**.

**Giới hạn quan trọng:** đây là cảnh 3D **ước lượng từ một góc nhìn**, không phải căn phòng/ngoại cảnh đầy đủ mọi phía. Mesh nền chỉ chứa bề mặt nhìn thấy, có thể bị rách hoặc méo khi nhìn nghiêng; vùng bị che chưa được hoàn thiện. Vật không thuộc các lớp COCO, kiến trúc và đám đông có thể không được tách đúng. TripoSR ước lượng phần sau đồ vật, không bảo đảm giống vật thật. Các vật có thể sai hướng hoặc tỉ lệ, cần chỉnh lại. Kích thước và độ sâu không phải số đo thực tế. Không gọi kết quả này là tái tạo chính xác 360°.

Model bổ sung tải từ Hugging Face: `LiheYoung/depth-anything-small-hf` và `facebook/mask2former-swin-small-coco-instance`; đọc model card và giấy phép trước khi sử dụng. Dependencies đã có trong bộ cài AI; không dùng API trả phí hoặc thay kết quả AI bằng khối mẫu.

## Góc máy, dự án và xuất file

- Kéo trái: orbit; chuột phải: pan; cuộn: zoom. Bấm chọn vật tự hiện gizmo di chuyển. Q: orbit, W: di chuyển, E: xoay, R: tỉ lệ. Các phím tắt không kích hoạt khi đang gõ thông số.
- Chỉnh hướng nắng, tiêu cự; lưu góc máy theo tên. Gọi lại bằng danh sách bên phải.
- Bật nhãn tên từng vật để thêm hướng dẫn trong ảnh chụp; không đưa nhãn vào GLB.
- **Chụp góc máy** xuất PNG 1920×1080, không kèm lưới/gizmo.
- **Xuất GLB** xuất các vật đang hiện, mở trong Blender bằng File → Import → glTF 2.0. GLB có model/màu; camera bookmark và ánh sáng editor không được xuất GLB.
- **Lưu dự án** tải `.ls3d`, chứa hình khối, vật liệu, ảnh và các góc máy. **Mở dự án** để tiếp tục. Không tự lưu: lưu trước khi đóng trang. AI đang chạy bị mất trạng thái giao diện nếu reload; worker vẫn chạy tới khi hoàn tất hoặc server dừng.
- Model GLB nhập được chuẩn hóa cạnh dài khoảng 2 m để dễ đặt; cần chỉnh lại tỉ lệ, không phải số đo thật từ ảnh.

## Máy AMD RX 580

Editor dùng WebGL trên AMD/NVIDIA; không yêu cầu CUDA. AI chạy CPU riêng, có thể chậm nhiều phút và dùng nhiều RAM. Không giả lập hỗ trợ CUDA/DirectML trên RX 580. Đóng app khác khi dựng AI. Worker thoát sau mỗi lần tạo để trả bộ nhớ cho hệ điều hành. Kết quả/ảnh xử lý ở `scene-studio/.data/`, các bản xuất engine ở `photo-3d-ai/outputs/`; có thể xóa khi không cần.

## Kiểm tra và giới hạn xác minh

Đã kiểm tra bằng Chromium headless: thêm khối/bối cảnh, đặt vật thể, đổi mode, nhập thông số, bookmark, lưu/mở lại dự án có texture, nhập/xuất GLB và xuất PNG. Không có lỗi JavaScript trong luồng kiểm tra. Sáu test backend/ghép cảnh kiểm tra routes, input, hàng đợi, và báo kết quả/lỗi worker với subprocess giả lập; kiểm tra phép chiếu depth và xuất cảnh có các node riêng với dự đoán AI giả lập. Engine TripoSR có ba test adapter/pipeline riêng với inference giả lập.

**Chưa xác minh inference AI thật, chất lượng model, hiệu năng RX 580 hoặc Windows:** máy cloud không có GPU và bị chặn Hugging Face HTTP 403. Kiểm tra phần editor không chứng minh inference chạy thành công trên máy người dùng. Nếu AI báo lỗi tải model, kiểm tra Internet tới Hugging Face và các host tải trọng số; không tắt TLS.

Linux chạy editor bằng `python scene-studio/server.py` từ gốc repository. Chạy test bằng Python trong virtualenv AI đã cài: `.venv-photo3d/bin/python -m unittest discover -s scene-studio/tests -v` (trên Windows thay executable bằng `photo-3d-ai\.venv\Scripts\python.exe`). Engine AI cần Python và dependencies hướng dẫn trong `photo-3d-ai/README.md`.

Three.js 0.180.0 MIT nằm trong `vendor/`, giữ giấy phép THREE-LICENSE.txt. Engine TripoSR và giấy phép được lưu ở `photo-3d-ai/`.


Kiểm tra bổ sung: đã thử kéo trục X bằng chuột trong Chromium, xác nhận tọa độ vật thể đổi và Undo trả về tọa độ cũ; kiểm tra tab inspector, tìm model, tách sân lễ thành các đối tượng riêng, ba bookmark, Undo/Redo, monitor, nhãn, PNG và lưu/mở dự án. Luồng toàn ảnh → HTTP job → nhiều mesh độc lập được kiểm tra với phản hồi AI giả lập. Hai kiến trúc model mới import được trong bộ dependencies đã cài; **chưa tải trọng số hoặc chạy inference thật** vì giới hạn mạng đã nêu.
