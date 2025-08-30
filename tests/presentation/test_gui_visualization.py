import sys
import os
import pytest
import pyvista as pv
from PyQt6.QtWidgets import QApplication
from src.gui.widgets.scene_viewer_3d import SceneViewer3D
from src.core.domain.file_loader import load_file

def test_load_glb_and_gltf(tmp_path):
    # Crée un mesh simple et l'enregistre en .glb et .gltf
    mesh = pv.Sphere()
    glb_path = tmp_path / "test.glb"
    gltf_path = tmp_path / "test.gltf"
    mesh.save(str(glb_path))
    mesh.save(str(gltf_path))

    glb_mesh = load_file(str(glb_path))
    gltf_mesh = load_file(str(gltf_path))
    assert glb_mesh.n_points > 0
    assert gltf_mesh.n_points > 0

    # Test affichage dans le widget PyQt6
    app = QApplication.instance() or QApplication([])
    viewer = SceneViewer3D()
    viewer.set_mesh(glb_mesh)
    viewer.set_mesh(gltf_mesh)
    # Vérifie que le widget accepte le mesh
    assert viewer.mesh is not None

if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])
