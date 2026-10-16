"""Reproducible source/resource bundle; intentionally excludes virtualenvs and AI weights."""
from pathlib import Path
import hashlib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'V4'
DEST = ROOT / 'releases' / f'LS-Pixel-Studio-{VERSION}-Full.zip'
TOP = f'LS-Pixel-Studio-{VERSION}'
FILES = ['START-STUDIO.bat', 'START-FULL-V4.bat', 'START-EDITOR-ONLY.bat',
         'INSTALL-FULL-V4.bat', 'portable-launch.ps1', 'START-3D-AI.bat',
         'SETUP-VISION-V2.bat', 'PROMPT-DUNG-CANH-V2.txt', 'README.md']
BLOCKED = {'.venv', '.venv-photo3d', '.runtime', '.cache', '.data', 'outputs', '__pycache__'}
paths = [ROOT / p for p in FILES]
for name in ['scene-studio', 'photo-3d-ai']:
    paths.extend(p for p in (ROOT / name).rglob('*') if p.is_file()
                 and not any(part in BLOCKED or part.startswith('.venv-old-') for part in p.relative_to(ROOT).parts)
                 and p.suffix not in {'.zip', '.pyc', '.log'})
paths.append(Path(__file__).resolve())
intro = '''LS PIXEL STUDIO V4 - BAT DAU

1. Giai nen toan bo, khong chay ben trong ZIP.
2. Chay START-STUDIO.bat. Lan dau can Internet va nhieu GB tai xuong.
3. Neu chi can editor: START-EDITOR-ONLY.bat.
4. Trong kho trai: Series -> Tap -> Shot. Luu tap, Tai series de sao luu/chuyen may.
5. Chon vat the -> Luu nhan vat/vat the thanh preset o bang phai.
6. Huong dan day du: scene-studio/README-V4.md.

RX 580 Windows: GPU cho WebGL, CPU cho TripoSR. NVIDIA tu thu CUDA neu tuong thich.
Gói nay khong kem san Python, CUDA wheel hoac AI weights de chay offline lan dau.
Chua kiem thu installer tren Windows/GPU that; xem pham vi kiem thu trong huong dan.
'''
DEST.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(DEST, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
    for path in sorted(set(paths)):
        data=path.read_bytes()
        if path.suffix in {'.bat', '.ps1'}:
            data=data.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
        info=zipfile.ZipInfo(TOP+'/'+path.relative_to(ROOT).as_posix(),date_time=(2026,10,17,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        archive.writestr(info,data)
    info=zipfile.ZipInfo(TOP+'/BAT-DAU-V4.txt',date_time=(2026,10,17,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    archive.writestr(info,intro.encode('utf-8-sig'))
with zipfile.ZipFile(DEST) as archive:
    assert archive.testzip() is None
    names=archive.namelist()
    for required in FILES+['scene-studio/series.js','scene-studio/notes.js','photo-3d-ai/hardware.py',
                           'scene-studio/assets/rabbit-officer-v1/Rabbit-Officer-V1.glb',
                           'scene-studio/assets/outpost7-v1/Outpost7-V1.ls3d']:
        assert TOP+'/'+required in names,required
    assert not any(any(part in BLOCKED for part in Path(name).parts) for name in names)
digest=hashlib.sha256(DEST.read_bytes()).hexdigest()
DEST.with_suffix('.sha256').write_text(digest+'  '+DEST.name+'\n',encoding='ascii')
print(f'{DEST.name}: {len(names)} files, {DEST.stat().st_size:,} bytes, SHA256 {digest}')
