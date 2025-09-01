# Test script pour la fonctionnalité d'exploration d'objets
import sys
import os
sys.path.append('src')

from PyQt6.QtWidgets import QApplication
from gui.dialogs.scene_objects_dialog import SceneObjectsDialog
from core.domain.scene import Scene3D

def test_scene_objects_dialog():
    app = QApplication([])
    
    # Créer une scène de test simple
    scene = Scene3D()
    
    # Simuler quelques objets
    scene.meshes = {
        "Building_A": "dummy_mesh_a",
        "Building_B": "dummy_mesh_b", 
        "Ground": "dummy_ground",
        "Tree_01": "dummy_tree"
    }
    
    # Créer et afficher le dialogue
    dialog = SceneObjectsDialog(scene)
    
    # Connecter quelques signaux pour le test
    dialog.object_selected.connect(lambda name: print(f"✅ Objet sélectionné: {name}"))
    dialog.object_highlighted.connect(lambda name, highlight: print(f"🔍 Objet {'surligné' if highlight else 'désurligné'}: {name}"))
    dialog.material_assigned.connect(lambda name, mat: print(f"🎨 Matériau assigné à {name}: {mat}"))
    
    dialog.show()
    app.exec()

if __name__ == "__main__":
    test_scene_objects_dialog()
