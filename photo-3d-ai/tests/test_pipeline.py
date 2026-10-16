"""Pipeline integration with mocked AI; does not establish real inference quality."""
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from PIL import Image
import torch
import trimesh
import app
from tsr.models.isosurface import MarchingCubeHelper

class PipelineTests(unittest.TestCase):
    def test_marching_cubes_axis_order_and_closed_surface(self):
        helper = MarchingCubeHelper(32)
        points = helper.grid_vertices
        center = torch.tensor([.3, .5, .7])
        # TripoSR passes -(density-threshold); inside sphere must be negative.
        level = torch.linalg.vector_norm(points-center, dim=1) - .15
        vertices, faces = helper(level)
        np.testing.assert_allclose(vertices.mean(0).numpy(), center.numpy(), atol=.015)
        mesh = trimesh.Trimesh(vertices.numpy(), faces.numpy())
        self.assertTrue(mesh.is_watertight)
        self.assertTrue(np.isfinite(mesh.vertices).all())

    def test_transparent_image_preprocessing_and_export_roundtrip(self):
        class FakeModel:
            renderer = type('Renderer', (), {'set_chunk_size': lambda self, size: None})()
            def __call__(self, images, device):
                self.image = images[0]
                return torch.zeros((1, 1))
            def extract_mesh(self, codes, has_vertex_color, resolution):
                mesh = trimesh.creation.icosphere(subdivisions=1)
                mesh.visual.vertex_colors = np.tile([128, 220, 70, 255], (len(mesh.vertices), 1))
                return [mesh]
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            image = Image.new('RGBA', (128, 128))
            for x in range(32, 96):
                for y in range(32, 96): image.putpixel((x, y), (255, 0, 0, 255))
            path = folder / 'input.png'; image.save(path)
            with patch.object(app, 'OUTPUTS', folder), patch.object(app, 'MODEL', FakeModel()), patch.object(app, 'DEVICE', 'cpu'):
                result = app.generate(str(path), 'Tiết kiệm RAM / VRAM', 'CPU', False, lambda *a, **k: None)
                self.assertEqual(result[0], result[1])
                for filename in result[1:4]:
                    loaded = trimesh.load(filename, force='mesh')
                    self.assertGreater(len(loaded.vertices), 0)
                    self.assertGreater(len(loaded.faces), 0)
                self.assertIn('cpu', result[4])

    def test_missing_input_is_rejected(self):
        with self.assertRaises(app.gr.Error):
            app.generate(None, 'Tiết kiệm RAM / VRAM', 'CPU', False)

if __name__ == '__main__': unittest.main()
