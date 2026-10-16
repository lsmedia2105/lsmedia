# Thỏ cảnh sát — Rabbit Officer V1

Model 3D stylized dựng riêng theo ảnh tham chiếu người dùng: thỏ xám tai dài, mắt tím, tai lót hồng, đồng phục xanh, áo giáp/huy hiệu, túi thắt lưng, găng, bảo vệ gối và giày có đầu ngón chân lộ lông. Tư thế mặc định chống tay vào hông. Không cần Ollama/TripoSR để mở.

Đây là **bộ nhân vật V1**, dùng được trên **tool V2**, không phải bản cập nhật phần mềm. Mặt sau được ước lượng; hình dáng, nét mặt và chi tiết là bản mô phỏng, chưa phải bản sao chính xác hoặc model sản xuất chính thức. Chưa có lông sợi, texture/PBR chi tiết, biểu cảm mặt, lip-sync hoặc chuyển động bàn tay riêng.

## Mở riêng để xem và tạo dáng

1. Giải nén ZIP.
2. Mở tool V2 bằng START-STUDIO.bat. Lưu dự án đang làm trước.
3. Bấm **Project**, chọn **Rabbit-Officer-V1.ls3d**. File này thay cảnh hiện tại, không thêm vào cảnh cũ.
4. Bấm tên nhân vật trong danh sách bên phải. Bảng **Tư thế nhân vật mô phỏng** xuất hiện.
5. Chọn Đứng/Ngồi/Ngồi xổm hoặc chỉnh cúi thân, hông, gối, tay, khuỷu. Tư thế đứng giữ góc chống hông cơ bản của model, các slider thay đổi thêm quanh trục X.
6. Lưu dự án `.ls3d` để giữ tư thế. Có bốn camera: toàn thân, chính diện, cận mặt và sau lưng.

## Thêm vào bối cảnh đang có

1. Mở bối cảnh của bạn rồi bấm **Nhập**, chọn **Rabbit-Officer-V1.glb**.
2. Khi tool yêu cầu, bấm lên sàn để đặt nhân vật. Tool chuẩn hóa model theo cạnh dài nhất (bao gồm tai); tăng tỉ lệ nếu cần.
3. Bấm **Tách nhóm thành vật thể riêng**, rồi chọn nhóm nhân vật còn lại trong danh sách. Lặp lại **hai lần tổng cộng** đến khi thấy bảng Tư thế.
4. Không tách sâu tiếp vào thân/tay/chân nếu muốn điều khiển toàn bộ rig qua bảng tư thế.
5. Đổi vị trí, góc xoay, tỉ lệ và tư thế. Chỉnh độ cao nếu đặt ngồi trên ghế hoặc cúi gối làm chân chưa chạm nền.

## Rig và file

Model sử dụng các nhóm khớp theo tên tương thích V2 (`pose-body`, `pose-head`, `pose-arm-*`, `pose-elbow-*`, `pose-thigh-*`, `pose-knee-*`). Các mảnh hình học đi theo khớp, không phải một mesh trơn bị uốn bằng skeleton/weight paint. Vì vậy một số chỗ khuỷu/hông có thể lộ giao mảnh khi bẻ nhiều. GLB giữ các nhóm này để chỉnh trong Blender, nhưng không phải humanoid rig chuẩn để retarget tự động/Mixamo. Không kèm animation clip.

- `Rabbit-Officer-V1.ls3d`: dự án mở trực tiếp trong studio, kèm camera và metadata tư thế.
- `Rabbit-Officer-V1.glb`: model để thêm vào cảnh khác hoặc mở trong Blender.
- `preview-model.png`: render kiểm tra model.
- `preview-studio.png`: ảnh model được mở trong V2 thực tế.

56 geometry / khoảng 45.818 đỉnh sau tối ưu. Đã kiểm tra GLB có mặt/đỉnh hữu hạn bằng trimesh; kiểm tra trong Chromium việc mở dự án, đổi ma trận khớp thật, lưu/mở lại tư thế và nhập GLB, tách hai lớp nhóm để điều khiển rig; không có lỗi JavaScript trong luồng kiểm tra. Chưa đo hiệu năng trên RX 580 Windows.

`build.mjs` và `build.html` trong repository là mã dựng để chỉnh tiếp. Từ gốc repository: `python -m http.server 8091 --directory scene-studio`, mở `/assets/rabbit-officer-v1/build.html` trên server đó. Không gọi API AI khi dựng model này.
