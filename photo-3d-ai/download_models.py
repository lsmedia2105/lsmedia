"""Prefetch the actual model files; successful downloads are cached between machines."""
import os
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parent
os.environ.setdefault('HF_HOME', str(ROOT / '.cache' / 'huggingface'))
os.environ.setdefault('U2NET_HOME', str(ROOT / '.cache' / 'rembg'))
from huggingface_hub import hf_hub_download, snapshot_download
import rembg

MODELS = [
    ('stabilityai/TripoSR', ['config.yaml', 'model.ckpt']),
    ('facebook/dino-vitb16', ['config.json']),
    ('LiheYoung/depth-anything-small-hf', ['config.json', 'preprocessor_config.json', '*.safetensors']),
    ('facebook/mask2former-swin-small-coco-instance', ['config.json', 'preprocessor_config.json', '*.safetensors', 'pytorch_model.bin']),
]

def main():
    stamp = ROOT / '.cache' / 'models-v4.json'
    if stamp.is_file():
        try:
            files = json.loads(stamp.read_text(encoding='utf-8'))
            if files and all((ROOT / '.cache' / p).is_file() for p in files):
                print('Model AI da du; dung lai cache.', flush=True)
                return
        except (ValueError, OSError):
            pass
    for repo, patterns in MODELS:
        print('Dang tai model:', repo, flush=True)
        snapshot_download(repo, allow_patterns=patterns)
    print('Tai model tach nen u2netp...', flush=True)
    rembg.new_session('u2netp', providers=['CPUExecutionProvider'])
    files = [str(p.relative_to(ROOT / '.cache')) for p in (ROOT / '.cache').rglob('*')
             if p.is_file() and p.name != stamp.name and '.locks' not in p.parts]
    stamp.write_text(json.dumps(files), encoding='utf-8')
    print('Da tai cac model 3D. Ollama duoc chuan bi rieng boi launcher.', flush=True)

if __name__ == '__main__':
    main()
