"""Exercise the real worker entry point under Windows-like cp1252 output."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

WORKER = Path(__file__).resolve().parents[1] / 'worker.py'

class WindowsEncodingTests(unittest.TestCase):
    def test_worker_can_print_vietnamese_with_cp1252_inherited(self):
        # Only AI inference is mocked; the worker entry point, stdout setup,
        # copying the GLB and printing the completion text execute unchanged.
        with tempfile.TemporaryDirectory() as directory:
            runner = """
import pathlib, runpy, sys, types
folder=pathlib.Path(sys.argv[2])
source=folder/'generated.glb'
source.write_bytes(b'glTF')
def generate(*a,**k):
    assert a[1]=='Tiết kiệm RAM / VRAM' and a[2]=='Tự động'
    print('Đang dựng nhân vật — hoàn tất',flush=True)
    return str(source),str(source),None,None,'Đã tạo mô hình tiếng Việt'
sys.modules['app']=types.SimpleNamespace(generate=generate,DEVICE_REPORT={'device':'cpu','cuda_tested':False})
worker=sys.argv[1]
sys.argv=[worker,str(folder),'auto','character']
runpy.run_path(worker,run_name='__main__')
"""
            child_env=os.environ.copy()
            child_env.update(PYTHONIOENCODING='cp1252',PYTHONUTF8='0')
            result=subprocess.run([sys.executable,'-c',runner,str(WORKER),directory],env=child_env,capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr.decode('utf-8',errors='replace'))
            text=result.stdout.decode('utf-8')
            self.assertIn('Đã tạo mô hình tiếng Việt',text)
            self.assertEqual((Path(directory)/'model.glb').read_bytes(),b'glTF')

if __name__=='__main__':unittest.main()
