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
quality = sys.argv[2]
if quality == 'auto':
    from hardware import recommended_profile
    quality = recommended_profile(app.DEVICE_REPORT)
profile = 'Tiết kiệm RAM / VRAM' if quality == 'low' else 'Cân bằng'
# Auto uses only CUDA devices that passed the operation test; AMD Windows remains CPU.
if len(sys.argv)>3 and sys.argv[3]=='scene':
    from scene_ai import reconstruct
    reconstruct(folder,quality,app)
else:
    result = app.generate(str(folder/'input.png'), profile, 'Tự động', True, lambda *a, **k: None)
    shutil.copyfile(result[1],folder/'model.glb')
    print(result[4], flush=True)
