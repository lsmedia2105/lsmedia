import asyncio
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import soundfile as sf
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
DATA = ROOT / '.data'
DATA.mkdir(exist_ok=True)
DEFAULT_PIPER = DATA / 'models' / 'vi_VN-vivos-x_low.onnx'
if not os.environ.get('PIPER_MODEL') and DEFAULT_PIPER.is_file():
    os.environ['PIPER_MODEL'] = str(DEFAULT_PIPER)
    os.environ.setdefault('PIPER_LANGUAGE', 'vi')
LANGUAGES = {'vi': 'Tiếng Việt', 'en': 'English', 'zh': '中文', 'zh-cn': '中文', 'ja': '日本語', 'ko': '한국어',
             'fr': 'Français', 'de': 'Deutsch', 'es': 'Español', 'ru': 'Русский', 'pt': 'Português'}
ENGINES = {
    'omnivoice': {'name': 'OmniVoice', 'note': 'Clone tiếng Việt · GPU', 'languages': [x for x in LANGUAGES if x != 'zh-cn'], 'clone': True},
    'piper': {'name': 'Piper', 'note': 'Giọng có sẵn · CPU nhẹ', 'languages': ['vi', 'en'], 'clone': False},
    'coqui': {'name': 'Coqui XTTS', 'note': 'Clone · không hỗ trợ tiếng Việt', 'languages': [x for x in LANGUAGES if x not in ('vi', 'zh')], 'clone': True},
    'chatterbox': {'name': 'Chatterbox', 'note': 'Clone · không hỗ trợ tiếng Việt', 'languages': [x for x in LANGUAGES if x not in ('vi', 'zh-cn')], 'clone': True},
}
JOBS = {}
LOCK = threading.Lock()
POOL = ThreadPoolExecutor(max_workers=1)
ACTIVE = None
WORKER = None
WORKER_ENGINE = None
LOG = None


def engine_python(engine):
    return ROOT / '.engines' / engine / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')


def piper_speakers():
    path = Path(os.environ.get('PIPER_MODEL', '/nonexistent') + '.json')
    try:
        config = json.loads(path.read_text())
        mapping = config.get('speaker_id_map') or {}
        return {str(value): name for name, value in mapping.items()} or {'0': 'Giọng mặc định'}
    except (OSError, ValueError):
        return {'0': 'Giọng mặc định'}


def stop_worker():
    global WORKER, WORKER_ENGINE, LOG
    if WORKER is not None:
        if WORKER.poll() is None:
            WORKER.terminate()
            try:
                WORKER.wait(timeout=10)
            except subprocess.TimeoutExpired:
                WORKER.kill()
                WORKER.wait()
        WORKER = None
    WORKER_ENGINE = None
    if LOG:
        LOG.close()
        LOG = None


def call_worker(engine, payload):
    global WORKER, WORKER_ENGINE, LOG
    if WORKER_ENGINE != engine or WORKER is None or WORKER.poll() is not None:
        stop_worker()
        LOG = (DATA / 'engine.log').open('w')
        WORKER = subprocess.Popen([str(engine_python(engine)), str(ROOT / 'worker.py'), engine],
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=LOG, text=True, cwd=ROOT)
        WORKER_ENGINE = engine
    WORKER.stdin.write(json.dumps(payload) + '\n')
    WORKER.stdin.flush()
    # A model's first download can take minutes. Keep the web server responsive.
    line = WORKER.stdout.readline()
    if not line:
        raise RuntimeError('Engine đã dừng. Xem .data/engine.log; kiểm tra GPU và thư viện.')
    reply = json.loads(line)
    if not reply.get('ok'):
        raise RuntimeError(reply.get('error', 'Engine thất bại'))


def postprocess(path, pitch, gain):
    audio, sr = sf.read(path, dtype='float32', always_2d=True)
    if not len(audio) or not np.isfinite(audio).all():
        raise ValueError('Âm thanh tạo ra trống hoặc không hợp lệ')
    if pitch:
        # Pitch change uses a separate optional library; speed stays unchanged.
        import librosa
        audio = np.stack([librosa.effects.pitch_shift(c, sr=sr, n_steps=pitch) for c in audio.T], axis=1)
    audio = np.clip(audio * 10 ** (gain / 20), -1, 1)
    sf.write(path, audio, sr, subtype='PCM_16')
    return len(audio) / sr


def run_job(job_id, payload):
    global ACTIVE
    started = time.monotonic()
    job = JOBS[job_id]
    try:
        job['status'] = 'running'
        job['message'] = 'Đang tải model hoặc tạo âm thanh… Lần đầu có thể mất vài phút.'
        call_worker(payload['engine'], payload)
        duration = postprocess(payload['output'], payload['pitch'], payload['gain'])
        job.update(status='done', duration=round(duration, 2), elapsed=round(time.monotonic() - started, 2),
                   message='Đã tạo âm thanh', url=f'/api/audio/{job_id}')
    except Exception as error:
        job.update(status='error', message=str(error)[:1000])
    finally:
        if payload.get('sample'):
            Path(payload['sample']).unlink(missing_ok=True)
        with LOCK:
            ACTIVE = None


def number(form, name, low, high, default):
    try:
        value = float(form.get(name, default))
    except (TypeError, ValueError):
        raise HTTPException(400, f'{name} không hợp lệ')
    if not math.isfinite(value) or not low <= value <= high:
        raise HTTPException(400, f'{name} nằm ngoài giới hạn')
    return value


app = FastAPI()


@app.middleware('http')
async def protect_local_api(request: Request, call_next):
    # No cross-site form submissions to this local service.
    if request.method == 'POST' and request.headers.get('sec-fetch-site') == 'cross-site':
        from fastapi.responses import JSONResponse
        return JSONResponse({'detail': 'Yêu cầu khác nguồn bị từ chối'}, status_code=403)
    return await call_next(request)


@app.get('/api/status')
def status():
    items = {}
    for key, spec in ENGINES.items():
        installed = engine_python(key).is_file()
        ready = installed
        if key == 'piper':
            ready = installed and Path(os.environ.get('PIPER_MODEL', '/nonexistent')).is_file()
        items[key] = dict(spec, installed=installed, configured=ready)
    return {'engines': items, 'languages': LANGUAGES, 'active': ACTIVE,
            'loaded_engine': WORKER_ENGINE if WORKER and WORKER.poll() is None else None,
            'piper_language': os.environ.get('PIPER_LANGUAGE', 'en'), 'piper_speakers': piper_speakers()}


@app.post('/api/generate', status_code=202)
async def create_job(request: Request):
    try:
        size = int(request.headers.get('content-length', '0'))
    except ValueError:
        raise HTTPException(400, 'Content-Length không hợp lệ')
    if size > 22 * 1024 * 1024:
        raise HTTPException(413, 'Dữ liệu tối đa 22 MB')
    async with request.form(max_files=1, max_fields=20, max_part_size=21 * 1024 * 1024) as form:
        return await prepare_job(form)


async def prepare_job(form):
    global ACTIVE
    engine = str(form.get('engine', ''))
    if engine not in ENGINES:
        raise HTTPException(400, 'Engine không hợp lệ')
    if not engine_python(engine).is_file():
        raise HTTPException(409, f'Chưa cài {engine}. Chạy: python install_engine.py {engine}')
    text = str(form.get('text', '')).strip()
    if not 1 <= len(text) <= 2000:
        raise HTTPException(400, 'Văn bản cần từ 1 đến 2000 ký tự')
    language = str(form.get('language', 'vi'))
    if language not in ENGINES[engine]['languages']:
        raise HTTPException(400, 'Engine không hỗ trợ ngôn ngữ này')
    if engine == 'piper':
        if language != os.environ.get('PIPER_LANGUAGE', 'en'):
            raise HTTPException(400, 'Ngôn ngữ phải khớp với giọng Piper đã cấu hình')
        if not Path(os.environ.get('PIPER_MODEL', '/nonexistent')).is_file():
            raise HTTPException(409, 'Chưa cấu hình PIPER_MODEL. Xem README.')
    speed = number(form, 'speed', .7, 1.4, 1)
    pitch = number(form, 'pitch', -3, 3, 0)
    gain = number(form, 'gain', -12, 6, 0)
    emotion = number(form, 'emotion', 0, 1, .5)
    speaker = str(form.get('speaker', '0'))
    if engine == 'piper' and speaker not in piper_speakers():
        raise HTTPException(400, 'Giọng Piper không hợp lệ')
    steps = number(form, 'steps', 16, 32, 16)
    if steps not in (16, 32):
        raise HTTPException(400, 'Số bước phải là 16 hoặc 32')
    if engine == 'chatterbox' and speed != 1:
        raise HTTPException(400, 'Chatterbox dùng tốc độ mặc định 1× trong bản này')
    if pitch:
        import importlib.util
        if importlib.util.find_spec('librosa') is None:
            raise HTTPException(409, 'Đổi cao độ cần cài thêm: pip install librosa==0.11.0')
    consent = form.get('consent') == 'true'
    license_consent = form.get('license_consent') == 'true'
    if engine == 'coqui' and not license_consent:
        raise HTTPException(400, 'Cần đồng ý giấy phép XTTS cho mục đích phi thương mại')
    transcript = str(form.get('transcript', '')).strip()
    if engine == 'omnivoice' and not 1 <= len(transcript) <= 1000:
        raise HTTPException(400, 'Nhập đúng lời trong mẫu (tối đa 1000 ký tự)')
    job_id = uuid.uuid4().hex
    sample_path = None
    sample_hash = None
    try:
        if ENGINES[engine]['clone']:
            if not consent:
                raise HTTPException(400, 'Cần xác nhận quyền sử dụng giọng')
            upload = form.get('sample')
            if not hasattr(upload, 'read'):
                raise HTTPException(400, 'Thiếu mẫu giọng')
            if Path(upload.filename or '').suffix.lower() not in ('.mp3', '.wav', '.flac'):
                raise HTTPException(400, 'Bản này nhận mẫu MP3, WAV hoặc FLAC')
            content = await upload.read(20 * 1024 * 1024 + 1)
            await upload.close()
            if len(content) > 20 * 1024 * 1024:
                raise HTTPException(413, 'Mẫu vượt quá 20 MB')
            sample_path = DATA / f'{job_id}.sample.wav'
            sample_path.write_bytes(content)
            try:
                info = sf.info(sample_path)
            except (RuntimeError, sf.LibsndfileError):
                raise HTTPException(400, 'File mẫu không phải âm thanh hợp lệ')
            minimum, maximum = (3, 10.1) if engine == 'omnivoice' else (3, 30)
            if not minimum <= info.duration <= maximum:
                raise HTTPException(400, f'Mẫu cần dài {minimum}–{int(maximum)} giây')
            if info.channels > 2 or info.samplerate > 192000:
                raise HTTPException(400, 'Mẫu tối đa 2 kênh, sample rate tối đa 192 kHz')
            # Decode and rewrite, so extension and actual format agree for every engine.
            audio, sr = sf.read(sample_path, dtype='float32', always_2d=True)
            if not np.isfinite(audio).all() or not np.any(audio):
                raise HTTPException(400, 'Mẫu không hợp lệ hoặc chỉ có im lặng')
            sf.write(sample_path, audio.mean(axis=1), sr, subtype='PCM_16')
            sample_hash = hashlib.sha256(sample_path.read_bytes()).hexdigest()
        payload = dict(engine=engine, text=text, language=language, transcript=transcript,
                       sample=str(sample_path) if sample_path else None, sample_hash=sample_hash,
                       output=str(DATA / f'{job_id}.wav'), speed=speed, steps=int(steps), pitch=pitch,
                       gain=gain, emotion=emotion, speaker=int(speaker) if engine == 'piper' else 0,
                       license_consent=license_consent)
        with LOCK:
            if ACTIVE:
                raise HTTPException(409, 'Đang có tác vụ. Chờ tác vụ hiện tại hoàn tất.')
            ACTIVE = job_id
            # Bound the session's in-memory history and retained output files.
            for old in list(JOBS)[:-49]:
                JOBS.pop(old)
                (DATA / f'{old}.wav').unlink(missing_ok=True)
            JOBS[job_id] = dict(id=job_id, engine=engine, text=text[:120], status='queued', message='Đang chuẩn bị')
        POOL.submit(run_job, job_id, payload)
        return {'id': job_id}
    except Exception:
        if sample_path:
            sample_path.unlink(missing_ok=True)
        raise


@app.get('/api/jobs')
def history():
    return list(JOBS.values())[::-1]


@app.get('/api/jobs/{job_id}')
def job_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(404, 'Không tìm thấy tác vụ')
    return JOBS[job_id]


@app.get('/api/audio/{job_id}')
def audio_file(job_id: str):
    job = JOBS.get(job_id)
    if not job or job['status'] != 'done':
        raise HTTPException(404, 'Chưa có âm thanh')
    return FileResponse(DATA / f'{job_id}.wav', media_type='audio/wav', filename=f'voice-{job_id[:8]}.wav')


@app.post('/api/unload')
def unload():
    with LOCK:
        if ACTIVE:
            raise HTTPException(409, 'Chờ tác vụ hoàn tất trước khi giải phóng GPU')
        stop_worker()
    return {'ok': True}


app.mount('/', StaticFiles(directory=ROOT / 'static', html=True), name='ui')

if __name__ == '__main__':
    import uvicorn
    try:
        uvicorn.run(app, host=os.environ.get('VOICE_HOST', '127.0.0.1'), port=8000)
    finally:
        stop_worker()
