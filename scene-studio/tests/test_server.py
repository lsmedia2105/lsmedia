import base64
from http.server import ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.request
import urllib.error

spec=importlib.util.spec_from_file_location('studio_server',Path(__file__).resolve().parents[1]/'server.py')
server=importlib.util.module_from_spec(spec);spec.loader.exec_module(server)

class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=ThreadingHTTPServer(('127.0.0.1',0),server.Handler)
        cls.base='http://127.0.0.1:'+str(cls.http.server_port)
        cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close();cls.thread.join()
    def setUp(self):server.JOBS.clear()
    def request(self,path,data=None,origin=None):
        headers={'Content-Type':'application/json'}
        if origin:headers['Origin']=origin
        req=urllib.request.Request(self.base+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
        try:
            with urllib.request.urlopen(req) as r:return r.status,r.read()
        except urllib.error.HTTPError as e:return e.code,e.read()
    def test_static_and_private_routes(self):
        self.assertEqual(self.request('/')[0],200)
        self.assertEqual(self.request('/api/status')[0],200)
        self.assertEqual(self.request('/worker.py')[0],404)
        self.assertEqual(self.request('/.data/')[0],404)
    def test_missing_engine_and_cross_origin_rejected(self):
        with patch.object(server,'engine_python',return_value=None):self.assertEqual(self.request('/api/generate',{'image':'x'})[0],409)
        self.assertEqual(self.request('/api/generate',{},'https://example.org')[0],403)
    def test_invalid_input_and_busy_queue(self):
        with patch.object(server,'engine_python',return_value=Path('/fake/python')):
            self.assertEqual(self.request('/api/generate',{'image':'!!!'})[0],400)
            self.assertEqual(self.request('/api/generate',{'image':'AA==','profile':'unknown'})[0],400)
            server.JOBS['existing']={'status':'running'}
            self.assertEqual(self.request('/api/generate',{'image':'AA=='})[0],409)
    def test_worker_success_and_failure_propagate(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp);server.JOBS['test']={'status':'queued'}
            def success(*args,**kwargs):
                (folder/'model.glb').write_bytes(b'glTF')
                return type('Result',(),{'returncode':0})()
            with patch.object(server,'engine_python',return_value=Path('/fake/python')),patch.object(server.subprocess,'run',side_effect=success):server.run_job('test',folder,'low')
            self.assertEqual(server.JOBS['test']['status'],'done')
            (folder/'model.glb').unlink()
            def failure(*args,**kwargs):
                (folder/'engine.log').write_text('Simulated model download failure')
                return type('Result',(),{'returncode':1})()
            with patch.object(server,'engine_python',return_value=Path('/fake/python')),patch.object(server.subprocess,'run',side_effect=failure):server.run_job('test',folder,'low')
            self.assertEqual(server.JOBS['test']['status'],'error')
            self.assertIn('Simulated model download failure',server.JOBS['test']['message'])

if __name__=='__main__':unittest.main()
