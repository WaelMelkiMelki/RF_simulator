# src/gui/widgets/scene_viewer_3d_widget.py
"""
Widget de présentation pour la visualisation 3D - NETDATA INNOVATION
Couche PRESENTATION - Interface utilisateur PyQt6 pour la visualisation 3D.
Conforme à l'architecture NETDATA avec séparation des responsabilités.
"""
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal

from .visualization_engine import VisualizationEngine

logger = logging.getLogger(__name__)

class SceneViewer3DWidget(QWidget):
    """
    Widget de présentation pour la visualisation 3D.
    
    COUCHE PRESENTATION - Architecture NETDATA INNOVATION
    Responsabilités :
    - Interface utilisateur PyQt6
    - Gestion des événements UI
    - Layout et contrôles visuels
    - Communication avec la couche Application via signaux
    
    Connecté à VisualizationEngine (Infrastructure Layer)
    """
    
    # Signaux pour la communication avec la couche Application
    mesh_selected = pyqtSignal(int)
    right_click_position = pyqtSignal(float, float, float)
    mesh_hovered = pyqtSignal(str)
    fullscreen_requested = pyqtSignal()
    view_changed = pyqtSignal(str)  # Signal pour changement de vue
    
    def __init__(self, parent=None):
        """Initialise le widget de présentation."""
        super().__init__(parent)
        
        # Référence au moteur de visualisation (Infrastructure Layer)
        self.visualization_engine = None
        
        # État de l'interface
        self.is_fullscreen = False
        
        self.init_ui()
        self.setup_visualization_engine()
        
    def init_ui(self):
        """Initialise l'interface utilisateur du widget."""
        logger.info("SceneViewer3DWidget: Initialisation de l'interface utilisateur")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container pour le moteur de visualisation
        self.visualization_container = QFrame(self)
        self.visualization_container.setFrameStyle(QFrame.Shape.StyledPanel)
        layout.addWidget(self.visualization_container)
        
        # Bouton de sortie du mode plein écran
        self.exit_fullscreen_button = QPushButton("✕ Quitter Plein Écran")
        self.exit_fullscreen_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 0, 0, 150);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 200);
            }
        """)
        self.exit_fullscreen_button.clicked.connect(self.exit_fullscreen_mode)
        self.exit_fullscreen_button.setVisible(False)
        
        # Container pour les contrôles
        button_container = QFrame(self)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.exit_fullscreen_button)
        button_layout.setContentsMargins(10, 10, 0, 0)
        button_container.setLayout(button_layout)
        layout.addWidget(button_container)
        layout.setAlignment(button_container, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        
        # Configuration focus pour interactions
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
    def setup_visualization_engine(self):
        """Configure le moteur de visualisation."""
        try:
            # Créer le moteur de visualisation (Infrastructure Layer)
            self.visualization_engine = VisualizationEngine(parent=self.visualization_container)
            
            # Layout pour intégrer le moteur
            container_layout = QVBoxLayout()
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addWidget(self.visualization_engine)
            self.visualization_container.setLayout(container_layout)
            
            # Connecter les signaux du moteur vers les signaux du widget
            self.visualization_engine.mesh_selected.connect(self.mesh_selected.emit)
            self.visualization_engine.right_click_position.connect(self.right_click_position.emit)
            self.visualization_engine.mesh_hovered.connect(self.mesh_hovered.emit)
            
            logger.info("SceneViewer3DWidget: Moteur de visualisation configuré")
            
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur configuration moteur: {e}")
            import traceback
            traceback.print_exc()
    
    def update_scene(self, scene):
        """
        Met à jour la scène via le moteur de visualisation.
        
        Interface vers la couche Application (via Orchestrator).
        """
        if self.visualization_engine:
            self.visualization_engine.update_scene(scene)
    
    def show_antenna_coverage(self, results_dict, antennas=None):
        """Affiche la couverture d'antennes via le moteur."""
        if self.visualization_engine:
            self.visualization_engine.show_antenna_coverage(results_dict, antennas)
    
    def clear_antennas(self):
        """Efface les antennes via le moteur."""
        if self.visualization_engine:
            self.visualization_engine.clear_antennas()
    
    def add_antenna(self, position, antenna_type="base", name=None, properties=None):
        """Ajoute une antenne via le moteur."""
        if self.visualization_engine:
            return self.visualization_engine.add_antenna(position, antenna_type, name, properties)
    
    def switch_to_fullscreen_mode(self):
        """Bascule en mode plein écran."""
        logger.info("SceneViewer3DWidget: Basculement en mode plein écran")
        self.is_fullscreen = True
        self.exit_fullscreen_button.setVisible(True)
        self.fullscreen_requested.emit()
        
    def exit_fullscreen_mode(self):
        """Sort du mode plein écran."""
        logger.info("SceneViewer3DWidget: Sortie du mode plein écran")
        self.is_fullscreen = False
        self.exit_fullscreen_button.setVisible(False)
        
        # Émettre signal pour notifier la fenêtre principale
        self.view_changed.emit("normal")
    
    def keyPressEvent(self, event):
        """Gère les événements clavier pour l'interface."""
        try:
            # F11 pour plein écran
            if event.key() == Qt.Key.Key_F11:
                if not self.is_fullscreen:
                    self.switch_to_fullscreen_mode()
                else:
                    self.exit_fullscreen_mode()
                return
            
            # Déléguer les autres événements au moteur de visualisation
            if self.visualization_engine:
                self.visualization_engine.keyPressEvent(event)
                
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur événement clavier: {e}")
        
        super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """Gère le redimensionnement du widget."""
        super().resizeEvent(event)
        if self.visualization_engine:
            self.visualization_engine.resizeEvent(event)
    
    def closeEvent(self, event):
        """Gère la fermeture du widget."""
        try:
            if self.visualization_engine:
                self.visualization_engine.cleanup()
            logger.info("SceneViewer3DWidget: Widget fermé proprement")
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur fermeture: {e}")
        
        super().closeEvent(event)
    
    # Méthodes de délégation vers le moteur (Interface Application Layer)
    def update_point_opacity(self, opacity):
        """Délègue la mise à jour d'opacité des points au moteur."""
        try:
            if self.visualization_engine:
                # Valider l'opacité (doit être entre 0.0 et 1.0)
                opacity = max(0.0, min(1.0, float(opacity)))
                self.visualization_engine.update_point_opacity(opacity)
                logger.info(f"SceneViewer3DWidget: Opacité des points mise à jour à {opacity:.2f}")
            else:
                logger.warning("SceneViewer3DWidget: Moteur de visualisation non disponible pour mise à jour opacité points")
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur mise à jour opacité points: {e}")
    
    def update_point_density(self, size):
        """Délègue la mise à jour de densité des points au moteur."""
        try:
            if self.visualization_engine:
                # Valider la taille (doit être positive et raisonnable)
                size = max(1.0, min(20.0, float(size)))
                self.visualization_engine.update_point_density(size)
                logger.info(f"SceneViewer3DWidget: Densité des points mise à jour à {size:.1f}")
            else:
                logger.warning("SceneViewer3DWidget: Moteur de visualisation non disponible pour mise à jour densité points")
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur mise à jour densité points: {e}")
    
    def update_scene_opacity(self, opacity):
        """Délègue la mise à jour d'opacité de scène au moteur."""
        try:
            if self.visualization_engine:
                # Valider l'opacité (doit être entre 0.0 et 1.0)
                opacity = max(0.0, min(1.0, float(opacity)))
                self.visualization_engine.update_scene_opacity(opacity)
                logger.info(f"SceneViewer3DWidget: Opacité de la scène mise à jour à {opacity:.2f}")
            else:
                logger.warning("SceneViewer3DWidget: Moteur de visualisation non disponible pour mise à jour opacité scène")
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur mise à jour opacité scène: {e}")
    
    def set_interest_center(self, center):
        """Délègue la définition du centre d'intérêt au moteur."""
        if self.visualization_engine:
            self.visualization_engine.set_interest_center(center)
    
    def update_interest_radius(self, radius):
        """Délègue la mise à jour du rayon d'intérêt au moteur."""
        if self.visualization_engine:
            self.visualization_engine.update_interest_radius(radius)
    
    def switch_to_2d_mode(self, plane_name="XY (Horizontal)"):
        """Délègue le basculement en mode 2D au moteur."""
        if self.visualization_engine:
            self.visualization_engine.switch_to_2d_mode(plane_name)
    
    def switch_to_3d_mode(self):
        """Délègue le basculement en mode 3D au moteur."""
        if self.visualization_engine:
            self.visualization_engine.switch_to_3d_mode()
    
    def apply_material_color(self, object_name, material_properties=None):
        """Applique une couleur de matériau à la scène."""
        if self.visualization_engine:
            # Déléguer au moteur de visualisation
            if hasattr(self.visualization_engine, 'apply_material_color'):
                # Extraire la couleur depuis les propriétés du matériau
                color = None
                if material_properties and isinstance(material_properties, dict):
                    # Utiliser la couleur spécifiée dans les propriétés
                    if 'color' in material_properties:
                        hex_color = material_properties['color']
                        if hex_color.startswith('#'):
                            # Convertir hex vers RGB
                            hex_color = hex_color[1:]  # Enlever le #
                            r = int(hex_color[0:2], 16) / 255.0
                            g = int(hex_color[2:4], 16) / 255.0  
                            b = int(hex_color[4:6], 16) / 255.0
                            color = [r, g, b]
                            logger.info(f"SceneViewer3DWidget: Couleur extraite {hex_color} -> {color}")
                    
                    material_name = material_properties.get('name', object_name)
                else:
                    material_name = str(material_properties) if material_properties else object_name
                
                # Appliquer la couleur au moteur
                self.visualization_engine.apply_material_color(material_name, color)
            else:
                logger.warning(f"SceneViewer3DWidget: apply_material_color non implémentée pour {object_name}")
    
    def enable_mesh_hover_highlight(self, enabled=True):
        """Active/désactive le surlignage au survol des meshes."""
        if self.visualization_engine:
            # Déléguer au moteur de visualisation
            if hasattr(self.visualization_engine, 'enable_mesh_hover_highlight'):
                self.visualization_engine.enable_mesh_hover_highlight(enabled)
            else:
                logger.debug(f"SceneViewer3DWidget: enable_mesh_hover_highlight({enabled}) - délégation silencieuse")
    
    def add_antenna_visualization(self, antenna):
        """
        Ajoute la visualisation d'une antenne à la scène.
        
        Args:
            antenna: Objet antenne à visualiser
        """
        try:
            if hasattr(self.visualization_engine, 'add_antenna_visualization'):
                self.visualization_engine.add_antenna_visualization(antenna)
                logger.info(f"SceneViewer3DWidget: Antenne {getattr(antenna, 'name', 'Inconnue')} ajoutée à la visualisation")
            else:
                logger.warning("SceneViewer3DWidget: Méthode add_antenna_visualization non disponible sur le moteur")
                
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur ajout antenne: {e}")
    
    def update_results_visualization(self, simulation_results, antennas, point_settings):
        """
        Met à jour la visualisation avec les résultats de simulation.
        
        Args:
            simulation_results: Dictionnaire contenant les résultats de simulation
            antennas: Liste des antennes de la simulation
            point_settings: Paramètres des points de simulation
        """
        try:
            if hasattr(self.visualization_engine, 'update_results_visualization'):
                self.visualization_engine.update_results_visualization(simulation_results, antennas, point_settings)
                logger.info("SceneViewer3DWidget: Résultats de simulation mis à jour dans la visualisation")
            else:
                logger.warning("SceneViewer3DWidget: Méthode update_results_visualization non disponible sur le moteur")
                
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur mise à jour résultats: {e}")
    
    def clear_scene(self):
        """
        Efface complètement la scène 3D.
        """
        try:
            if hasattr(self.visualization_engine, 'clear_scene'):
                self.visualization_engine.clear_scene()
                logger.info("SceneViewer3DWidget: Scène effacée")
            else:
                logger.warning("SceneViewer3DWidget: Méthode clear_scene non disponible sur le moteur")
                
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur effacement scène: {e}")
    
    def initialize_empty_scene(self):
        """
        Initialise une scène vide.
        """
        try:
            if hasattr(self.visualization_engine, 'initialize_empty_scene'):
                self.visualization_engine.initialize_empty_scene()
                logger.info("SceneViewer3DWidget: Scène vide initialisée")
            else:
                logger.warning("SceneViewer3DWidget: Méthode initialize_empty_scene non disponible sur le moteur")
                
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur initialisation scène vide: {e}")
    
    def clear_results(self):
        """
        Efface les résultats de simulation de la visualisation.
        """
        try:
            if hasattr(self.visualization_engine, 'clear_results'):
                self.visualization_engine.clear_results()
                logger.info("SceneViewer3DWidget: Résultats de simulation effacés")
            else:
                logger.warning("SceneViewer3DWidget: Méthode clear_results non disponible sur le moteur")
                
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur effacement résultats: {e}")
    
    def show_exit_fullscreen_button(self, visible):
        """
        Affiche ou masque le bouton de sortie du plein écran.
        
        Args:
            visible: True pour afficher, False pour masquer
        """
        try:
            if hasattr(self, 'exit_fullscreen_button'):
                self.exit_fullscreen_button.setVisible(visible)
                logger.debug(f"SceneViewer3DWidget: Bouton plein écran {'affiché' if visible else 'masqué'}")
            else:
                logger.warning("SceneViewer3DWidget: Bouton exit_fullscreen_button non trouvé")
                
        except Exception as e:
            logger.error(f"SceneViewer3DWidget: Erreur gestion bouton plein écran: {e}")
