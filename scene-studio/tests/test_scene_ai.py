"""Scene assembly tests with mocked model predictions; not AI quality tests."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import numpy as np
from PIL import Image
import torch
import trimesh
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_ai import depth_mesh, reconstruct

class SceneTests(unittest.TestCase):
    def test_depth_projection_and_holes(self):
        depth=np.full((12,16),4,dtype=np.float32)
        rgb=np.full((12,16,3),128,dtype=np.uint8)
        full=depth_mesh(rgb,depth,np.zeros((12,16),bool))
        hole=np.zeros((12,16),bool);hole[4:8,5:10]=True
        cut=depth_mesh(rgb,depth,hole)
        self.assertLess(len(cut.faces),len(full.faces))
        self.assertTrue(np.isfinite(cut.vertices).all())
        np.testing.assert_allclose(cut.vertices[:,2],-4)
    def test_scene_instances_export_as_independent_nodes(self):
        import transformers
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);Image.new('RGB',(100,80),'white').save(folder/'input.png')
            labels=torch.full((80,100),-1);labels[15:60,30:60]=0
            class Processor:
                def __call__(self,**kw):return {}
                def post_process_instance_segmentation(self,*a,**kw):return [{'segmentation':labels,'segments_info':[{'id':0,'label_id':0}]}]
            class Segmenter:
                config=SimpleNamespace(id2label={0:'person'})
                def eval(self):return self
                def __call__(self,**kw):return None
            class Engine:
                @staticmethod
                def generate(*a,**k):
                    path=folder/'instance.glb';trimesh.creation.icosphere(subdivisions=1).export(path)
                    return str(path),str(path)
            with patch.object(transformers,'pipeline',return_value=lambda image:{'predicted_depth':torch.linspace(0,1,80*100).reshape(1,80,100)}),patch.object(transformers.AutoImageProcessor,'from_pretrained',return_value=Processor()),patch.object(transformers.Mask2FormerForUniversalSegmentation,'from_pretrained',return_value=Segmenter()):
                reconstruct(folder,'low',Engine)
            scene=trimesh.load(folder/'model.glb',force='scene')
            self.assertEqual(len(scene.geometry),2)
            self.assertTrue((folder/'report.json').exists())

if __name__=='__main__':unittest.main()
