"""CPU marching cubes adapter; avoids CUDA compiler/toolchain requirements.

The upstream torchmcubes returns xyz in reversed array-axis order. Here
scikit-image returns array-axis order directly, matching grid_vertices.
"""
from typing import Optional, Tuple
import numpy as np
import torch
import torch.nn as nn
from skimage.measure import marching_cubes

class IsosurfaceHelper(nn.Module):
    points_range: Tuple[float, float] = (0, 1)

class MarchingCubeHelper(IsosurfaceHelper):
    def __init__(self, resolution: int):
        super().__init__()
        self.resolution = resolution
        self._grid_vertices: Optional[torch.FloatTensor] = None

    @property
    def grid_vertices(self):
        if self._grid_vertices is None:
            axes = [torch.linspace(0, 1, self.resolution)] * 3
            self._grid_vertices = torch.stack(torch.meshgrid(*axes, indexing='ij'), dim=-1).reshape(-1, 3)
        return self._grid_vertices

    def forward(self, level):
        volume = -level.detach().float().cpu().numpy().reshape((self.resolution,) * 3)
        vertices, faces, _, _ = marching_cubes(volume, level=0.0)
        return (torch.from_numpy(vertices.copy()).to(level.device) / (self.resolution - 1),
                torch.from_numpy(faces.astype(np.int64).copy()).to(level.device))
