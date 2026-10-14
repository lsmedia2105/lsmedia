"""Install an optional engine in its own virtual environment."""
import argparse
import importlib.util
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PACKAGES = {
    'omnivoice': ['torch==2.8.0', 'torchaudio==2.8.0', 'transformers==5.3.0', 'omnivoice==0.2.1'],
    'piper': ['piper-tts==1.8.0'],
    'coqui': ['torch==2.8.0', 'torchaudio==2.8.0', 'coqui-tts==0.27.5'],
    'chatterbox': ['chatterbox-tts==0.1.7'],
}


def create_environment(directory):
    # Colab's Debian Python can omit ensurepip/python-venv. virtualenv seeds pip
    # itself and supports that runtime without apt or administrator access.
    if importlib.util.find_spec('virtualenv') is None:
        print('Đang chuẩn bị bộ tạo môi trường cho Colab…', flush=True)
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'virtualenv==21.14.7'])
    subprocess.check_call([sys.executable, '-m', 'virtualenv', '--no-periodic-update', str(directory)])
    python = directory / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    subprocess.check_call([str(python), '-m', 'pip', '--version'])
    return python

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('engine', choices=PACKAGES)
    args = parser.parse_args()
    directory = ROOT / '.engines' / args.engine
    # Isolate torch/transformers versions between engines.
    print(f'Đang tạo môi trường riêng cho {args.engine} với Python {sys.version.split()[0]}…', flush=True)
    python = create_environment(directory)
    print(f'Đang cài {args.engine}; lần đầu có thể tải nhiều GB thư viện…', flush=True)
    subprocess.check_call([str(python), '-m', 'pip', 'install', *PACKAGES[args.engine], 'soundfile'])
    print(f'{args.engine}: đã cài. Model sẽ tải ở lần tạo đầu tiên.')
