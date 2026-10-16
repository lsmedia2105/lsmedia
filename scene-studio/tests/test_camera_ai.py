import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import camera_ai

SHOT={'name':'Cận mặt','subjectId':'rabbit','framing':'close','lens':85,'azimuth':-30,'elevation':0}
class CameraAITests(unittest.TestCase):
    def test_valid_camera_plan(self):
        result=camera_ai.validate([SHOT],{'rabbit'})
        self.assertEqual(result[0]['lens'],85)
    def test_unknown_subject_and_invalid_numbers_rejected(self):
        for changed in [{'subjectId':'missing'},{'lens':float('nan')},{'lens':999},{'elevation':91},{'framing':'execute_code'}]:
            with self.assertRaises(ValueError):camera_ai.validate([{**SHOT,**changed}],{'rabbit'})
    def test_ollama_request_and_structured_reply(self):
        class Response:
            def __enter__(self):return io.BytesIO(json.dumps({'message':{'content':json.dumps({'shots':[SHOT]})}}).encode())
            def __exit__(self,*args):pass
        with patch.object(camera_ai.urllib.request,'build_opener') as factory:
            factory.return_value.open.return_value=Response()
            result=camera_ai.plan('cận mặt thỏ 85mm',[{'id':'rabbit','name':'Thỏ cảnh sát'}])
            req=factory.return_value.open.call_args.args[0]
            self.assertEqual(req.full_url,'http://127.0.0.1:11434/api/chat')
            self.assertEqual(result[0]['subjectId'],'rabbit')
    def test_ollama_unavailable_has_actionable_message(self):
        with patch.object(camera_ai.urllib.request,'build_opener') as factory:
            factory.return_value.open.side_effect=camera_ai.urllib.error.URLError('offline')
            with self.assertRaisesRegex(RuntimeError,'offline'):camera_ai.plan('cận mặt',[{'id':'rabbit','name':'Thỏ'}])

if __name__=='__main__':unittest.main()
