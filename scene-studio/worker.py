"""Run real TripoSR using the existing isolated AI installation."""
from pathlib import Path
import shutil
import sys
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'photo-3d-ai'))
import app
folder = Path(sys.argv[1]).resolve()
profile = 'Tiết kiệm RAM / VRAM' if sys.argv[2] == 'low' else 'Cân bằng'
# CPU is intentional: Windows RX580 has no CUDA support. Do not silently use an unsupported AMD backend.
result = app.generate(str(folder/'input.png'), profile, 'CPU', True, lambda *a, **k: None)
shutil.copyfile(result[1],folder/'model.glb')
print(result[4], flush=True)
