"""Repeatable per-machine install. Copied virtualenvs are preserved, never reused blindly."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import venv
from hardware import inventory, choose_backend

ROOT = Path(__file__).resolve().parent
REPORT = ROOT.parent / '.runtime' / 'hardware.json'


def fingerprint():
    identity = platform.node()
    if sys.platform == 'win32':
        import winreg
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography') as key:
                identity = winreg.QueryValueEx(key, 'MachineGuid')[0]
        except OSError:
            pass
    data = '\n'.join([identity, str(ROOT), str(Path(sys.executable).resolve()), sys.version])
    return hashlib.sha256(data.encode()).hexdigest()


def run(python, *args):
    subprocess.check_call([str(python), *args], cwd=ROOT)


def inspect_torch(python):
    result = subprocess.run([str(python), '-X', 'utf8', str(ROOT / 'hardware.py')],
                            capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=90)
    if result.returncode:
        raise RuntimeError('PyTorch self-test failed: ' + result.stderr[-1000:])
    return json.loads(result.stdout.splitlines()[-1])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--download-models', action='store_true')
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 11) or platform.architecture()[0] != '64bit':
        raise SystemExit('Can Python 3.11 64-bit. Hay chay START-STUDIO.bat de tu chuan bi.')
    hardware = inventory()
    target = choose_backend(hardware['nvidia'])
    machine = fingerprint()
    folder = ROOT / '.venv'
    marker = folder / '.ls-install.json'
    try:
        previous = json.loads(marker.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        previous = {}
    if folder.exists() and previous.get('machine') != machine:
        backup = ROOT / ('.venv-old-' + time.strftime('%Y%m%d-%H%M%S') + '-' + str(os.getpid()))
        folder.rename(backup)
        print('Moi truong cu duoc giu tai:', backup.name, flush=True)
    python = folder / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    dependencies = hashlib.sha256((ROOT / 'requirements.txt').read_bytes()).hexdigest()
    installed = False
    # Reuse compatible wheels across driver updates; probe the actual GPU every launch.
    signature = {'requirements': dependencies, 'selection': target}
    if not python.is_file():
        venv.EnvBuilder(with_pip=True).create(folder)
    if previous.get('machine') != machine or previous.get('signature') != signature:
        run(python, '-m', 'pip', 'install', '--upgrade', 'pip')
        print('GPU:', ', '.join(hardware['displays']) or hardware['nvidia'] or 'CPU', flush=True)
        print('Cai PyTorch:', target, flush=True)
        try:
            run(python, '-m', 'pip', 'install', '--upgrade', '--force-reinstall',
                'torch==' + target['torch'], '--index-url', 'https://download.pytorch.org/whl/' + target['backend'])
        except subprocess.CalledProcessError:
            if target['backend'] == 'cpu':
                raise
            print('Chua cai duoc CUDA wheel; thu ban CPU. Lan mo sau se thu lai CUDA.', flush=True)
            signature = {**signature, 'selection': {'backend':'cpu','torch':'2.5.1'}}
            run(python, '-m', 'pip', 'install', '--force-reinstall', 'torch==2.5.1',
                '--index-url', 'https://download.pytorch.org/whl/cpu')
        run(python, '-m', 'pip', 'install', '-r', str(ROOT / 'requirements.txt'))
        run(python, '-m', 'pip', 'check')
        installed = True
    try:
        runtime = inspect_torch(python)
    except (RuntimeError, subprocess.TimeoutExpired, ValueError):
        # Repair a damaged runtime once, with the portable CPU build.
        run(python, '-m', 'pip', 'install', '--force-reinstall', 'torch==2.5.1',
            '--index-url', 'https://download.pytorch.org/whl/cpu')
        runtime = inspect_torch(python)
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps({**hardware, **runtime, 'checked_on': hashlib.sha256(platform.node().encode()).hexdigest()}, ensure_ascii=False, indent=2), encoding='utf-8')
    marker.write_text(json.dumps({'machine': machine, 'signature': signature,
                                 'runtime': runtime}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('TripoSR:', runtime['device'], runtime['name'], runtime['warning'], flush=True)
    print('Da cai/kiem tra xong.' if installed else 'Dung lai moi truong da cai; khong cai lai dependencies.', flush=True)
    if args.download_models:
        run(python, '-X', 'utf8', str(ROOT / 'download_models.py'))


if __name__ == '__main__':
    main()
