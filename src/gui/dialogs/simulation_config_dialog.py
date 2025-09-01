# src/gui/dialogs/simulation_config_dialog.py
"""
Dialogue pour configurer les paramètres de la simulation.
Permet à l'utilisateur de définir la résolution, les modèles de propagation,
et la densité visuelle des points de couverture.
"""

import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDoubleSpinBox, QSpinBox,
    QComboBox, QPushButton, QLabel, QDialogButtonBox, QGroupBox, QStackedWidget, QWidget
)
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)

class SimulationConfigDialog(QDialog):
    """
    Dialogue modale pour configurer les paramètres de la simulation RF.
    Permet de définir la résolution du maillage, les niveaux de hauteur,
    le modèle de propagation, et la densité visuelle des points de couverture.
    """

    def __init__(self, antenna_names, parent=None):
        """
        Initialise le dialogue de configuration.

        Args:
            antenna_names (list): Liste des noms d'antennes disponibles.
            parent (QWidget, optional): Widget parent. Defaults to None.
        """
        super().__init__(parent)
        self.setWindowTitle("Configuration de la Simulation")
        self.setModal(True)
        self.config_data = None
        self.antenna_names = antenna_names
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur du dialogue."""
        layout = QVBoxLayout(self)

        # --- GROUPE : Paramètres du Maillage ---
        mesh_group_box = QGroupBox("Paramètres du Maillage de Calcul")
        mesh_layout = QFormLayout(mesh_group_box)

        # Résolution (mètres) - Contrôle la distance entre les points de calcul
        self.resolution_spin = QDoubleSpinBox()
        self.resolution_spin.setRange(0.1, 10.0)
        self.resolution_spin.setValue(1.0)  # Valeur par défaut
        self.resolution_spin.setSingleStep(0.1)
        self.resolution_spin.setSuffix(" m")
        mesh_layout.addRow("Résolution du maillage:", self.resolution_spin)

        # Niveaux de hauteur
        self.height_levels_spin = QSpinBox()
        self.height_levels_spin.setRange(1, 10)
        self.height_levels_spin.setValue(3)  # Valeur par défaut
        mesh_layout.addRow("Nombre de niveaux de hauteur:", self.height_levels_spin)

        layout.addWidget(mesh_group_box)

        # --- GROUPE : Modèle de Propagation ---
        model_group_box = QGroupBox("Modèle de Propagation")
        model_layout = QFormLayout(model_group_box)

        # Modèle de propagation
        self.model_combo = QComboBox()
        # Ajout de modèles plus réalistes si disponibles
        self.model_combo.addItems([
            "free_space", 
            "material_aware", 
            "simple_ray_tracing"
        ])
        self.model_combo.setCurrentText("free_space")
        model_layout.addRow("Modèle de propagation:", self.model_combo)

        # StackedWidget pour les paramètres spécifiques aux modèles
        self.model_stack = QStackedWidget()
        
        # Page pour free_space (aucun paramètre)
        self.free_space_page = QWidget()
        free_space_layout = QVBoxLayout()
        free_space_layout.addWidget(QLabel("Aucun paramètre spécifique pour ce modèle."))
        self.free_space_page.setLayout(free_space_layout)
        
        # Page pour material_aware (aucun paramètre pour l'instant)
        self.material_aware_page = QWidget()
        material_aware_layout = QVBoxLayout()
        material_aware_layout.addWidget(QLabel("Aucun paramètre spécifique pour ce modèle."))
        self.material_aware_page.setLayout(material_aware_layout)
        
        # Page pour simple_ray_tracing
        self.simple_ray_tracing_page = QWidget()
        ray_tracing_layout = QFormLayout()
        
        self.max_reflections_spin = QSpinBox()
        self.max_reflections_spin.setRange(0, 10)
        self.max_reflections_spin.setValue(2)
        ray_tracing_layout.addRow("Réflexions maximales:", self.max_reflections_spin)
        
        self.simple_ray_tracing_page.setLayout(ray_tracing_layout)
        
        # Ajouter les pages au stacked widget
        self.model_stack.addWidget(self.free_space_page)
        self.model_stack.addWidget(self.material_aware_page)
        self.model_stack.addWidget(self.simple_ray_tracing_page)
        
        model_layout.addRow(self.model_stack)
        
        # Connecter le changement de modèle
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        
        layout.addWidget(model_group_box)

        # --- GROUPE : Visualisation ---
        vis_group_box = QGroupBox("Visualisation des Résultats")
        vis_layout = QFormLayout(vis_group_box)

        self.center_combo = QComboBox()
        self.center_combo.addItems(["Aucun"] + self.antenna_names)  # "Aucun" pour désactiver la zone
        self.center_combo.setCurrentText("Aucun")
        vis_layout.addRow("Centre de la zone d'intérêt:", self.center_combo)

        self.coverage_point_density_spin = QDoubleSpinBox()
        self.coverage_point_density_spin.setRange(0.001, 10000.0)
        self.coverage_point_density_spin.setValue(1.0)
        self.coverage_point_density_spin.setSingleStep(0.1)
        self.coverage_point_density_spin.setDecimals(3)
        self.coverage_point_density_spin.setSuffix(" pts/m³")
        vis_layout.addRow("Densité des points de couverture:", self.coverage_point_density_spin)

        layout.addWidget(vis_group_box)

        # Boutons OK/Annuler
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Initialiser l'état du stacked widget
        self.on_model_changed(self.model_combo.currentText())

    def on_model_changed(self, model_name):
        if model_name == "free_space":
            self.model_stack.setCurrentIndex(0)
        elif model_name == "material_aware":
            self.model_stack.setCurrentIndex(1)
        elif model_name == "simple_ray_tracing":
            self.model_stack.setCurrentIndex(2)

    def accept(self):
        try:
            # Récupérer les paramètres de base
            self.config_data = {
                "resolution": self.resolution_spin.value(),
                "height_levels": self.height_levels_spin.value(),
                "propagation_model": self.model_combo.currentText(),
                "rf_calculator_backend": "optimized",
                "visualization_mode": "heatmap",
                "interest_center": self.center_combo.currentText() if self.center_combo.currentText() != "Aucun" else None,
                "coverage_point_density": self.coverage_point_density_spin.value()
            }
            
            # Ajouter les paramètres spécifiques au modèle de propagation
            propagation_model_config = {}
            
            if self.model_combo.currentText() == "simple_ray_tracing":
                propagation_model_config = {
                    "max_reflections": self.max_reflections_spin.value()
                }
            elif self.model_combo.currentText() == "material_aware":
                propagation_model_config = {
                    "max_reflections": 3  # Valeur par défaut
                }
                
            self.config_data["propagation_model_config"] = propagation_model_config
            
            logger.debug(f"SimulationConfigDialog: Configuration validée: {self.config_data}")
            super().accept()
        except Exception as e:
            logger.error(f"SimulationConfigDialog.accept: Erreur lors de la validation: {e}")

    def get_config_data(self):
        return self.config_data