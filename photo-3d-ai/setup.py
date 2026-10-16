"""Install isolated dependencies without requiring a CUDA C++ compiler."""
from pathlib import Path
import shutil
import subprocess
import sys
import venv

root = Path(__file__).resolve().parent
if not (3, 10) <= sys.version_info[:2] <= (3, 12):
    raise SystemExit('Please install Python 3.10, 3.11 or 3.12 (64-bit). Python 3.11 recommended.')
folder = root / '.venv'
venv.EnvBuilder(with_pip=True).create(folder)
python = folder / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
subprocess.check_call([str(python), '-m', 'pip', 'install', '--upgrade', 'pip'])
# CUDA wheels include runtime libraries; only a compatible NVIDIA driver is needed.
index = 'https://download.pytorch.org/whl/cu121' if shutil.which('nvidia-smi') else 'https://download.pytorch.org/whl/cpu'
print('PyTorch source:', index, flush=True)
subprocess.check_call([str(python), '-m', 'pip', 'install', 'torch==2.5.1', '--index-url', index])
subprocess.check_call([str(python), '-m', 'pip', 'install', '-r', str(root / 'requirements.txt')])
subprocess.check_call([str(python), '-m', 'pip', 'check'])
print('Setup complete. Run START-WINDOWS.bat (Windows) or .venv/bin/python app.py (Linux).')
