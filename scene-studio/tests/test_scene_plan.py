import copy
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scene_plan

SAMPLE=Path(__file__).resolve().parents[1]/'examples/mars-reference.json'
class PlanTests(unittest.TestCase):
    def test_sample_scene_has_separate_landmarks_and_character(self):
        plan=scene_plan.validate(json.loads(SAMPLE.read_text()))
        types={n['type'] for n in plan['objects']}
        self.assertTrue({'terrain','tower','dome','person','vehicle','planet'}.issubset(types))
        self.assertGreater(len(plan['objects']),10)
    def test_invalid_model_output_is_rejected(self):
        plan=json.loads(SAMPLE.read_text())
        for key,value in [('type','execute_python'),('size',[-1,2,3]),('position',[float('nan'),0,0]),('color','javascript:alert(1)')]:
            bad=copy.deepcopy(plan);bad['objects'][0][key]=value
            with self.assertRaises(ValueError):scene_plan.validate(bad)
    def test_photo_is_sent_only_to_local_vision_and_response_is_data(self):
        class Response:
            def __enter__(self):return io.BytesIO(json.dumps({'message':{'content':SAMPLE.read_text()}}).encode())
            def __exit__(self,*args):pass
        class Local:
            def open(self,request,timeout):
                self.request=request
                self.body=json.loads(request.data)
                return Response()
        local=Local()
        with tempfile.TemporaryDirectory() as d:
            photo=Path(d)/'image.png';photo.write_bytes(b'fake image: model inference mocked')
            with patch.object(scene_plan.urllib.request,'build_opener',return_value=local):result=scene_plan.from_image(photo,character=True)
        self.assertEqual(local.request.full_url,'http://127.0.0.1:11434/api/chat')
        self.assertTrue(local.body['messages'][0]['images'])
        self.assertIn('CHARACTER reference',local.body['messages'][0]['content'])
        self.assertEqual(len(result['objects']),18)
    def test_local_service_unavailable_gives_install_command(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'image.png';path.write_bytes(b'fake')
            with patch.object(scene_plan.urllib.request,'build_opener') as mock:
                mock.return_value.open.side_effect=scene_plan.urllib.error.URLError('offline')
                with self.assertRaisesRegex(RuntimeError,'ollama pull'):scene_plan.from_image(path)

if __name__=='__main__':unittest.main()
