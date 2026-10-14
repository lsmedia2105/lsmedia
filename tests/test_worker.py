import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class AutoTranscriptWorkerTests(unittest.TestCase):
    def test_auto_asr_prompt_metadata_and_cache(self):
        # Fake model/CUDA; verify worker orchestration, not speech quality.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'torch.py').write_text('''
from contextlib import nullcontext
from types import SimpleNamespace
cuda = SimpleNamespace(is_available=lambda: True)
float16 = 'float16'
inference_mode = nullcontext
''')
            (root / 'omnivoice.py').write_text('''
import numpy as np
from types import SimpleNamespace
class OmniVoice:
    @classmethod
    def from_pretrained(cls, name, **kwargs):
        assert kwargs['asr_device'] == 'cpu'
        return cls()
    def create_voice_clone_prompt(self, ref_audio, ref_text):
        assert ref_text is None, 'Empty transcript must trigger automatic ASR'
        return SimpleNamespace(ref_text='Lời được AI nhận dạng.')
    def generate(self, **kwargs):
        assert kwargs['voice_clone_prompt'].ref_text == 'Lời được AI nhận dạng.'
        return [np.ones(24000, dtype=np.float32)*.1]
''')
            data = dict(sample='reference.wav', sample_hash='same-sample', transcript='',
                        text='Xin chào', language='vi', speed=1, steps=16,
                        output=str(root / 'output.wav'))
            result = subprocess.run([sys.executable, str(Path(__file__).resolve().parents[1] / 'worker.py'), 'omnivoice'],
                input=(json.dumps(data)+'\n')*2, text=True, capture_output=True,
                env={**os.environ, 'PYTHONPATH': str(root)}, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            events = [json.loads(line) for line in result.stdout.splitlines()]
            completed = [event for event in events if 'ok' in event]
            self.assertEqual(len(completed), 2)
            self.assertTrue(all(event['ok'] for event in completed), completed)
            self.assertEqual(completed[0]['transcript'], 'Lời được AI nhận dạng.')
            self.assertEqual(sum('chép lời' in event.get('message', '') for event in events), 1)


if __name__ == '__main__':
    unittest.main()
