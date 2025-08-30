# src/gui/windows/visualization_2d_window.py
"""
Fenêtre de visualisation 2D pour les résultats de simulation RF.
Affiche les points de couverture sur un plan sélectionnable.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QToolBar, QComboBox, QSlider, QLabel, 
    QDoubleSpinBox, QApplication, QMessageBox
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, pyqtSignal
import pyvista as pv
from pyvistaqt import QtInteractor
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Visualization2DWindow(QMainWindow):
    """Fenêtre de visualisation 2D pour les résultats de simulation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Visualisation 2D - RF Simulator")
        self.setGeometry(200, 200, 800, 600)
        
        # Données de simulation
        self.simulation_points = None  # np.array de points 3D
        self.simulation_values = None  # np.array de valeurs (puissance dBm)
        
        # Plan de visualisation actuel
        self.current_plane = "XY (Horizontal)"
        
        # Position sur l'axe perpendiculaire
        self.orthogonal_position = 0.0
        
        self.init_ui()
        logger.info("Visualization2DWindow: Fenêtre 2D créée")

    def init_ui(self):
        """Initialise l'interface utilisateur de la fenêtre 2D."""
        # Barre d'outils
        self.create_toolbar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Plotter PyVista pour la visualisation 2D
        self.plotter = QtInteractor(self)
        self.plotter.enable_parallel_projection()
        self.plotter.add_axes()
        self.plotter.show_grid()
        layout.addWidget(self.plotter)
        
        self.setLayout(layout)
        logger.info("Visualization2DWindow: Interface utilisateur 2D initialisée")

    def create_toolbar(self):
        """Crée la barre d'outils pour les contrôles 2D."""
        toolbar = QToolBar("Outils 2D")
        self.addToolBar(toolbar)

        # Sélection du plan
        toolbar.addWidget(QLabel("Plan: "))
        self.plan_combo = QComboBox()
        self.plan_combo.addItems([
            "XY (Horizontal)",
            "XZ (Vertical frontal)",
            "YZ (Vertical latéral droit)"
        ])
        self.plan_combo.setCurrentText("XY (Horizontal)")
        self.plan_combo.currentTextChanged.connect(self.change_plane)
        toolbar.addWidget(self.plan_combo)
        
        # Curseur de position orthogonale
        toolbar.addSeparator()
        toolbar.addWidget(QLabel("Position: "))
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.setRange(-50, 50)  # Valeurs par défaut
        self.position_slider.setValue(0)
        self.position_slider.valueChanged.connect(self.update_position_from_slider)
        toolbar.addWidget(self.position_slider)
        
        self.position_spin = QDoubleSpinBox()
        self.position_spin.setRange(-100, 100)
        self.position_spin.setValue(0.0)
        self.position_spin.setSingleStep(0.1)
        self.position_spin.valueChanged.connect(self.update_position_from_spin)
        toolbar.addWidget(self.position_spin)
        
        # Label d'axe
        self.axis_label = QLabel("Z:")
        toolbar.addWidget(self.axis_label)
        
        toolbar.addSeparator()
        
        # Bouton de fermeture
        close_action = QAction(QIcon.fromTheme("window-close"), "Fermer", self)
        close_action.triggered.connect(self.close)
        toolbar.addAction(close_action)
        
        logger.info("Visualization2DWindow: Barre d'outils 2D créée")

    def set_simulation_data(self, points, values):
        """
        Définit les données de simulation à afficher.
        Args:
            points (np.array): Tableau de points 3D (N x 3)
            values (np.array): Tableau de valeurs de puissance (N,)
        """
        try:
            logger.info(f"Visualization2DWindow: Réception de {len(points)} points de simulation")
            self.simulation_points = np.array(points)
            self.simulation_values = np.array(values)
            self.update_slider_bounds()
            self.display_points_on_current_plane()
        except Exception as e:
            logger.error(f"Visualization2DWindow: Erreur lors de la définition des données de simulation: {e}")
            QMessageBox.warning(self, "Erreur 2D", f"Impossible de charger les données: {e}")

    def update_slider_bounds(self):
        """Met à jour les bornes des sliders selon les données de simulation."""
        try:
            if self.simulation_points is not None and len(self.simulation_points) > 0:
                axis_index = self.get_orthogonal_axis_index()
                if axis_index is not None and axis_index < 3:
                    axis_values = self.simulation_points[:, axis_index]
                    min_val = np.min(axis_values)
                    max_val = np.max(axis_values)
                    self.position_slider.setRange(int(min_val * 10), int(max_val * 10))
                    self.position_spin.setRange(min_val, max_val)
                    center_val = (min_val + max_val) / 2
                    self.position_slider.setValue(int(center_val * 10))
                    self.position_spin.setValue(center_val)
                    logger.debug(f"Visualization2DWindow: Bornes mises à jour: [{min_val:.2f}, {max_val:.2f}]")
        except Exception as e:
            logger.error(f"Visualization2DWindow: Erreur lors de la mise à jour des bornes: {e}")

    def get_orthogonal_axis_index(self):
        """Retourne l'index de l'axe perpendiculaire au plan actuel."""
        axis_mapping = {
            "XY (Horizontal)": 2,  # Z
            "XZ (Vertical frontal)": 1,  # Y
            "YZ (Vertical latéral droit)": 0,  # X
        }
        return axis_mapping.get(self.current_plane, 2)  # Z par défaut

    def get_parallel_axes_indices(self):
        """Retourne les indices des deux axes parallèles au plan actuel."""
        axes_mapping = {
            "XY (Horizontal)": (0, 1),  # X, Y
            "XZ (Vertical frontal)": (0, 2),  # X, Z
            "YZ (Vertical latéral droit)": (1, 2),  # Y, Z
        }
        return axes_mapping.get(self.current_plane, (0, 1))  # X, Y par défaut

    def change_plane(self, plane_name):
        """Change le plan de visualisation."""
        try:
            logger.info(f"Visualization2DWindow: Changement de plan vers {plane_name}")
            self.current_plane = plane_name
            axis_index = self.get_orthogonal_axis_index()
            axis_names = ['X', 'Y', 'Z']
            self.axis_label.setText(f"{axis_names[axis_index]}:")
            self.update_slider_bounds()
            self.display_points_on_current_plane()
        except Exception as e:
            logger.error(f"Visualization2DWindow: Erreur lors du changement de plan: {e}")

    def update_position_from_slider(self, value):
        """Met à jour la position orthogonale selon la valeur du slider."""
        try:
            position = float(value) / 10.0
            self.position_spin.setValue(position)
            self.orthogonal_position = position
            self.display_points_on_current_plane()
        except Exception as e:
            logger.error(f"Visualization2DWindow: Erreur slider: {e}")

    def update_position_from_spin(self, value):
        """Met à jour la position orthogonale selon la valeur du spinbox."""
        try:
            self.position_slider.setValue(int(value * 10))
            self.orthogonal_position = value
            self.display_points_on_current_plane()
        except Exception as e:
            logger.error(f"Visualization2DWindow: Erreur spinbox: {e}")

    def display_points_on_current_plane(self):
        """Affiche les points de simulation sur le plan 2D actuel."""
        try:
            if self.simulation_points is None or self.simulation_values is None:
                return
            if len(self.simulation_points) == 0 or len(self.simulation_values) == 0:
                return
            self.plotter.clear()
            orthogonal_axis = self.get_orthogonal_axis_index()
            parallel_axes = self.get_parallel_axes_indices()
            tolerance = 1.0
            axis_positions = self.simulation_points[:, orthogonal_axis]
            mask = np.abs(axis_positions - self.orthogonal_position) <= tolerance
            if np.sum(mask) == 0:
                logger.debug("Visualization2DWindow: Aucun point proche du plan sélectionné")
                self.plotter.add_text("Aucun point proche du plan sélectionné", 
                                    position='upper_left', 
                                    font_size=12, 
                                    color='red')
                self.plotter.render()
                return
            filtered_points = self.simulation_points[mask]
            filtered_values = self.simulation_values[mask]
            x_coords = filtered_points[:, parallel_axes[0]]
            y_coords = filtered_points[:, parallel_axes[1]]
            points_2d = np.column_stack([x_coords, y_coords, np.zeros_like(x_coords)])
            point_cloud = pv.PolyData(points_2d)
            point_cloud['signal_strength'] = filtered_values
            self.plotter.add_mesh(
                point_cloud,
                scalars='signal_strength',
                cmap='viridis',
                render_points_as_spheres=True,
                point_size=8,
                scalar_bar_args={
                    'title': 'Puissance (dBm)',
                    'vertical': True,
                    'position_x': 0.85,
                    'position_y': 0.1
                }
            )
            self.plotter.add_text(f"Plan: {self.current_plane}, Position: {self.orthogonal_position:.1f}m\n"
                                f"Points affichés: {len(filtered_points)}", 
                                position='upper_left', 
                                font_size=10, 
                                color='white')
            self.plotter.reset_camera()
            self.plotter.render()
            logger.debug(f"Visualization2DWindow: {len(filtered_points)} points affichés sur le plan {self.current_plane}")
        except Exception as e:
            logger.error(f"Visualization2DWindow: Erreur affichage points: {e}")
            self.plotter.add_text(f"Erreur d'affichage: {e}", 
                                position='upper_left', 
                                font_size=12, 
                                color='red')
            self.plotter.render()

    def closeEvent(self, event):
        """Gère la fermeture de la fenêtre."""
        try:
            if self.plotter:
                self.plotter.close()
        except Exception as e:
            logger.error(f"Visualization2DWindow: Erreur fermeture: {e}")
        finally:
            event.accept()
        logger.info("Visualization2DWindow: Fenêtre 2D fermée")
