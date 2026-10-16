"""Run real TripoSR using the existing isolated AI installation."""
from pathlib import Path
import shutil
import sys
# Windows redirected output otherwise commonly defaults to cp1252.
# Configure before importing models so their diagnostics use UTF-8 too.
for stream in (sys.stdout, sys.stderr):
    if hasattr(stream, 'reconfigure'):
        stream.reconfigure(encoding='utf-8', errors='backslashreplace')
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'photo-3d-ai'))
import app
folder = Path(sys.argv[1]).resolve()
profile = 'Tiết kiệm RAM / VRAM' if sys.argv[2] == 'low' else 'Cân bằng'
# CPU is intentional: Windows RX580 has no CUDA support. Do not silently use an unsupported AMD backend.
if len(sys.argv)>3 and sys.argv[3]=='scene':
    from scene_ai import reconstruct
    reconstruct(folder,sys.argv[2],app)
else:
    result = app.generate(str(folder/'input.png'), profile, 'CPU', True, lambda *a, **k: None)
    shutil.copyfile(result[1],folder/'model.glb')
    print(result[4], flush=True)
