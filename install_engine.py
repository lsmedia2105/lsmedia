"""Install an optional engine in its own virtual environment."""
import argparse
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parent
PACKAGES = {
    'omnivoice': ['torch==2.8.0', 'torchaudio==2.8.0', 'transformers==5.3.0', 'omnivoice==0.2.1'],
    'piper': ['piper-tts==1.8.0'],
    'coqui': ['torch==2.8.0', 'torchaudio==2.8.0', 'coqui-tts==0.27.5'],
    'chatterbox': ['chatterbox-tts==0.1.7'],
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('engine', choices=PACKAGES)
    args = parser.parse_args()
    directory = ROOT / '.engines' / args.engine
    # Isolate torch/transformers versions between engines.
    venv.EnvBuilder(with_pip=True).create(directory)
    python = directory / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    subprocess.check_call([str(python), '-m', 'pip', 'install', *PACKAGES[args.engine], 'soundfile'])
    print(f'{args.engine}: đã cài. Model sẽ tải ở lần tạo đầu tiên.')
