import importlib.util
from pathlib import Path
import os
import unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('studio_hardware',Path(__file__).resolve().parents[1]/'hardware.py')
hardware=importlib.util.module_from_spec(spec);spec.loader.exec_module(hardware)

class HardwareTests(unittest.TestCase):
    def test_backend_driver_architecture_and_memory_gates(self):
        def gpu(cap=8.6,driver='551.23',memory_mb=8192):return {'capability':cap,'driver':driver,'memory_mb':memory_mb}
        with patch.dict(os.environ,{'LS_AI_DEVICE':'auto'}):
            self.assertEqual(hardware.choose_backend([])['backend'],'cpu')
            self.assertEqual(hardware.choose_backend([gpu()])['backend'],'cu121')
            self.assertEqual(hardware.choose_backend([gpu(12.0,'576.52')]),{'backend':'cu128','torch':'2.7.1'})
            for card in [gpu(12.0,'551.23'),gpu(3.5),gpu(memory_mb=2048),gpu(driver='470.20')]:
                self.assertEqual(hardware.choose_backend([card])['backend'],'cpu')
        with patch.dict(os.environ,{'LS_AI_DEVICE':'cpu'}):
            self.assertEqual(hardware.choose_backend([gpu()])['backend'],'cpu')

    def test_cuda_availability_alone_is_not_success(self):
        class Cuda:
            is_available=lambda self:True
            device_count=lambda self:1
            get_device_properties=lambda self,i:type('Properties',(),{'total_memory':8*1024**3,'name':'Mock GPU'})()
        class Torch:
            __version__='mock'
            cuda=Cuda()
            @staticmethod
            def ones(*a,**kw):raise RuntimeError('no kernel image is available')
        with patch.dict(os.environ,{'LS_AI_DEVICE':'auto'}):
            report=hardware.probe_torch(Torch)
            self.assertEqual(report['device'],'cpu')
            self.assertFalse(report['cuda_tested'])
            self.assertIn('no kernel image',report['warning'])

    def test_probe_success_and_auto_profile(self):
        class Tensor:
            __matmul__=lambda self,other:self
            sum=lambda self:self
            item=lambda self:512
        class Cuda:
            is_available=lambda self:True
            device_count=lambda self:1
            synchronize=lambda self,i:None
            get_device_properties=lambda self,i:type('Properties',(),{'total_memory':8*1024**3,'name':'Mock GPU'})()
        class Torch:
            __version__='mock'
            cuda=Cuda()
            ones=lambda *a,**kw:Tensor()
        with patch.dict(os.environ,{'LS_AI_DEVICE':'auto'}):
            report=hardware.probe_torch(Torch)
            self.assertEqual(report['device'],'cuda:0')
            self.assertTrue(report['cuda_tested'])
            self.assertEqual(hardware.recommended_profile(report),'medium')
            self.assertEqual(hardware.recommended_profile({'device':'cpu'}),'low')

if __name__=='__main__':unittest.main()
