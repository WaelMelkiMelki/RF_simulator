"""
Fenêtre principale de l'application RF Simulator 3D.
Gère l'interface utilisateur, les interactions avec le backend et l'affichage 3D.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QListWidget, QVBoxLayout, QWidget, QSplitter, 
    QLabel, QMessageBox, QStatusBar, QToolBar, QDockWidget,
    QPushButton, QHBoxLayout, QProgressBar, QTextEdit, QFileDialog, QApplication,
    QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox, QDoubleSpinBox, QSlider,
    QListWidget, QListWidgetItem, QSpinBox, QMenuBar
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from gui.adapters.backend_adapter import BackendAdapter
from gui.widgets.scene_viewer_3d_widget import SceneViewer3DWidget
# --- MISE À JOUR: Import de la boîte de dialogue ---
from gui.dialogs.simulation_config_dialog import SimulationConfigDialog # <-- NOUVEAU
from gui.dialogs.scene_objects_dialog import SceneObjectsDialog # <-- NOUVEAU
# --- FIN MISE À JOUR ---
import logging
import os
logger = logging.getLogger(__name__)

# Classes de dialogue conservées au cas où, mais plus utilisées dans les barres d'outils
class AddAntennaDialog(QDialog):
    """Dialogue pour ajouter une nouvelle antenne."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ajouter une antenne")
        self.setModal(True)
        self.antenna_data = None
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout(self)
        # Type d'antenne
        self.type_combo = QComboBox()
        self.type_combo.addItems(["wifi", "5g"])
        layout.addRow("Type d'antenne:", self.type_combo)
        # Nom
        self.name_edit = QLineEdit()
        self.name_edit.setText("Nouvelle Antenne")
        layout.addRow("Nom:", self.name_edit)
        # Position X, Y, Z
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setRange(-1000, 1000)
        self.x_spin.setValue(0.0)
        layout.addRow("Position X:", self.x_spin)
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setRange(-1000, 1000)
        self.y_spin.setValue(0.0)
        layout.addRow("Position Y:", self.y_spin)
        self.z_spin = QDoubleSpinBox()
        self.z_spin.setRange(-100, 100)
        self.z_spin.setValue(2.0)  # Hauteur standard d'une antenne
        layout.addRow("Position Z:", self.z_spin)
        # Fréquence
        self.freq_edit = QLineEdit()
        self.freq_edit.setText("2.4GHz")
        layout.addRow("Fréquence:", self.freq_edit)
        # Puissance
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setRange(0, 100)
        self.power_spin.setValue(20.0)
        self.power_spin.setSuffix(" dBm")
        layout.addRow("Puissance:", self.power_spin)
        # Rayon de couverture
        self.coverage_radius_spin = QDoubleSpinBox()
        self.coverage_radius_spin.setRange(1, 100)
        self.coverage_radius_spin.setValue(10.0)
        self.coverage_radius_spin.setSuffix(" m")
        layout.addRow("Rayon de couverture:", self.coverage_radius_spin)
        # SSID (pour WiFi)
        self.ssid_edit = QLineEdit()
        self.ssid_edit.setText("MonReseau")
        layout.addRow("SSID (WiFi):", self.ssid_edit)
        # Boutons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        # Mettre à jour les champs selon le type
        self.type_combo.currentTextChanged.connect(self.update_field)

    def update_field(self, antenna_type):
        """Met à jour les champs selon le type d'antenne."""
        if antenna_type == "wifi":
            self.freq_edit.setText("2.4GHz")
            self.ssid_edit.setEnabled(True)
            self.power_spin.setValue(20.0)
        else:  # 5g
            self.freq_edit.setText("3.5GHz")
            self.ssid_edit.setEnabled(False)
            self.power_spin.setValue(30.0)  # 5G a généralement plus de puissance

    # Rien à faire ici, le code est déjà dans init_ui

    def accept(self):
        """Valide et stocke les données de l'antenne."""
        antenna_type = self.type_combo.currentText()
        name = self.name_edit.text()
        position = [self.x_spin.value(), self.y_spin.value(), self.z_spin.value()]
        frequency = self.freq_edit.text()
        power_dbm = self.power_spin.value()
        coverage_radius = self.coverage_radius_spin.value()
        ssid = self.ssid_edit.text() if antenna_type == "wifi" else ""

        self.antenna_data = {
            "type": antenna_type,
            "name": name,
            "position": position,
            "frequency": frequency,
            "power_dbm": power_dbm,
            "coverage_radius": coverage_radius,
            "ssid": ssid
        }
        super().accept()

    def get_antenna_data(self):
        """Retourne les données de l'antenne."""
        return self.antenna_data

class SelectInterestZoneDialog(QDialog):
    """Dialogue pour sélectionner une zone d'intérêt existante."""    
    def __init__(self, zones, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sélectionner une zone d'intérêt")
        self.setModal(True)
        self.selected_zone_index = -1
        self.zones = zones
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        for zone in self.zones:
            item = QListWidgetItem(str(zone))
            self.list_widget.addItem(item)
        layout.addWidget(QLabel("Sélectionner une zone d'intérêt :"))
        layout.addWidget(self.list_widget)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        """Valide et stocke l'index de la zone sélectionnée."""
        current_row = self.list_widget.currentRow()
        if current_row >= 0:
            self.selected_zone_index = current_row
        super().accept()

    def get_selected_zone_index(self):
        """Retourne l'index de la zone sélectionnée."""
        return self.selected_zone_index

class MainWindow(QMainWindow):
    def _update_scene_safe(self, scene):
        """Met à jour la scène 3D dans le visualiseur de manière sécurisée."""
        try:
            if hasattr(self, 'scene_viewer') and self.scene_viewer is not None:
                self.scene_viewer.update_scene(scene)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de la scène: {e}")
    def get_available_materials(self):
        """Retourne la liste des matériaux disponibles."""
        # Cette liste devrait venir d'une source de données (base de données, fichier de configuration, etc.)
        # Pour l'instant, nous utilisons une liste statique
        return ['default', 'brick', 'concrete', 'glass', 'wood', 'metal', 'drywall', 'plaster']
    
    def __init__(self):
        super().__init__()
        self.backend = BackendAdapter()
        self.is_scene_viewer_fullscreen_in_splitter = False
        self._saved_main_sizes = None
        self._saved_left_sizes = None
        self._saved_right_sizes = None
        self.interest_zones = []  # Liste des zones d'intérêt
        self.current_zone_index = -1  # Index de la zone active
        # --- NOUVEAU: Attributs pour le chargement de scène et la boîte de dialogue ---
        self._last_loaded_scene_path = None
        self._material_dialog = None
        # --- FIN NOUVEAU ---

        # Initialisation de l'interface utilisateur
        self.create_central_widget()
        self.create_status_bar()
        self.create_menu_bar() # Ajout de la création du menu
        self.create_dock_panels()  # <-- AJOUT
        self.setup_connections()
        self.setup_toolbars() # Ce setup_toolbars est modifié

        # Charger automatiquement la scène au démarrage
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.load_default_scene)

    # Charger automatiquement la scène au démarrage
    def load_default_scene(self):
        """Charge automatiquement la scène sans thread."""
        try:
            file_path = r"C:\Users\wael\Downloads\stage_netdata\app\urban_scene_modeling\scene.gltf"
            # Chargement direct sans thread
            from core.infrastructure.file_loader import FileLoader
            loader = FileLoader()
            scene = loader.load_file(file_path)
            self.on_scene_Loaded(scene)
        except Exception as e:
            error_msg = f"Erreur chargement automatique: {e}"
            logger.error(error_msg)

    def create_menu_bar(self):
        """Crée la barre de menus."""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")
        self.load_scene_action = QAction("Charger Scène...", self)
        self.load_scene_action.setShortcut("Ctrl+O")
        self.load_scene_action.triggered.connect(self.load_scene)
        file_menu.addAction(self.load_scene_action)
        
        file_menu.addSeparator()
        quit_action = QAction("Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Simulation
        sim_menu = menubar.addMenu("Simulation")
        self.run_sim_action = QAction("Démarrer Simulation", self)
        self.run_sim_action.setShortcut("F5")
        self.run_sim_action.triggered.connect(self.run_simulation)
        sim_menu.addAction(self.run_sim_action)
        
        # Menu Aide
        help_menu = menubar.addMenu("Aide")
        help_action = QAction("À propos", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

    def setup_connections(self):
        """Configure les connexions de signaux/slots."""
        self.backend.scene_loaded.connect(self.on_scene_Loaded)
        self.backend.antenna_added.connect(self.on_antenna_added)
        # --- CORRECTION: Ajout de la méthode manquante ---
        self.backend.antenna_selected.connect(self.on_antennas_selected)
        # --- FIN CORRECTION ---
        self.backend.simulation_started.connect(self.on_simulation_started)
        self.backend.simulation_progress.connect(self.on_progress_updated) # <-- Methode ajoutée
        self.backend.simulation_finished.connect(self.on_simulation_finished)
        self.backend.error_occurred.connect(self.on_error_occurred)

    def create_status_bar(self):
        """Crée la barre de statut."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt", 2000)

    def on_scene_load_error(self, error_msg):
        """Callback en cas d'erreur de chargement asynchrone."""
        try:
            # Si show_loading_indicator existe, masquer l'indicateur
            if hasattr(self, 'show_loading_indicator'):
                self.show_loading_indicator(False)
            error_msg = f"Erreur lors du chargement de la scène: {error_msg}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            if hasattr(self, 'show_error_message'):
                self.show_error_message(error_msg)
            else:
                QMessageBox.warning(self, "Erreur", error_msg)
        except Exception as e:
            logger.error(f"Erreur dans on_scene_load_error: {e}")

    def on_simulation_started(self):
        """Callback lorsque la simulation démarre."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Simulation en cours...", 2000)

    def on_error_occurred(self, message):
        """Callback lorsqu'une erreur se produit."""
        self.status_bar.showMessage(f"Erreur: {message}", 5000)
        QMessageBox.warning(self, "Erreur", message)

    # --- NOUVEAU: Ajout de la méthode manquante ---
    def on_progress_updated(self, progress, message):
        """Callback lors de la mise à jour de la progression."""
        logger.info(f"MainWindow: Mise à jour progression: {progress}% - {message}")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(message, 2000)
    # --- FIN NOUVEAU ---
    
    # --- NOUVEAU: Ajout de la méthode manquante ---
    def on_antennas_selected(self, antennas):
        """Callback lors de la sélection d'antennes."""
        logger.info(f"MainWindow: Antennes sélectionnées reçues: {[ant.name for ant in antennas]}")
        # Si vous avez une logique spécifique à exécuter quand des antennes
        # sont sélectionnées via le backend (pas via l'UI), vous pouvez la mettre ici.
        # Pour l'instant, on se contente de logger.
    # --- FIN NOUVEAU ---
    
    # --- NOUVEAU: Ajout de la méthode manquante ---
    def on_simulation_finished(self, results):
        """Callback lorsque la simulation est terminée."""
        logger.info(f"MainWindow: Résultats de simulation reçus: {type(results)}")
        try:
            # CORRECTION: Extraire les résultats et les antennes
            if isinstance(results, dict) and 'results' in results and 'antennas' in results:
                simulation_results = results['results']
                antennas = results['antennas']
            else:
                simulation_results = results
                antennas = self.backend.get_antennas() if hasattr(self.backend, 'get_antennas') else []
            # CORRECTION: Passer les paramètres d'affichage des points
            point_settings = {
                'opacity': getattr(self, 'point_opacity', 0.7),
                'size': getattr(self, 'point_size', 6)
            }
            self.scene_viewer.update_results_visualization(simulation_results, antennas, point_settings)
            self.progress_bar.setVisible(False)
            self.status_bar.showMessage("Simulation terminée - Valeurs négatives normales (puissance reçue)", 5000)
        except Exception as e:
            error_msg = f"Erreur lors de la mise à jour des résultats: {e}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "Erreur de visualisation", error_msg)
    # --- FIN NOUVEAU ---

    def setup_toolbars(self):
        """Configure les barres d'outils - MODIFIÉ"""
        # Barre d'outils principale
        self.toolbar = QToolBar("Outils principaux")
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Bouton Charger Scène
        load_scene_btn = QPushButton("Charger Scène")
        load_scene_btn.clicked.connect(self.load_scene)
        self.toolbar.addWidget(load_scene_btn)
        
        # Bouton Démarrer Simulation
        run_sim_btn = QPushButton("Démarrer Simulation")
        run_sim_btn.clicked.connect(self.run_simulation)
        self.toolbar.addWidget(run_sim_btn)
        
        # Bouton Réinitialiser
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.clicked.connect(self.reset_application)
        self.toolbar.addWidget(reset_btn)
        
        # === NOUVEAU: Bouton pour explorer les objets ===
        explore_objects_btn = QPushButton("🔍 Explorer objets")
        explore_objects_btn.clicked.connect(self.open_scene_objects_dialog)
        explore_objects_btn.setToolTip("Ouvre l'explorateur d'objets pour naviguer et assigner des matériaux")
        self.toolbar.addWidget(explore_objects_btn)
        
        self.toolbar.addSeparator()
        
        # Configuration du slider d'opacité des points
        self.toolbar.addWidget(QLabel("Opacité des points : "))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)  # 0.1 à 1.0 (multiplié par 10)
        self.opacity_slider.setValue(70)  # 0.7 par défaut
        self.opacity_slider.setFixedWidth(100)
        self.opacity_slider.valueChanged.connect(self.update_point_opacity)
        self.toolbar.addWidget(self.opacity_slider)
        self.toolbar.addWidget(QLabel("Densité des points : "))
        self.density_slider = QSlider(Qt.Orientation.Horizontal)
        self.density_slider.setRange(1, 20)  # 1 à 20 points
        self.density_slider.setValue(6)  # 6 par défaut
        self.density_slider.setFixedWidth(100)
        self.density_slider.valueChanged.connect(self.update_point_density)
        self.toolbar.addWidget(self.density_slider)
        self.toolbar.addWidget(QLabel(" Opacité scène: "))

        # Configuration du slider d'opacité de la scène
        self.scene_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.scene_opacity_slider.setRange(10, 100)  # 0.1 à 1.0 (multiplié par 10)
        self.scene_opacity_slider.setValue(100)      # 1.0 opaque par défaut
        self.scene_opacity_slider.setFixedWidth(100)
        self.scene_opacity_slider.valueChanged.connect(self.update_scene_opacity)
        self.toolbar.addWidget(self.scene_opacity_slider)

        # --- BARRE D'OUTILS PLAN DE VISUALISATION SUPPRIMÉE ---
        # plan_toolbar = QToolBar("Contrôles de plan")
        # self.addToolBar(Qt.ToolBarArea.TopToolBarArea, plan_toolbar)
        # plan_toolbar.addWidget(QLabel("Plan de visualisation:"))
        # # Combo box pour sélectionner le plan
        # self.plan_combo = QComboBox()
        # self.plan_combo.addItems([
        #     "XY (Horizontal)",
        #     "XZ (Vertical frontal)",
        #     "YZ (Vertical latéral droit)",
        #     "ZX (Vertical frontal alternatif)"
        # ])
        # self.plan_combo.setCurrentText("XY (Horizontal)")
        # self.plan_combo.currentTextChanged.connect(self.change_visualization_from_main)
        # plan_toolbar.addWidget(self.plan_combo)
        # # Slider pour la position orthogonale au plan
        # self.orthogonal_position_slider = QSlider(Qt.Orientation.Horizontal)
        # self.orthogonal_position_slider.setRange(-50, 50)  # Valeur par défaut, seront mises à jour avec la scène
        # self.orthogonal_position_slider.setValue(0)
        # self.orthogonal_position_slider.valueChanged.connect(self.update_orthogonal_position)
        # plan_toolbar.addWidget(QLabel("Position:"))
        # plan_toolbar.addWidget(self.orthogonal_position_slider)
        # # Spin box pour la position précise
        # self.orthogonal_position_spin = QDoubleSpinBox()
        # self.orthogonal_position_spin.setRange(-100, 100)
        # self.orthogonal_position_spin.setValue(0.0)
        # self.orthogonal_position_spin.setSingleStep(0.1)
        # self.orthogonal_position_spin.valueChanged.connect(self.update_orthogonal_position_from_spin)
        # plan_toolbar.addWidget(self.orthogonal_position_spin)
        # # Label pour indiquer l'axe contrôlé
        # self.axis_label = QLabel("Z:")
        # plan_toolbar.addWidget(self.axis_label)
        # -------------------------------------------------------

        # --- BARRE D'OUTILS ZONES D'INTÉRÊT SUPPRIMÉE ---
        # interest_toolbar = QToolBar("Contrôles de zone d'intérêt")
        # self.addToolBar(Qt.ToolBarArea.TopToolBarArea, interest_toolbar)
        # # Boutons pour gérer les zones d'intérêt
        # add_zone_action = QAction(QIcon.fromTheme("list-add", QIcon()), "Ajouter Zone", self)
        # add_zone_action.triggered.connect(self.add_interest_zone)
        # interest_toolbar.addAction(add_zone_action)
        # select_zone_action = QAction(QIcon.fromTheme("edit-find", QIcon()), "Sélectionner Zone", self)
        # select_zone_action.triggered.connect(self.select_interest_zone)
        # interest_toolbar.addAction(select_zone_action)
        # # Bouton pour supprimer uniquement la scène 3D
        # remove_scene_action = QAction(QIcon.fromTheme("edit-delete", QIcon()), "Supprimer Scène 3D", self)
        # remove_scene_action.triggered.connect(self.remove_scene_only)
        # interest_toolbar.addAction(remove_scene_action)
        # -----------------------------------------------

    # Méthodes pour le contrôle du plan de visualisation - conservées au cas où
    def change_visualization_from_main(self, plane_name):
        """Change le plan de visualisation depuis MainWindow."""
        try:
            logger.info(f"MainWindow: Changement du plan de visualisation vers {plane_name}")
            # Mettre à jour la vue selon le plan sélectionné via le backend
            if hasattr(self, 'scene_viewer'):
                self.scene_viewer.change_visualization(plane_name)
            # Mettre à jour l'axe contrôlé et les bornes
            self.update_orthogonal_axis_info(plane_name)
        except Exception as e:
            logger.error(f"MainWindow: Erreur lors du changement de plan: {e}")

    def update_orthogonal_axis_info(self, plane_name):
        """Met à jour l'axe contrôlé et les bornes du slider selon le plan sélectionné."""
        try:
            # Déterminer l'axe contrôlé selon le plan
            axis_mapping = {
                "XY (Horizontal)": ("Z", 2),
                "XZ (Vertical frontal)": ("Y", 1),
                "YZ (Vertical latéral droit)": ("X", 0),
                "ZX (Vertical frontal alternatif)": ("Y", 1)
            }
            axis_name, axis_index = axis_mapping.get(plane_name, ("Z", 2))
            # Mettre à jour le label de l'axe
            self.axis_label.setText(f"{axis_name}:")
            # Si une scène est Chargée, mettre à jour les bornes
            if hasattr(self.backend, 'current_scene') and self.backend.current_scene:
                bounds = self.backend.current_scene.get_bounds()
                if bounds and len(bounds) >= 6:
                    axis_min = bounds[axis_index * 2]
                    axis_max = bounds[axis_index * 2 + 1]
                    # Mettre à jour les plages des sliders
                    self.orthogonal_position_slider.setRange(int(axis_min * 10), int(axis_max * 10))
                    self.orthogonal_position_spin.setRange(axis_min, axis_max)
                    # Centrer sur la valeur moyenne
                    center_value = (axis_min + axis_max) / 2
                    self.orthogonal_position_slider.setValue(int(center_value * 10))
                    self.orthogonal_position_spin.setValue(center_value)
            logger.debug(f"MainWindow: Axe contrôlé mis à jour: {axis_name}")
        except Exception as e:
            logger.error(f"MainWindow: Erreur lors de la mise à jour de l'axe contrôlé: {e}")

    def update_orthogonal_position(self, value):
        """Met à jour la position orthogonale selon la valeur du slider."""
        try:
            position = float(value) / 10.0  # Convertir en mètre
            # Synchroniser avec le spin box
            self.orthogonal_position_spin.setValue(position)
            # Appliquer la position
            current_plan = self.plan_combo.currentText()
            axis_mapping = {
                "XY (Horizontal)": "Z",
                "XZ (Vertical frontal)": "Y",
                "YZ (Vertical latéral droit)": "X",
                "ZX (Vertical frontal alternatif)": "Y"
            }
            axis = axis_mapping.get(current_plan, "Z")
            if hasattr(self, 'scene_viewer'):
                self.scene_viewer.set_orthogonal_position(position, axis)
            logger.debug(f"MainWindow: Position orthogonale {axis} mise à jour: {position}")
        except Exception as e:
            logger.error(f"MainWindow: Erreur lors de la mise à jour de la position orthogonale: {e}")

    def update_orthogonal_position_from_spin(self, value):
        """Met à jour la position orthogonale selon la valeur du spin box."""
        try:
            # Synchroniser avec le slider
            self.orthogonal_position_slider.setValue(int(value * 10))  # Convertir en dixièmes
            # Appliquer la position
            current_plan = self.plan_combo.currentText()
            axis_mapping = {
                "XY (Horizontal)": "Z",
                "XZ (Vertical frontal)": "Y",
                "YZ (Vertical latéral droit)": "X",
                "ZX (Vertical frontal alternatif)": "Y"
            }
            axis = axis_mapping.get(current_plan, "Z")
            if hasattr(self, 'scene_viewer'):
                self.scene_viewer.set_orthogonal_position(value, axis)
            logger.debug(f"MainWindow: Position orthogonale {axis} mise à jour depuis spin: {value}")
        except Exception as e:
            logger.error(f"MainWindow: Erreur lors de la mise à jour de la position orthogonale depuis spin: {e}")

    # Méthodes pour l'opacité et la densité - conservées
    def update_scene_opacity(self, value):
        """Met à jour l'opacité de la scène 3D."""
        try:
            opacity = value / 100.0  # Convertir en valeur décimale (0.1 à 1.0)
            logger.debug(f"MainWindow: Mise à jour de l'opacité de la scène à {opacity:.2f}")
            # Mettre à jour l'opacité dans la visualisation
            if hasattr(self, 'scene_viewer'):
                self.scene_viewer.update_scene_opacity(opacity)
        except Exception as e:
            logger.error(f"MainWindow: Erreur lors de la mise à jour de l'opacité de la scène: {e}")

    def update_point_opacity(self, value):
        """Met à jour l'opacité des points de simulation."""
        try:
            opacity = value / 100.0  # Convertir en valeur décimale (0.1 à 1.0)
            logger.debug(f"MainWindow: Mise à jour de l'opacité des points à {opacity:.2f}")
            # Mettre à jour l'opacité dans la visualisation
            if hasattr(self, 'scene_viewer'):
                self.scene_viewer.update_point_opacity(opacity)
        except Exception as e:
            logger.error(f"MainWindow: Erreur lors de la mise à jour de l'opacité des points: {e}")

    def update_point_density(self, value):
        """Met à jour la densité (taille) des points de simulation."""
        try:
            size = value  # Valeur directe (1 à 20)
            logger.debug(f"MainWindow: Mise à jour de la densité des points à {size}")
            # Mettre à jour la densité dans la visualisation
            if hasattr(self, 'scene_viewer'):
                self.scene_viewer.update_point_density(size)
        except Exception as e:
            logger.error(f"MainWindow: Erreur lors de la mise à jour de la densité des points: {e}")

    def reset_application(self):
        """Réinitialise complètement l'application."""
        try:
            logger.info("MainWindow: Réinitialisation de l'application")
            self.status_bar.showMessage("Réinitialisation de l'application...", 2000)
            # Confirmation de la réinitialisation
            reply = QMessageBox.question(
                self,
                'Confirmation',
                'Êtes-vous sûr de vouloir réinitialiser complètement l\'application ?\nToutes les données seront perdues.',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Effacer la liste des antennes dans le sélecteur
                self.antenna_selector.clear()
                # Effacer la scène 3D
                if hasattr(self, 'scene_viewer'):
                    # Correction : vérifier l'existence des méthodes avant appel
                    if hasattr(self.scene_viewer, 'clear_scene'):
                        try:
                            self.scene_viewer.clear_scene()
                        except Exception as e:
                            logger.warning(f"Erreur clear_scene: {e}")
                    if hasattr(self.scene_viewer, 'initialize_empty_scene'):
                        try:
                            self.scene_viewer.initialize_empty_scene()
                        except Exception as e:
                            logger.warning(f"Erreur initialize_empty_scene: {e}")
                    # Effacer également les traces de simulation
                    if hasattr(self.scene_viewer, 'clear_results'):
                        try:
                            self.scene_viewer.clear_results()
                        except Exception as e:
                            logger.warning(f"Erreur clear_results: {e}")
                # Réinitialiser le backend
                if hasattr(self, 'backend'):
                    # Effacer les antennes du backend
                    if hasattr(self.backend, 'antennas'):
                        self.backend.antennas.clear()
                    # Réinitialiser la scène courante
                    if hasattr(self.backend, 'current_scene'):
                        self.backend.current_scene = None
                # Réinitialiser les états
                self.is_scene_viewer_fullscreen_in_splitter = False
                self.interest_zones = []
                self.current_zone_index = -1
                # Réafficher les panneaux si nécessaire
                if hasattr(self, 'left_panel'):
                    self.left_panel.setVisible(True)
                if hasattr(self, 'right_panel'):
                    self.right_panel.setVisible(True)
                # Réinitialiser les tailles par défaut
                if hasattr(self, 'main_splitter'):
                    self.main_splitter.setSizes([250, 900, 250])
                # Masquer les boutons de plein écran
                if hasattr(self, 'scene_viewer') and hasattr(self.scene_viewer, 'show_exit_fullscreen_button'):
                    try:
                        self.scene_viewer.show_exit_fullscreen_button(False)
                    except Exception as e:
                        logger.warning(f"Erreur show_exit_fullscreen_button: {e}")
                # Masquer la barre de progression
                if hasattr(self, 'progress_bar'):
                    self.progress_bar.setVisible(False)
                # Réinitialiser la barre de statut
                self.status_bar.showMessage("Application réinitialisée", 3000)
                logger.info("MainWindow: Application réinitialisée avec succès")
        except Exception as e:
            error_msg = f"Erreur lors de la réinitialisation de l'application: {e}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "Erreur de réinitialisation", error_msg)

    def create_central_widget(self):
        """Crée le widget central avec le visualiseur 3D."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        # Barre de progression pour les simulations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        # Splitter principal
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        # Visualiseur 3D
        self.scene_viewer = SceneViewer3DWidget()
        self.main_splitter.addWidget(self.scene_viewer)
        layout.addWidget(self.main_splitter)
        logger.info("MainWindow: Widget central créé")

    def create_dock_panels(self):
        """Crée les panneaux dockable pour les contrôles."""
        # Panneau gauche - Sélection des antennes
        left_dock = QDockWidget("Antennes", self)
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.antenna_selector = QListWidget()
        self.antenna_selector.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        left_layout.addWidget(QLabel("Sélectionner les antennes :"))
        left_layout.addWidget(self.antenna_selector)
        
        # NOUVEAU BOUTON - Utilise le dialogue AddAntennaDialog
        add_antenna_manual_btn = QPushButton("Ajouter Antenne")
        add_antenna_manual_btn.clicked.connect(self.add_antenna) # <-- Connecté à la méthode qui ouvre le dialogue
        left_layout.addWidget(add_antenna_manual_btn)
        
        left_dock.setWidget(left_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)
        
        # Panneau droit - Logs et informations
        right_dock = QDockWidget("Logs et Informations", self)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        right_layout.addWidget(QLabel("Logs de l'application :"))
        right_layout.addWidget(self.log_display)
        right_dock.setWidget(right_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)
        # Stockage des références
        self.left_panel = left_dock
        self.right_panel = right_dock

    def add_antenna(self):
        """Ouvre le dialogue pour ajouter une antenne avec ses caractéristiques."""
        try:
            dialog = AddAntennaDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                antenna_data = dialog.get_antenna_data()
                # --- CORRECTION: Vérifier si antenna_data existe et contient 'name' ---
                if antenna_data and "name" in antenna_data:
                    from core.domain.antenna_factory import AntennaFactory
                    # Normaliser le nom de l'antenne : espaces, unicité, caractères spéciaux
                    normalized_name = antenna_data["name"].replace(" ", "_").strip()
                    normalized_name = ''.join(c for c in normalized_name if c.isalnum() or c == '_')
                    existing_names = [self.antenna_selector.item(i).text() for i in range(self.antenna_selector.count())]
                    unique_name = normalized_name
                    suffix = 1
                    while unique_name in existing_names:
                        unique_name = f"{normalized_name}_{suffix}"
                        suffix += 1
                    antenna_data["name"] = unique_name
                    try:
                        factory = AntennaFactory()
                        antenna = factory.create_antenna(
                            antenna_data["type"],
                            {
                                "name": antenna_data["name"],
                                "position": antenna_data["position"],
                                "frequency": antenna_data["frequency"],
                                "power_dbm": antenna_data["power_dbm"],
                                "coverage_radius": antenna_data["coverage_radius"],
                                "ssid": antenna_data["ssid"]
                            }
                        )
                        self.backend.add_antenna(antenna)
                        self.status_bar.showMessage(
                            f"Antenne {antenna.name} ajoutée à la position ({antenna.position[0]:.1f}, {antenna.position[1]:.1f}, {antenna.position[2]:.1f})", 3000)
                    except Exception as e:
                        error_msg = f"Erreur lors de l'ajout de l'antenne: {e}"
                        logger.error(error_msg)
                        self.status_bar.showMessage(error_msg, 5000)
                        QMessageBox.warning(self, "Erreur d'ajout", error_msg)
        except Exception as e:
            error_msg = f"Erreur lors de l'ouverture du dialogue d'ajout d'antenne: {e}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "Erreur d'ouverture", error_msg)

    class LogHandler(logging.Handler):
        """Handler personnalisé pour afficher les logs dans l'interface."""
        def __init__(self, text_edit):
            super().__init__()
            self.text_edit = text_edit

        def emit(self, record):
            msg = self.format(record)
            # Utiliser une méthode thread-safe pour mettre à jour l'interface
            self.text_edit.append(msg)

    def load_sample_data(self):
        """Charge des données d'exemple au démarrage."""
        try:
            # Exemple d'import et de placement d'une antenne
            from core.infrastructure.file_loader import FileLoader
            from core.domain.antenna_factory import AntennaFactory
            # Vérifier si le fichier de scène existe
            scene_file = "data/test_scene.obj"
            if os.path.exists(scene_file):
                loader = FileLoader()
                scene = loader.load_file(scene_file)
                # Créer une antenne WiFi d'exemple
                antenna_config = {
                    "name": "WiFi Antenna 1",
                    "position": [0, 0, 1],
                    "frequency": "2.4GHz",
                    "power_dbm": 20.0,
                    "coverage_radius": 10.0,  # Rayon de couverture
                    "ssid": "TestNetwork"
                }
                factory = AntennaFactory()
                antenna = factory.create_antenna("wifi", antenna_config)
                # Ajout de l'antenne dans le sélecteur
                self.on_antenna_added(antenna)
                # Mise à jour de la scène 3D
                self.scene_viewer.update_scene(scene)
                self.status_bar.showMessage("Données d'exemple Chargées", 3000)
            else:
                self.status_bar.showMessage("Fichier de scène non trouvé", 3000)
        except Exception as e:
            logger.error(f"Erreur lors du chargement des données d'exemple: {e}")
            self.status_bar.showMessage("Erreur Charger données exemple", 5000)

    def toggle_scene_viewer_fullscreen_in_splitter(self):
        """
        Bascule le SceneViewer3D en mode "plein écran" au sein du splitter principal.
        Cela masque les panneaux latéraux et agrandit le visualiseur.
        """
        try:
            if not self.is_scene_viewer_fullscreen_in_splitter:
                logger.info("MainWindow: Passage de SceneViewer3D en mode 'plein écran' dans le splitter.")
                # 1. Sauvegarder les tailles actuelles des splitters
                if hasattr(self, 'left_panel'):
                    self._saved_left_sizes = self.left_panel.size()
                if hasattr(self, 'right_panel'):
                    self._saved_right_sizes = self.right_panel.size()
                if hasattr(self, 'main_splitter'):
                    self._saved_main_sizes = self.main_splitter.sizes()
                # 2. Masquer les panneaux latéraux
                if hasattr(self, 'left_panel'):
                    self.left_panel.setVisible(False)
                if hasattr(self, 'right_panel'):
                    self.right_panel.setVisible(False)
                # 3. Agrandir le SceneViewer3D dans le splitter principal
                if hasattr(self, 'main_splitter'):
                    total_width = self.width()
                    new_main_sizes = [0, total_width, 0]  # [gauche, milieu, droite]
                    self.main_splitter.setSizes(new_main_sizes)
                self.is_scene_viewer_fullscreen_in_splitter = True
                self.status_bar.showMessage("Vue SceneViewer3D agrandie", 2000)
                logger.info("MainWindow: SceneViewer3D agrandi dans le splitter.")
                # Afficher le bouton de sortie dans SceneViewer3D
                if hasattr(self, 'scene_viewer') and hasattr(self.scene_viewer, 'show_exit_fullscreen_button'):
                    self.scene_viewer.show_exit_fullscreen_button(True)
            else:
                logger.info("MainWindow: Restauration de la vue normale depuis le mode 'plein écran' du splitter.")
                # 1. Réafficher les panneaux latéraux
                if hasattr(self, 'left_panel'):
                    self.left_panel.setVisible(True)
                if hasattr(self, 'right_panel'):
                    self.right_panel.setVisible(True)
                # 2. Restaurer les tailles sauvegardées
                restored = False
                if self._saved_main_sizes and hasattr(self, 'main_splitter'):
                    self.main_splitter.setSizes(self._saved_main_sizes)
                    restored = True
                if self._saved_left_sizes and hasattr(self, 'left_panel'):
                    self.left_panel.resize(self._saved_left_sizes)
                if self._saved_right_sizes and hasattr(self, 'right_panel'):
                    self.right_panel.resize(self._saved_right_sizes)
                # Si aucune taille n'a été restaurée, remettre les tailles par défaut
                if not restored and hasattr(self, 'main_splitter'):
                    self.main_splitter.setSizes([250, 900, 250])  # Taille par défaut
                self.is_scene_viewer_fullscreen_in_splitter = False
                self.status_bar.showMessage("Vue normale restaurée", 2000)
                logger.info("MainWindow: Vue normale de SceneViewer3D restaurée.")
                # Masquer le bouton de sortie dans SceneViewer3D
                if hasattr(self, 'scene_viewer') and hasattr(self.scene_viewer, 'show_exit_fullscreen_button'):
                    self.scene_viewer.show_exit_fullscreen_button(False)
        except Exception as e:
            error_msg = f"Erreur lors du basculement du mode 'plein écran' dans le splitter: {e}"
            logger.error(f"MainWindow.toggle_scene_viewer_fullscreen_in_splitter: {error_msg}")
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "Erreur Plein Écran Splitter", error_msg)

    def on_antenna_added(self, antenna):
        """Callback lorsqu'une antenne est ajoutée."""
        self.antenna_selector.addItem(antenna.name)
        # Sélectionner automatiquement la nouvelle antenne
        items = self.antenna_selector.findItems(antenna.name, Qt.MatchFlag.MatchExactly)
        if items:
            items[0].setSelected(True)
            self.update_selected_antennas()  # Mettre à jour la sélection dans le backend
        # Ajouter la visualisation de l'antenne (seulement le cylindre, pas le rayon)
        if hasattr(self, 'scene_viewer'):
            self.scene_viewer.add_antenna_visualization(antenna)
        logger.info(f"MainWindow: Antenne ajoutée reçue du backend: {type(antenna)} - {antenna.name}")

    def update_selected_antennas(self):
        """Met à jour les antennes sélectionnées."""
        selected_items = self.antenna_selector.selectedItems()
        selected_ids = [item.text() for item in selected_items]
        self.backend.select_antenna(selected_ids)
        logger.info(f"MainWindow: Antennes sélectionnées: {selected_ids}")

    # --- NOUVEAU: Méthode modifiée on_scene_Loaded ---
    def on_scene_Loaded(self, scene):
        """
        Callback lorsqu'une scène est chargée.
        Si la scène provient d'un fichier GLTF, ouvre le dialogue d'attribution des matériaux.
        """
        logger.info(f"Scène chargée: {type(scene)}")
        self.backend.current_scene = scene

        # VALIDATION CRITIQUE: Vérifier que la scène contient des meshes
        mesh_names = scene.get_mesh_names()
        if not mesh_names:
            error_msg = "La scène ne contient aucun mesh valide. Format de fichier peut-être incompatible."
            logger.error(error_msg)
            self.show_error_message(error_msg)
            return

        # Mise à jour de la vue
        QTimer.singleShot(100, lambda: self._update_scene_safe(scene))

        # Ouvrir le dialogue UNIQUEMENT si meshes existent
        if self._last_loaded_scene_path and self._last_loaded_scene_path.lower().endswith((".gltf", ".glb")):
            if mesh_names:  # Double validation
                logger.info("Scène GLTF chargée avec des meshes - pas de dialogue de matériaux")
                # Dialogue de matériaux supprimé selon la demande de l'utilisateur
        
        # === NOUVEAU: Ouvrir automatiquement le dialogue d'exploration d'objets ===
        QTimer.singleShot(500, lambda: self._open_scene_objects_dialog(scene))
        
    # --- NOUVEAU ---

    # --- FIN NOUVEAU ---

    # --- NOUVEAU: Méthode load_scene modifiée ---
    def load_scene(self):
        """Charge une scène depuis un fichier."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Charger une scène 3D",
                "",
                "Fichiers 3D (*.obj *.stl *.glb *.gltf *.ply);;Tous les fichiers (*)"
            )
            if file_path:
                self.status_bar.showMessage(f"Chargement de la scène: {os.path.basename(file_path)}", 2000)
                # Utiliser le chargement asynchrone
                self.load_scene_async(file_path)
        except Exception as e:
            error_msg = f"Erreur lors du Chargement de la scène: {e}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "Erreur de Chargement", error_msg)
    # --- FIN NOUVEAU ---

    # --- MISE À JOUR: Méthode run_simulation ---
    def run_simulation(self):
        """
        Démarre la simulation.
        Ouvre d'abord le dialogue de configuration.
        """
        try:
            # Obtenir la liste des noms d'antennes pour le dialogue
            # Cela suppose que vous avez un moyen d'accéder aux noms, 
            # par exemple via self.backend.get_antennas() ou en parcourant self.antenna_selector
            try:
                # Option 1: Via le backend (si la méthode existe)
                # antenna_names = [ant.name for ant in self.backend.get_antennas()]
                
                # Option 2: Via l'UI (plus robuste si l'UI est la source canonique à ce moment)
                antenna_names = [self.antenna_selector.item(i).text() for i in range(self.antenna_selector.count())]
            except Exception as names_err:
                logger.warning(f"MainWindow.run_simulation: Impossible d'obtenir la liste des antennes pour le dialogue: {names_err}. Utilisation d'une liste vide.")
                antenna_names = []

            # 1. Créer et configurer le dialogue
            dialog = SimulationConfigDialog(antenna_names, parent=self)

            # 2. Afficher le dialogue de manière modale
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # 3. Récupérer les données de configuration si l'utilisateur clique sur OK
                config = dialog.get_config_data()
                
                if config:
                    self.status_bar.showMessage("Démarrage de la simulation...", 2000)
                    logger.info(f"MainWindow.run_simulation: Configuration reçue du dialogue: {config}")
                    
                    # 4. Utiliser la configuration pour démarrer la simulation
                    # Le backend s'occupera de la logique en utilisant config["coverage_point_density"]
                    self.backend.start_simulation(config)
                else:
                    # Normalement, get_config_data ne devrait pas retourner None si exec() == Accepted,
                    # mais c'est une bonne pratique de vérifier.
                    logger.warning("MainWindow.run_simulation: Aucune configuration reçue du dialogue.")
                    self.status_bar.showMessage("Simulation annulée: configuration invalide.", 3000)
            else:
                # L'utilisateur a cliqué sur Annuler
                logger.info("MainWindow.run_simulation: Démarrage de la simulation annulé par l'utilisateur.")
                self.status_bar.showMessage("Simulation annulée.", 2000)

        except Exception as e:
            error_msg = f"Erreur lors du démarrage de la simulation: {e}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "Erreur de simulation", error_msg)
    # --- FIN MISE À JOUR ---

    def show_help(self):
        """Affiche l'aide de l'application."""
        help_text = """
        <h2>RF Simulator 3D - Aide</h2>
        <p><b>Fonctionnalités principales</b></p>
        <ul>
            <li>Visualisation 3D de scènes avec antennes</li>
            <li>Simulation de propagation RF</li>
            <li>Analyse de couverture réseau</li>
            <li>Export des résultats</li>
        </ul>
        <p><b>Contrôles</b></p>
        <ul>
            <li>Clic gauche + glisser : Rotation de la vue 3D</li>
            <li>Molette souris : Zoom</li>
            <li>Clic droit + glisser : Déplacement de la vue</li>
            <li>Double-clic sur antenne : Propriétés</li>
        </ul>
        <p><b>Formats supportés</b></p>
        <ul>
            <li>OBJ (.obj)</li>
            <li>STL (.stl)</li>
            <li>GLB/GLTF (.glb, .gltf)</li>
            <li>PLY (.ply)</li>
        </ul>
        """
        QMessageBox.information(self, "Aide RF Simulator 3D", help_text)

    def closeEvent(self, event):
        """Gère la fermeture de l'application."""
        logger.info("MainWindow: Fermeture de l'application")
        # Désactiver la surbrillance au survol
        if hasattr(self, 'scene_viewer'):
            self.scene_viewer.enable_mesh_hover_highlight(False)

        reply = QMessageBox.question(
            self,
            'Confirmation',
            'Êtes-vous sûr de vouloir quitter ?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    # Méthodes pour la gestion des zones d'intérêt - conservées mais plus appelées via barre d'outils
    def add_interest_zone(self):
        """Ajoute une nouvelle zone d'intérêt via un dialogue."""
        try:
            # Utilise SelectInterestZoneDialog pour ajouter une nouvelle zone
            center_dialog = SelectInterestZoneDialog(self.interest_zones, self)
            if center_dialog.exec() == QDialog.DialogCode.Accepted:
                selected_index = center_dialog.get_selected_zone_index()
                if selected_index >= 0:
                    self.current_zone_index = selected_index
                    logger.info(f"MainWindow: Zone d'intérêt sélectionnée: {self.interest_zones[selected_index]}")
                    if hasattr(self, 'scene_viewer'):
                        self.scene_viewer.set_interest_zones(self.interest_zones, self.current_zone_index)
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout de la zone d'intérêt: {e}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "Erreur", error_msg)

    def select_interest_zone(self):
        """Permet à l'utilisateur de sélectionner une zone d'intérêt existante."""
        if not self.interest_zones:
            QMessageBox.information(self, "Info", "Aucune zone d'intérêt définie.")
            return
        # Créer un dialogue de sélection
        dialog = SelectInterestZoneDialog(self.interest_zones, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_index = dialog.get_selected_zone_index()
            if selected_index >= 0:
                self.current_zone_index = selected_index
                logger.info(f"MainWindow: Zone d'intérêt sélectionnée: {self.interest_zones[selected_index]}")
                if hasattr(self, 'scene_viewer'):
                    self.scene_viewer.set_interest_zones(self.interest_zones, self.current_zone_index)
                    # self.update_interest_radius(self.interest_radius_slider.value()) # Pas de slider défini
        else:
            self.status_bar.showMessage("Sélection de zone annulée", 2000)

    def update_interest_radius(self, value):
        """Met à jour le rayon de la zone d'intérêt active."""
        try:
            radius = float(value)  # Valeur en mètre
            logger.debug(f"MainWindow: Mise à jour du rayon de la zone d'intérêt à {radius}m")
            # Mettre à jour le rayon de la zone active
            if 0 <= self.current_zone_index < len(self.interest_zones):
                self.interest_zones[self.current_zone_index].radius = radius
            # Passer toutes les zones au SceneViewer3D
            if hasattr(self, 'scene_viewer'):
                self.scene_viewer.set_interest_zones(self.interest_zones, self.current_zone_index)
        except Exception as e:
            logger.error(f"MainWindow: Erreur lors de la mise à jour du rayon de la zone: {e}")

    def remove_scene_only(self):
        """Supprime uniquement la scène 3D (le modèle de l'environnement), sans affecter les points de simulation."""
        try:
            logger.info("MainWindow: Suppression uniquement de la scène 3D")
            # Effacer la scène 3D
            if hasattr(self, 'scene_viewer'):
                # Correction : vérifier l'existence des méthodes avant appel
                if hasattr(self.scene_viewer, 'clear_scene'):
                    try:
                        self.scene_viewer.clear_scene()
                    except Exception as e:
                        logger.warning(f"Erreur clear_scene: {e}")
                # Ne PAS effacer les résultats de simulation
                # Les points de simulation sont conservés
                # Réinitialiser la scène avec un contenu vide
                if hasattr(self.scene_viewer, 'initialize_empty_scene'):
                    try:
                        self.scene_viewer.initialize_empty_scene()
                    except Exception as e:
                        logger.warning(f"Erreur initialize_empty_scene: {e}")
            # Mettre à jour la barre de statut
            self.status_bar.showMessage("Scène 3D supprimée", 2000)
        except Exception as e:
            error_msg = f"Erreur lors de la suppression de la scène 3D: {e}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.warning(self, "Erreur de suppression", error_msg)

    def load_scene_async(self, file_path):
        """Charge une scène avec gestion robuste du threading et fallback synchrone."""
        try:
            from PyQt6.QtCore import QThread
            # Vérification robuste de l'état du thread
            if (hasattr(self, 'loading_thread') and 
                self.loading_thread is not None and 
                isinstance(self.loading_thread, QThread) and 
                self.loading_thread.isRunning()):
                self.loading_thread.quit()
                self.loading_thread.wait(1000)
                self.loading_thread = None

            self._last_loaded_scene_path = file_path

            # Utiliser directement le file_loader du backend
            try:
                from core.infrastructure.file_loader import FileLoader
                loader = FileLoader()
                scene = loader.load_file(file_path)
                self.on_scene_Loaded(scene)
            except Exception as e:
                error_msg = f"Erreur chargement scène: {e}"
                logger.error(error_msg)
                self.status_bar.showMessage(error_msg, 5000)
                self.show_error_message(error_msg)
        except Exception as e:
            error_msg = f"Erreur chargement scène: {e}"
            logger.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            self.show_error_message(error_msg)

    def _open_scene_objects_dialog(self, scene):
        """Ouvre le dialogue d'exploration et de navigation des objets de la scène."""
        try:
            if not scene:
                return
                
            # Créer et afficher le dialogue d'objets
            self.scene_objects_dialog = SceneObjectsDialog(scene, parent=self)
            
            # Connecter les signaux pour l'interaction avec la vue 3D
            self.scene_objects_dialog.object_selected.connect(self._on_object_selected)
            self.scene_objects_dialog.object_highlighted.connect(self._on_object_highlighted)
            self.scene_objects_dialog.material_assigned.connect(self._on_material_assigned_from_dialog)
            
            # Afficher le dialogue de manière non-modale
            self.scene_objects_dialog.show()
            
            logger.info("Dialogue d'exploration d'objets ouvert")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture du dialogue d'objets: {e}")
    
    def _on_object_selected(self, object_name):
        """Appelé quand un objet est sélectionné dans le dialogue."""
        try:
            # Centrer la vue 3D sur l'objet sélectionné
            if hasattr(self.scene_viewer, 'center_on_object'):
                self.scene_viewer.center_on_object(object_name)
            
            logger.debug(f"Objet sélectionné: {object_name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la sélection d'objet: {e}")
    
    def _on_object_highlighted(self, object_name, highlight):
        """Appelé quand un objet doit être mis en surbrillance."""
        try:
            # Appliquer la surbrillance dans la vue 3D
            if hasattr(self.scene_viewer, 'highlight_object'):
                success = self.scene_viewer.highlight_object(object_name, highlight)
                if success:
                    action = "surligné" if highlight else "désurligné"
                    self.status_bar.showMessage(f"Objet {object_name} {action}", 2000)
                else:
                    logger.warning(f"Impossible de surligner l'objet: {object_name}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la surbrillance d'objet: {e}")
    
    def _on_material_assigned_from_dialog(self, object_name, material_properties):
        """Appelé quand un matériau est assigné depuis le dialogue d'objets."""
        try:
            # Mettre à jour les propriétés de matériau dans le backend
            if hasattr(self.backend, 'current_scene') and self.backend.current_scene:
                # Créer ou mettre à jour le mapping des matériaux
                if not hasattr(self.backend.current_scene, 'mesh_material_mapping'):
                    self.backend.current_scene.mesh_material_mapping = {}
                
                self.backend.current_scene.mesh_material_mapping[object_name] = material_properties
                
                # Propager les matériaux si la méthode existe
                if hasattr(self.backend.current_scene, 'propagate_materials_to_cells'):
                    self.backend.current_scene.propagate_materials_to_cells()
            
            # NOUVEAU: Appliquer la couleur du matériau dans la visualisation 3D
            if hasattr(self, 'scene_viewer') and self.scene_viewer:
                self.scene_viewer.apply_material_color(object_name, material_properties)
            
            self.status_bar.showMessage(f"Matériau assigné à {object_name}", 3000)
            logger.info(f"Matériau assigné: {object_name} -> {material_properties}")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'assignation de matériau: {e}")
            self.status_bar.showMessage(f"Erreur d'assignation: {e}", 5000)

    def open_scene_objects_dialog(self):
        """Ouvre le dialogue d'exploration d'objets (méthode publique accessible depuis la toolbar)."""
        try:
            if hasattr(self.backend, 'current_scene') and self.backend.current_scene:
                self._open_scene_objects_dialog(self.backend.current_scene)
            else:
                self.status_bar.showMessage("Aucune scène chargée. Chargez d'abord une scène 3D.", 3000)
                QMessageBox.information(
                    self,
                    "Aucune scène",
                    "Veuillez d'abord charger une scène 3D pour explorer ses objets."
                )
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture du dialogue: {e}")
            self.status_bar.showMessage(f"Erreur: {e}", 5000)

    def show_error_message(self, message):
        """Affiche un message d'erreur à l'utilisateur."""
        QMessageBox.critical(self, "Erreur", message)