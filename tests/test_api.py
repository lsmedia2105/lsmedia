import io
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import patch

import numpy as np
import soundfile as sf
from fastapi.testclient import TestClient

import server


def wav(seconds=4, silent=False):
    out = io.BytesIO()
    sr = 24000
    x = np.zeros(int(sr * seconds)) if silent else .1 * np.sin(2 * np.pi * 220 * np.arange(int(sr * seconds)) / sr)
    sf.write(out, x, sr, format='WAV')
    return out.getvalue()


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.patches = [patch.object(server, 'DATA', Path(self.directory.name)),
                        patch.object(server, 'engine_python', return_value=Path(__file__))]
        for p in self.patches:
            p.start()
        server.JOBS.clear()
        server.ACTIVE = None
        self.client = TestClient(server.app)
        self.fields = dict(engine='omnivoice', text='Xin chào!', language='vi', transcript='Xin chào', consent='true')

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.directory.cleanup()

    def send(self, fields=None, sample=None):
        return self.client.post('/api/generate', data=fields or self.fields,
                                files={'sample': ('sample.wav', sample if sample is not None else wav(), 'audio/wav')})

    def wait(self, job):
        for _ in range(100):
            result = self.client.get('/api/jobs/' + job).json()
            if result['status'] in ('done', 'error') and server.ACTIVE is None:
                return result
            time.sleep(.01)
        self.fail('Job did not finish')

    def test_upload_job_download_and_cleanup(self):
        # Fake inference only; real multipart, job processing, postprocessing and WAV download.
        def inference(engine, payload):
            self.assertEqual(engine, 'omnivoice')
            self.assertTrue(Path(payload['sample']).exists())
            self.assertEqual(payload['transcript'], 'Xin chào')
            sf.write(payload['output'], .2*np.ones(24000), 24000)
        with patch.object(server, 'call_worker', side_effect=inference):
            response = self.send()
            self.assertEqual(response.status_code, 202, response.text)
            job = response.json()['id']
            result = self.wait(job)
        self.assertEqual(result['status'], 'done', result)
        audio = self.client.get(result['url'])
        self.assertEqual(audio.status_code, 200)
        self.assertEqual(audio.content[:4], b'RIFF')
        self.assertEqual(sf.info(io.BytesIO(audio.content)).duration, 1)
        self.assertFalse(list(Path(self.directory.name).glob('*.sample.wav')))
        self.assertEqual(len(self.client.get('/api/jobs').json()), 1)

    def test_model_failure_is_visible_and_releases_slot(self):
        with patch.object(server, 'call_worker', side_effect=RuntimeError('GPU unavailable')):
            job = self.send().json()['id']
            result = self.wait(job)
        self.assertEqual(result['status'], 'error')
        self.assertIn('GPU unavailable', result['message'])
        self.assertIsNone(server.ACTIVE)
        self.assertEqual(self.client.get('/api/audio/' + job).status_code, 404)

    def test_mp3_is_decoded_to_mono_wav_before_inference(self):
        sample = io.BytesIO()
        sf.write(sample, np.column_stack([.1*np.sin(np.arange(96000)/20)]*2), 24000, format='MP3')
        def inference(engine, payload):
            info = sf.info(payload['sample'])
            self.assertEqual(info.format, 'WAV')
            self.assertEqual(info.channels, 1)
            self.assertAlmostEqual(info.duration, 4, places=1)
            sf.write(payload['output'], np.ones(24000)*.1, 24000)
        with patch.object(server, 'call_worker', side_effect=inference):
            response = self.client.post('/api/generate', data=self.fields,
                files={'sample': ('voice.mp3', sample.getvalue(), 'audio/mpeg')})
            self.assertEqual(response.status_code, 202, response.text)
            self.assertEqual(self.wait(response.json()['id'])['status'], 'done')

    def test_invalid_and_overlong_mp3_rejected(self):
        long_sample = io.BytesIO()
        sf.write(long_sample, np.sin(np.arange(12*24000)/20)*.1, 24000, format='MP3')
        for content in (b'broken mp3', long_sample.getvalue()):
            response = self.client.post('/api/generate', data=self.fields,
                files={'sample': ('voice.mp3', content, 'audio/mpeg')})
            self.assertEqual(response.status_code, 400)

    def test_consent_required(self):
        self.assertEqual(self.send({**self.fields, 'consent': 'false'}).status_code, 400)

    def test_bad_audio_short_and_silent_rejected(self):
        for data in (b'not audio', wav(.5), wav(silent=True)):
            with self.subTest(size=len(data)):
                self.assertEqual(self.send(sample=data).status_code, 400)

    def test_unsupported_vietnamese_rejected(self):
        for engine in ('coqui', 'chatterbox'):
            self.assertEqual(self.send({**self.fields, 'engine': engine}).status_code, 400)

    def test_nonfinite_settings_rejected(self):
        self.assertEqual(self.send({**self.fields, 'speed': 'nan'}).status_code, 400)

    def test_busy_does_not_leave_uploaded_sample(self):
        server.ACTIVE = 'another-job'
        self.assertEqual(self.send().status_code, 409)
        self.assertFalse(list(Path(self.directory.name).glob('*.sample.wav')))
        server.ACTIVE = None

    def test_static_page_and_missing_job(self):
        self.assertIn('Voice Studio', self.client.get('/').text)
        self.assertEqual(self.client.get('/api/jobs/unknown').status_code, 404)

    def test_cross_site_submit_rejected(self):
        response = self.client.post('/api/generate', headers={'sec-fetch-site': 'cross-site'})
        self.assertEqual(response.status_code, 403)


if __name__ == '__main__':
    unittest.main()
