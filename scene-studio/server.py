"""Local studio server. No third-party dependencies required for the editor."""
import base64
import binascii
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import threading
import uuid
import webbrowser

ROOT = Path(__file__).resolve().parent
DATA = ROOT / '.data'
DATA.mkdir(exist_ok=True)
JOBS = {}
LOCK = threading.Lock()
ENGINE = ROOT.parent / 'photo-3d-ai'

def engine_python():
    name = 'Scripts/python.exe' if sys.platform == 'win32' else 'bin/python'
    for folder in [ENGINE / '.venv', ROOT.parent / '.venv-photo3d']:
        candidate = folder / name
        if candidate.is_file(): return candidate
    return None

def run_job(job_id, folder, profile, kind="character"):
    job = JOBS[job_id]
    try:
        job.update(status='running', message='Đang tải model / dựng 3D. CPU có thể mất nhiều phút. Xem cửa sổ chạy tool.')
        with (folder / 'engine.log').open('w', encoding='utf-8') as log:
            result = subprocess.run([str(engine_python()), str(ROOT / 'worker.py'), str(folder), profile, kind], cwd=ENGINE, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode != 0 or not (folder / 'model.glb').is_file():
            tail = (folder / 'engine.log').read_text(encoding='utf-8', errors='replace')[-1600:]
            raise RuntimeError(tail)
        message='Đã dựng model AI. Bấm vào sàn để đặt trong cảnh.'
        if kind=='scene':
            report=json.loads((folder/'report.json').read_text(encoding='utf-8'))
            message=f"Đã dựng cảnh: {report['objects']} vật thể riêng; {report['skipped']} vật bỏ qua; {len(report['warnings'])} vật lỗi. " + report['note']
        job.update(status='done', message=message, kind=kind, url=f'/models/{job_id}')
    except Exception as exc:
        job.update(status='error', message='AI chưa tạo được model. Kiểm tra mạng Hugging Face và RAM. ' + str(exc)[-1600:])

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def send_json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8'); self.send_header('Content-Length', str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if self.path == '/api/status':
            self.send_json(200, {'ai_installed': engine_python() is not None, 'device_note': 'RX 580 dùng CPU cho AI; trình xem 3D dùng WebGL.'}); return
        if self.path.startswith('/api/jobs/'):
            job = JOBS.get(self.path.removeprefix('/api/jobs/'))
            self.send_json(200 if job else 404, job or {'message':'Không tìm thấy tác vụ'}); return
        if self.path.startswith('/models/'):
            job_id = self.path.removeprefix('/models/')
            if len(job_id) != 32 or any(c not in '0123456789abcdef' for c in job_id): self.send_error(404); return
            path = DATA / job_id / 'model.glb'
            if not path.is_file(): self.send_error(404); return
            self.send_response(200); self.send_header('Content-Type','model/gltf-binary'); self.send_header('Content-Length',str(path.stat().st_size)); self.end_headers(); self.wfile.write(path.read_bytes()); return
        # Keep job inputs/logs and Python source off static routes.
        if self.path.split('?')[0] not in ['/', '/index.html', '/app.js', '/style.css'] and not (self.path.startswith('/vendor/') and '..' not in self.path and self.path.endswith('.js')):
            self.send_error(404); return
        super().do_GET()
    def do_POST(self):
        if self.path != '/api/generate': self.send_error(404); return
        if self.headers.get('Sec-Fetch-Site') == 'cross-site': self.send_error(403); return
        origin = self.headers.get('Origin')
        if origin and origin not in ['http://127.0.0.1:8090','http://localhost:8090']: self.send_error(403); return
        if self.headers.get('Content-Type','').split(';')[0] != 'application/json': self.send_error(415); return
        if not engine_python(): self.send_json(409, {'message':'Chạy photo-3d-ai/INSTALL-WINDOWS.bat để cài AI trước. Studio vẫn dùng được khi chưa cài AI.'}); return
        try:
            length = int(self.headers.get('Content-Length','0'))
            if not 0 < length <= 22*1024*1024: raise ValueError('Ảnh tối đa 15 MB')
            body = json.loads(self.rfile.read(length))
            profile = body.get('profile','low')
            kind = body.get('kind','character')
            if kind not in ['character','scene']: raise ValueError('Loại ảnh không hợp lệ')
            if profile not in ['low','medium']: raise ValueError('Cấu hình không hợp lệ')
            raw = base64.b64decode(body['image'].split(',',1)[-1], validate=True)
            if not raw or len(raw)>15*1024*1024: raise ValueError('Ảnh tối đa 15 MB')
            with LOCK:
                if any(j['status'] in ['queued','running'] for j in JOBS.values()):
                    self.send_json(409, {'message':'Đang có tác vụ AI. Chờ tác vụ hiện tại hoàn tất.'}); return
                job_id = uuid.uuid4().hex; folder = DATA / job_id; folder.mkdir()
                (folder / 'input.png').write_bytes(raw)
                JOBS[job_id] = {'status':'queued','message':'Đang chờ dựng model…'}
            threading.Thread(target=run_job,args=(job_id,folder,profile,kind),daemon=True).start()
            self.send_json(202, {'id':job_id})
        except (ValueError,KeyError,TypeError,binascii.Error) as exc: self.send_json(400, {'message':str(exc)})

if __name__ == '__main__':
    print('LS Scene Studio: http://127.0.0.1:8090', flush=True)
    server = ThreadingHTTPServer(('127.0.0.1',8090), Handler)
    webbrowser.open('http://127.0.0.1:8090')
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
