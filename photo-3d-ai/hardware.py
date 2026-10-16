"""Read-only hardware inventory and a real CUDA operation probe; no AMD/CUDA claims."""
import csv
import io
import json
import os
import platform
import subprocess


def command(args, timeout=15):
    try:
        result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8',
                                errors='replace', timeout=timeout, check=True,
                                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ''


def inventory():
    rows = command(['nvidia-smi', '--query-gpu=index,name,memory.total,driver_version,compute_cap',
                    '--format=csv,noheader,nounits'])
    cards = []
    for row in csv.reader(io.StringIO(rows)):
        try:
            index, name, memory, driver, capability = [v.strip() for v in row]
            cards.append(dict(index=int(index), name=name, memory_mb=int(memory),
                              driver=driver, capability=float(capability)))
        except (ValueError, TypeError):
            continue
    displays = []
    if platform.system() == 'Windows':
        raw = command(['powershell.exe', '-NoProfile', '-Command',
                       '[Console]::OutputEncoding=[Text.UTF8Encoding]::new(); '
                       '@(Get-CimInstance Win32_VideoController | Select-Object -ExpandProperty Name) | ConvertTo-Json -Compress'])
        try:
            names = json.loads(raw)
            displays = [names] if isinstance(names, str) else names if isinstance(names, list) else []
        except ValueError:
            pass
    return {'system': platform.system(), 'displays': displays, 'nvidia': cards}


def choose_backend(cards):
    """Conservative pinned wheels; driver or architecture mismatch stays on CPU."""
    options = []
    for card in cards:
        try:
            driver = tuple(int(n) for n in card['driver'].split('.')[:2])
            cap = card['capability']
            if card['memory_mb'] < 4096:
                continue
            if 10 <= cap <= 12 and driver >= (570, 65):
                options.append((card['memory_mb'], 'cu128', '2.7.1'))
            elif 5 <= cap < 10 and driver >= (527, 41):
                options.append((card['memory_mb'], 'cu121', '2.5.1'))
        except (KeyError, TypeError, ValueError):
            continue
    if os.environ.get('LS_AI_DEVICE', '').lower() == 'cpu' or not options:
        return {'backend': 'cpu', 'torch': '2.5.1'}
    _, backend, version = max(options)
    return {'backend': backend, 'torch': version}


def probe_torch(torch_module=None):
    if torch_module is None:
        import torch as torch_module
    t = torch_module
    result = {'device': 'cpu', 'name': 'CPU', 'memory_mb': 0, 'cuda_tested': False,
              'torch': t.__version__, 'warning': ''}
    if os.environ.get('LS_AI_DEVICE', '').lower() == 'cpu':
        result['warning'] = 'Đã chọn CPU bằng LS_AI_DEVICE.'
        return result
    try:
        if not t.cuda.is_available():
            result['warning'] = 'CUDA không khả dụng. TripoSR dùng CPU; khung 3D vẫn dùng WebGL.'
            return result
        devices = sorted(range(t.cuda.device_count()), key=lambda i: t.cuda.get_device_properties(i).total_memory, reverse=True)
        failures = []
        for i in devices:
            try:
                properties = t.cuda.get_device_properties(i)
                if properties.total_memory < 4 * 1024**3:
                    continue
                # Availability alone misses unsupported kernels (e.g. a new GPU on old wheels).
                tensor = t.ones((8, 8), device=f'cuda:{i}')
                value = (tensor @ tensor).sum().item()
                t.cuda.synchronize(i)
                if value != 512:
                    raise RuntimeError('CUDA self-test failed')
                del tensor
                result.update(device=f'cuda:{i}', name=properties.name,
                              memory_mb=properties.total_memory // 1024**2, cuda_tested=True)
                return result
            except Exception as exc:
                failures.append(str(exc)[:160])
        result['warning'] = 'CUDA không vượt qua kiểm tra hoặc VRAM dưới 4 GB; dùng CPU. ' + '; '.join(failures)
    except Exception as exc:
        result['warning'] = 'Không kiểm tra được CUDA; dùng CPU: ' + str(exc)[:200]
    return result


def recommended_profile(report):
    return 'medium' if report.get('cuda_tested') and report.get('memory_mb', 0) >= 8192 else 'low'


if __name__ == '__main__':
    print(json.dumps(probe_torch(), ensure_ascii=True))
