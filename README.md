**Bản V2:** dựng bố cục mô phỏng từ JSON do AI viết, cảnh Sao Hỏa mẫu và nhân vật đại diện có điều khiển tư thế. [Tải ZIP V2](https://github.com/lsmedia2105/lsmedia/raw/main/releases/LS-Pixel-Studio-V2.zip) · [Hướng dẫn V2](scene-studio/README.md). Bộ mẫu/nhập JSON không cần cài thêm AI; tự đọc ảnh trong app cần Ollama và model riêng, chưa xác minh inference thật. V2 không khôi phục chính xác mọi ảnh thành asset như bản gốc.

**Bản V1:** sửa lỗi `UnicodeEncodeError / cp1252` khi tạo model trên Windows. [Tải ZIP V1](https://github.com/lsmedia2105/lsmedia/raw/main/releases/LS-Pixel-Studio-V1.zip). Copy đè vào thư mục cũ, không cần cài lại AI.

## LS Scene Studio — bản studio dựng cảnh

**Mở `START-STUDIO.bat`** để dùng studio: ảnh tham chiếu, dựng từng vật thể bằng AI, bố trí nhân vật/bối cảnh, lưu góc máy, xuất PNG và GLB. [Hướng dẫn và giới hạn](scene-studio/README.md). Cần Python 3.11; cài AI qua `photo-3d-ai/INSTALL-WINDOWS.bat`. Bấm vật thể để hiện trục kéo như Blender. Chế độ bối cảnh xử lý toàn ảnh bằng AI độ sâu + tách vật + TripoSR; kết quả là cảnh ước lượng với nền chỉ gồm bề mặt nhìn thấy, chưa tái tạo chính xác toàn cảnh 360°.

---

## Tool ảnh → vật thể 3D bằng AI

Bản **TripoSR AI** nằm trong [`photo-3d-ai`](photo-3d-ai/README.md). Trên Windows, cài Python 3.11 64-bit, chạy `photo-3d-ai/INSTALL-WINDOWS.bat` một lần, sau đó mở **`START-3D-AI.bat`** ở thư mục này. Có chế độ tiết kiệm VRAM và CPU; card yếu vẫn có thể thiếu bộ nhớ. Xuất GLB/OBJ/STL mở trong Blender. Chưa xác minh inference thật ở máy cloud vì Hugging Face bị chặn.

Bản `image-3d` cũ là phù điêu từ độ sáng, khác với bản AI ở trên.

---

# Voice Studio — miễn phí

[Mở Voice Studio trên Google Colab](https://colab.research.google.com/github/lsmedia2105/lsmedia/blob/main/Voice-Studio-Colab.ipynb)

Giao diện web tiếng Việt, responsive, gồm OmniVoice, Piper, Coqui XTTS và Chatterbox. Không tích hợp dịch vụ API trả phí. Clone cần GPU trong workflow này; máy yếu nên dùng notebook Colab đi kèm. Colab miễn phí không đảm bảo cấp GPU hoặc thời gian chạy.

## Dùng trên Colab (khuyến nghị)

1. Bấm link Colab ở trên; không cần tải hoặc upload ZIP.
2. Đăng nhập Google, chọn Runtime → Change runtime type → T4 GPU → Save.
3. Chọn Runtime → Run all (Chạy tất cả). Notebook có ba ô: lấy source từ GitHub, cài engine, mở giao diện.
4. Mặc định cài OmniVoice. Có thể chọn engine khác bằng danh sách ở ô cài đặt trước khi chạy; Piper tự tải giọng tiếng Việt nhẹ và không cần GPU.
5. Trong giao diện, chọn OmniVoice, upload mẫu MP3/WAV/FLAC dài 3 giây–10 phút (tối đa 50 MB), giữ AI tự chép lời bật, nhập văn bản cần đọc, xác nhận quyền sử dụng giọng và tạo âm thanh.

Nếu repository riêng tư, Colab có thể cần bạn cho phép truy cập GitHub và lệnh clone trong runtime có thể không truy cập được source; repository công khai mới hỗ trợ luồng không cần xác thực này. Không đặt token vào notebook.

Lần đầu cần tải model từ Hugging Face. Những lần tiếp theo trong cùng phiên giữ model và cache prompt OmniVoice, không nhận dạng lại khi đoạn mẫu không đổi. Đổi engine sẽ giải phóng engine cũ. Không tải cả bốn model cùng lúc.

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
| OmniVoice 0.2.1 | Clone GPU, mẫu upload 3s–10 phút | Có tiếng Việt; tốc độ; 16/32 bước; AI tự chép lời |
| Piper 1.8.0 | Giọng có sẵn CPU | Ngôn ngữ tùy model; tốc độ |
| Coqui 0.27.5 / XTTS v2 | Clone GPU, tự lấy đoạn từ mẫu dài | Không tiếng Việt; tốc độ; cần đồng ý CPML phi thương mại |
| Chatterbox 0.1.7 Multilingual | Clone GPU, tự lấy đoạn từ mẫu dài | Không tiếng Việt; độ biểu cảm; bản này giữ tốc độ 1× |

Chatterbox giữ watermark tích hợp của nhà cung cấp. Giấy phép thư viện và trọng số từng model khác nhau; đọc giấy phép trước khi dùng thương mại. OmniVoice được kiểm tra theo repo k2-fsa/OmniVoice; các adapter khác đối chiếu API chính thức.

Cao độ là hậu xử lý riêng, không phải điều khiển cảm xúc model. Cài `pip install librosa==0.11.0` trong `.venv` server nếu cần. Âm lượng luôn có sẵn. Đổi cao độ quá nhiều có thể giảm độ giống mẫu. Bản này chỉ xuất WAV, chưa có MP3.

## Dữ liệu và trạng thái

- Mẫu MP3/WAV/FLAC upload vào máy chạy server khi tạo, giải mã và chuyển về mono WAV và xóa sau khi tác vụ kết thúc. Không gửi mẫu tới API TTS trả phí.
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

15 test API/worker kiểm tra input, quyền sử dụng, ngôn ngữ, job, file WAV, lỗi engine và dọn mẫu. Inference trong test dùng mock, không đánh giá chất lượng giọng. Browser Chromium đã kiểm tra đổi engine, upload, lưu/dùng lại mẫu, reset consent và layout desktop/mobile. Piper đã cài và sinh WAV tiếng Việt thật trên CPU: hai lần tạo đều có âm thanh hợp lệ, lần hai dùng lại model; giải phóng model cũng đã kiểm tra. Ban đầu Hugging Face bị chặn; sau thay đổi cấu hình mạng đã tải model thành công. Chưa xác minh clone giọng thật của OmniVoice, Coqui và Chatterbox vì máy kiểm thử không có GPU. Notebook Colab chưa được chạy trên runtime Colab thực tế.

## Cấu trúc

`server.py`: API + quản lý tác vụ; `reference_audio.py`: chuẩn hóa và chọn đoạn mẫu; `worker.py`: adapter và cache model; `install_engine.py`: môi trường engine; `static/`: giao diện; `Voice-Studio-Colab.ipynb`: launcher Colab. Thư mục `.engines`, `.venv`, `.data` không đưa vào gói source.

## Mẫu dài và AI chép lời

Nhận MP3/WAV/FLAC dài 3 giây–10 phút, tối đa 50 MB. File dài hơn khoảng 10 giây được chọn một đoạn khoảng 8 giây dựa trên mức hoạt động âm thanh, tránh đoạn đầu im lặng. Đây không phải nhận diện người nói hoặc tách giọng khỏi nhạc: hãy dùng file một người nói, ít tạp âm. UI hiển thị khoảng thời gian đã chọn sau khi tạo. Bộ chọn xử lý PCM theo khối; MP3 được giải mã một lần trước khi chọn để tránh lỗi seek của decoder.

OmniVoice mặc định bỏ trống `ref_text`, kích hoạt Whisper large-v3-turbo tích hợp để nhận dạng lời trong đoạn thực sự dùng. Whisper chạy CPU để giữ VRAM cho clone, cần tải thêm model ở lần đầu và có thể làm lần đầu chậm hơn. Không dùng API trả phí. Lời nhận dạng có thể sai; có tùy chọn tắt AI để nhập tay với mẫu 3–10 giây. Không dùng bản chép toàn bộ file dài vì không khớp đoạn đã cắt.

API/worker đã kiểm tra chọn đoạn file dài, MP3, chế độ không cần transcript, metadata lời nhận dạng và cache prompt bằng model giả lập. Chưa kiểm thử độ chính xác ASR tiếng Việt hoặc clone thật trên GPU trong máy này. Nội dung cần đọc vẫn do người dùng nhập; AI tự chép lời áp dụng cho ô lời mẫu.
