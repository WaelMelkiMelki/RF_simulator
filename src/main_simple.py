"""
Application principale RF Simulator 3D
Affiche une scène 3D et permet de positionner une antenne par saisie des coordonnées.
"""

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
import sys
from src.core.infrastructure.file_loader import FileLoader
from src.gui.widgets.scene_viewer_3d_widget import SceneViewer3DWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RF Simulator 3D - Démo Simple")
        self.setGeometry(100, 100, 1200, 800)
        self.loader = FileLoader()
        self.scene_viewer = SceneViewer3DWidget(self)
        self.setCentralWidget(self.scene_viewer)
        self.init_ui()

    def init_ui(self):
        # Barre d'outils simple (sans saisie de coordonnées ni bouton antenne)
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        btn_import = QPushButton("Importer scène 3D")
        btn_import.clicked.connect(self.import_scene)
        toolbar_layout.addWidget(btn_import)
        # Ajout du toolbar au layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(toolbar)
        main_layout.addWidget(self.scene_viewer)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def import_scene(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Sélectionner une scène 3D", "", "Fichiers 3D (*.obj *.stl *.glb *.gltf)")
        if file_path:
            scene = self.loader.load_file(file_path)
            self.scene_viewer.update_scene(scene)
            QMessageBox.information(self, "Scène chargée", f"Scène chargée depuis : {file_path}")

    def place_antenna(self):
        try:
            x = float(self.x_input.text())
            y = float(self.y_input.text())
            z = float(self.z_input.text())
        except ValueError:
            QMessageBox.warning(self, "Erreur", "Veuillez saisir des coordonnées valides.")
            return
        # Ajout visuel simple d'une sphère pour représenter l'antenne
        if hasattr(self.scene_viewer, 'plotter_widget') and self.scene_viewer.plotter_widget:
            import pyvista as pv
            sphere = pv.Sphere(center=(x, y, z), radius=0.2)
            self.scene_viewer.plotter_widget.add_mesh(sphere, color='red')
            self.scene_viewer.plotter_widget.render()
            QMessageBox.information(self, "Antenne placée", f"Antenne placée en ({x}, {y}, {z})")
        else:
            QMessageBox.warning(self, "Erreur", "Le visualiseur 3D n'est pas prêt.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
