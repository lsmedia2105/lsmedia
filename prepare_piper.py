"""Prepare the small official Vietnamese Piper model (noncommercial dataset)."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
if __name__ == '__main__':
    subprocess.check_call([sys.executable, str(ROOT / 'install_engine.py'), 'piper'])
    python = ROOT / '.engines/piper' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    directory = ROOT / '.data/models'
    directory.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([str(python), '-m', 'piper.download_voices', 'vi_VN-vivos-x_low'], cwd=directory)
    print('Sẵn sàng: restart server, chọn Piper và Tiếng Việt. Model VIVOS dùng dữ liệu CC BY-NC-SA 4.0.')
