# TERRAN RESEARCH OUTPOST-7 — bộ cảnh V1

Bối cảnh 3D mô phỏng dựng riêng theo ảnh tham chiếu người dùng. Chạy được trong LS Pixel Studio V2, không cần Ollama hoặc TripoSR để mở. Đây là asset V1, không phải bản cập nhật phần mềm V3.

## Mở trong tool V2

1. Giải nén bộ cảnh ra một thư mục bất kỳ.
2. Mở START-STUDIO.bat như bình thường. **Lưu dự án đang làm trước**, vì mở dự án sẽ thay cảnh hiện tại.
3. Bấm **Project** ở thanh trên, chọn **Outpost7-V1.ls3d**. Không chọn file này bằng nút nhập bố cục JSON ở tab AI.
4. Chờ load, chọn bookmark **Ảnh tham chiếu · tổng thể** nếu cần. Nút **Lưới sàn** bật/tắt các đường lưới trong editor.
5. Bấm vật thể hoặc tên bên phải để kéo bằng trục. Xe, nhà kính, chảo, khối nhà, tháp, núi/đá là các đối tượng riêng. Bộ phận nhỏ bên trong một đối tượng có thể đã gộp theo vật liệu để giảm draw calls.
6. Có 4 góc máy: tổng thể, nhìn từ trên, cận xe, nhà kính/tháp. Chụp ảnh hoặc lưu dự án của bạn sau khi chỉnh.

## File đi kèm

- **Outpost7-V1.ls3d**: ưu tiên dùng file này để mở trong studio, giữ kích thước, vị trí và 4 bookmark.
- **Outpost7-V1.glb**: mô hình 3D mở trong Blender hoặc import vào một dự án khác. GLB không giữ camera bookmark. Studio V2 tự thu nhỏ model GLB khi nhập; cần tăng tỉ lệ nếu muốn cùng kích thước với dự án gốc. Mở .ls3d tránh bước này.
- **preview-studio.png**: ảnh kiểm tra cảnh thực sự mở trong studio.
- **preview-render.png**: ảnh render từ trình dựng, với nền cam, sương xa và ánh sáng riêng. Studio V2 vẫn dùng nền/ánh sáng editor; màu trời và độ tương phản khác ảnh render này.

## Nội dung và mức chi tiết

82 đối tượng gốc; GLB có 112 geometry, khoảng 124 nghìn đỉnh trước xuất. Gồm địa hình cát, dãy vách đá trái, núi xa, tháp nghiên cứu có gân/trụ và ăng ten, nhà kính khung vòm/cây, các phòng/hành lang, chảo vệ tinh nghiêng, ăng ten lưới, cửa khí/cầu thang, bãi đáp, xe sáu bánh có lốp/gai và thiết bị, hàng hóa, bình áp suất, đá tiền cảnh và hai hành tinh.

Mô hình là bản previz stylized, không phải bản tái tạo ảnh chân thực: kích thước và phần khuất được ước lượng; không có chữ/logo và toàn bộ texture chi tiết của ảnh tham chiếu, không có rig/animation cho xe hoặc cửa. Cảnh theo ảnh này không có nhân vật nên không thêm nhân vật ngoài yêu cầu. Địa hình/hành tinh có thể làm nút Toàn cảnh zoom xa; dùng bookmark tổng thể để trở lại góc phù hợp.

Đã kiểm tra GLB bằng trimesh, xác nhận geometry có mặt/đỉnh hữu hạn; mở .ls3d trong Chromium với V2, xác nhận 82 đối tượng, di chuyển riêng xe, bốn bookmark và xuất PNG Full HD; không có lỗi JavaScript trong luồng kiểm tra. Chưa đo FPS trên RX 580 Windows của người dùng. Bộ phận theo vật liệu được gộp để giảm draw calls.

## Mã dựng để chỉnh tiếp (trong repository)

`build.mjs` tạo hình học có seed cố định; `build.html` render và xuất dữ liệu. Từ gốc repository, chạy `python -m http.server 8091 --directory scene-studio`, rồi mở trang `/assets/outpost7-v1/build.html` trên server đó. Mã dùng Three.js MIT đã có trong vendor, không gọi API AI. Gói tải về chỉ cần các file asset và hướng dẫn; không cần chạy mã dựng.
