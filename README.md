# Voice Studio — miễn phí

[Mở Voice Studio trên Google Colab](https://colab.research.google.com/github/lsmedia2105/lsmedia/blob/main/Voice-Studio-Colab.ipynb)

Giao diện web tiếng Việt, responsive, gồm OmniVoice, Piper, Coqui XTTS và Chatterbox. Không tích hợp dịch vụ API trả phí. Clone cần GPU trong workflow này; máy yếu nên dùng notebook Colab đi kèm. Colab miễn phí không đảm bảo cấp GPU hoặc thời gian chạy.

## Dùng trên Colab (khuyến nghị)

1. Bấm link Colab ở trên; không cần tải hoặc upload ZIP.
2. Đăng nhập Google, chọn Runtime → Change runtime type → T4 GPU → Save.
3. Chọn Runtime → Run all (Chạy tất cả). Notebook có ba ô: lấy source từ GitHub, cài engine, mở giao diện.
4. Mặc định cài OmniVoice. Có thể chọn engine khác bằng danh sách ở ô cài đặt trước khi chạy; Piper tự tải giọng tiếng Việt nhẹ và không cần GPU.
5. Trong giao diện, chọn OmniVoice, upload mẫu WAV/FLAC 3–10 giây, nhập chính xác lời trong mẫu, xác nhận quyền sử dụng giọng và tạo âm thanh.

Nếu repository riêng tư, Colab có thể cần bạn cho phép truy cập GitHub và lệnh clone trong runtime có thể không truy cập được source; repository công khai mới hỗ trợ luồng không cần xác thực này. Không đặt token vào notebook.

Lần đầu cần tải model từ Hugging Face. Những lần tiếp theo trong cùng phiên giữ model và cache prompt OmniVoice. Đổi engine sẽ giải phóng engine cũ. Không tải cả bốn model cùng lúc.

## Chạy local

Khuyến nghị Python 3.12. Windows có thể mở `start-local.bat` để cài phần web và chạy server, sau đó cài engine theo hướng dẫn dưới.

```sh
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows thay bằng: .venv\Scripts\activate
pip install -r requirements.txt
python install_engine.py omnivoice
python server.py
```

Trên máy chạy server, mở trình duyệt tại `http://127.0.0.1:8000`. Giao diện onboarding cloud không hỗ trợ preview loopback. Notebook Colab dùng cơ chế iframe của Colab, không tạo link public.

Cài một engine bổ sung bằng `python install_engine.py piper`, `coqui` hoặc `chatterbox`. Mỗi engine dùng virtualenv riêng vì phiên bản torch/transformers khác nhau. Việc cài engine clone có thể tải nhiều GB thư viện. GPU NVIDIA được khuyến nghị; Apple MPS chưa được tích hợp trong bản này.

### Piper trên CPU

Piper chỉ đọc giọng có sẵn, không clone.

Để cài nhanh giọng tiếng Việt nhẹ (khoảng 28 MB, 65 người đọc), chạy `python prepare_piper.py`, rồi restart server. Server tự nhận model này, không cần đặt biến môi trường. Chất lượng model là `x_low`; dataset VIVOS có giấy phép CC BY-NC-SA 4.0, dành cho sử dụng phi thương mại. Model card: https://huggingface.co/rhasspy/piper-voices/blob/main/vi/vi_VN/vivos/x_low/MODEL_CARD

Nếu muốn dùng model khác, ví dụ tiếng Anh:

```sh
mkdir -p .data/models
cd .data/models
../../.engines/piper/bin/python -m piper.download_voices en_US-lessac-medium
cd ../..
export PIPER_MODEL="$PWD/.data/models/en_US-lessac-medium.onnx"
export PIPER_LANGUAGE=en
python server.py
```

Giữ file `.onnx.json` cạnh `.onnx`. Windows dùng `.engines\piper\Scripts\python.exe` để tải và `set PIPER_MODEL=đường_dẫn_tuyệt_đối`, `set PIPER_LANGUAGE=en`. Có thể thay bằng model tiếng Việt nếu có model tương thích được phép sử dụng, rồi đặt `PIPER_LANGUAGE=vi`. UI chỉ cho chọn ngôn ngữ đã cấu hình.

### Model và giới hạn

| Engine | Chế độ | Ngôn ngữ / tùy chỉnh |
| --- | --- | --- |
| OmniVoice 0.2.1 | Clone GPU, mẫu 3–10s | Có tiếng Việt; tốc độ; 16/32 bước; yêu cầu bản chép mẫu |
| Piper 1.8.0 | Giọng có sẵn CPU | Ngôn ngữ tùy model; tốc độ |
| Coqui 0.27.5 / XTTS v2 | Clone GPU, mẫu 3–30s | Không tiếng Việt; tốc độ; cần đồng ý CPML phi thương mại |
| Chatterbox 0.1.7 Multilingual | Clone GPU, mẫu 3–30s | Không tiếng Việt; độ biểu cảm; bản này giữ tốc độ 1× |

Chatterbox giữ watermark tích hợp của nhà cung cấp. Giấy phép thư viện và trọng số từng model khác nhau; đọc giấy phép trước khi dùng thương mại. OmniVoice được kiểm tra theo repo k2-fsa/OmniVoice; các adapter khác đối chiếu API chính thức.

Cao độ là hậu xử lý riêng, không phải điều khiển cảm xúc model. Cài `pip install librosa==0.11.0` trong `.venv` server nếu cần. Âm lượng luôn có sẵn. Đổi cao độ quá nhiều có thể giảm độ giống mẫu. Bản này chỉ xuất WAV, chưa có MP3.

## Dữ liệu và trạng thái

- Mẫu upload vào máy chạy server khi tạo, chuyển về mono WAV và xóa sau khi tác vụ kết thúc. Không gửi mẫu tới API TTS trả phí.
- “Lưu mẫu” giữ audio và lời mẫu trong IndexedDB của trình duyệt. Có nút xóa; dữ liệu có thể mất nếu xóa dữ liệu trình duyệt hoặc đổi địa chỉ truy cập.
- Tối đa 50 tác vụ trong lịch sử phiên. File kết quả ở `.data/`, cần tải trước khi Colab hết hạn. Restart server làm mất lịch sử trong bộ nhớ; file cũ có thể vẫn tồn tại đến khi bạn xóa hoặc runtime kết thúc.
- Server dùng một worker model, xử lý một tác vụ mỗi lần. Không có đăng nhập; dành cho local hoặc phiên Colab cá nhân, không triển khai public trực tiếp.
- Nút giải phóng model dừng worker, giải phóng bộ nhớ. Download model phụ thuộc mạng; xem `.data/engine.log` khi lỗi.

## Kiểm tra đã thực hiện

```sh
pip install httpx==0.28.1
python -m unittest discover -s tests -v
node --check static/app.js
```

9 test API kiểm tra input, quyền sử dụng, ngôn ngữ, job, file WAV, lỗi engine và dọn mẫu. Inference trong test dùng mock, không đánh giá chất lượng giọng. Browser Chromium đã kiểm tra đổi engine, upload, lưu/dùng lại mẫu, reset consent và layout desktop/mobile. Piper đã cài và sinh WAV tiếng Việt thật trên CPU: hai lần tạo đều có âm thanh hợp lệ, lần hai dùng lại model; giải phóng model cũng đã kiểm tra. Ban đầu Hugging Face bị chặn; sau thay đổi cấu hình mạng đã tải model thành công. Chưa xác minh clone giọng thật của OmniVoice, Coqui và Chatterbox vì máy kiểm thử không có GPU. Notebook Colab chưa được chạy trên runtime Colab thực tế.

## Cấu trúc

`server.py`: API + quản lý tác vụ; `worker.py`: adapter và cache model; `install_engine.py`: môi trường engine; `static/`: giao diện; `Voice-Studio-Colab.ipynb`: launcher Colab. Thư mục `.engines`, `.venv`, `.data` không đưa vào gói source.
