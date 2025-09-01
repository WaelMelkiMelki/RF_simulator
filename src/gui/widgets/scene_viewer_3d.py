# src/gui/widgets/scene_viewer_3d.py
"""
Wrapper de compatibilité pour SceneViewer3D - NETDATA INNOVATION

TRANSITION vers architecture NETDATA :
- Maintient la compatibilité avec le code existant
- Délègue au nouveau VisualizationEngine (Infrastructure Layer)
- Fournit l'interface existante pendant la migration

NOUVELLE ARCHITECTURE CONFORME NETDATA :
- SceneViewer3DWidget (Presentation Layer) : Interface utilisateur PyQt6
- VisualizationEngine (Infrastructure Layer) : Moteur de rendu PyVista/VTK
"""
import logging
import numpy as np
import pyvista as pv
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame, QPushButton
from pyvistaqt import QtInteractor

from .visualization_engine import VisualizationEngine

logger = logging.getLogger(__name__)

class SceneViewer3D(VisualizationEngine):
    """
    Classe de compatibilité pour SceneViewer3D.
    
    DEPRECATED - Utiliser SceneViewer3DWidget + VisualizationEngine
    
    Cette classe maintient la compatibilité avec l'ancien code
    tout en déléguant au nouveau VisualizationEngine conforme NETDATA.
    """
    
    def __init__(self, parent=None):
        """Initialise le wrapper de compatibilité."""
        logger.warning("SceneViewer3D: Classe dépréciée. Utiliser SceneViewer3DWidget + VisualizationEngine")
        super().__init__(parent)
    
    # Méthodes de compatibilité - délèguent au moteur
    
    @staticmethod
    def get_friendly_name(technical_name):
        """Convertit un nom technique en nom convivial."""
        if not technical_name or not isinstance(technical_name, str):
            return "Objet Inconnu"
        
        object_mappings = {
            "Block_0/Block_0/Block_0/Block_0/Block_0": "Bâtiment 1",
            "Block_0/Block_0/Block_1/Block_0/Block_0": "Bâtiment 2", 
            "Block_0/Block_0/Block_2/Block_0/Block_0": "Bâtiment 3",
            "Block_0/Block_0/Block_3/Block_0/Block_0": "Bâtiment 4",
            "Block_0/Block_0/Block_4/Block_0/Block_0": "Bâtiment 5"
        }
        
        if technical_name in object_mappings:
            return object_mappings[technical_name]
        
        if "Block_" in technical_name:
            parts = technical_name.split("/")
            for part in reversed(parts):
                if part.startswith("Block_") and len(part) > 6:
                    try:
                        num = int(part.split("_")[1]) + 1
                        return f"Objet {num}"
                    except:
                        pass
        
        if len(technical_name) > 20:
            return f"Objet ({technical_name[:15]}...)"
        
        return technical_name
    
    def init_ui(self):
        """Compatibilité - déjà géré par VisualizationEngine."""
        pass
    
    def initialize_empty_scene(self):
        """Compatibilité - déjà géré par VisualizationEngine."""
        pass
    
    def setup_mouse_interactions(self):
        """Compatibilité - déjà géré par VisualizationEngine."""
        pass
    
    def on_mouse_move_vtk(self, obj, event):
        """Compatibilité - délègue au moteur."""
        self._on_mouse_move_vtk(obj, event)
    
    def on_right_click_vtk(self, obj, event):
        """Compatibilité - délègue au moteur."""
        self._on_right_click_vtk(obj, event)
    
    def _extract_point_from_picker(self, picker):
        """Compatibilité - utilise la méthode du moteur."""
        return super()._extract_point_from_picker(picker)
    
    def update_coordinate_display(self, x, y, z):
        """Méthode supprimée dans la nouvelle architecture."""
        pass
    
    def copy_coordinates_to_clipboard(self, x=None, y=None, z=None):
        """Méthode supprimée dans la nouvelle architecture."""
        pass
    
    def set_orthogonal_position(self, position, axis):
        """Compatibilité - fonctionnalité basique."""
        try:
            if axis == 'x':
                self.plotter.camera.position = (position, 0, 0)
            elif axis == 'y':
                self.plotter.camera.position = (0, position, 0)
            elif axis == 'z':
                self.plotter.camera.position = (0, 0, position)
            self.plotter.render()
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur position orthogonale: {e}")
    
    def show_scene(self, scene_or_mesh):
        """Compatibilité - affiche une scène ou un mesh."""
        try:
            if hasattr(scene_or_mesh, 'meshes'):
                # C'est un objet Scene
                self.update_scene(scene_or_mesh)
            else:
                # C'est probablement un mesh PyVista direct
                self.plotter.clear()
                self.plotter.add_axes()
                self.plotter.show_grid()
                
                actor = self.plotter.add_mesh(
                    scene_or_mesh,
                    opacity=0.8,
                    smooth_shading=True
                )
                
                self._scene_actors = [actor]
                self.plotter.reset_camera()
                
                logger.info("SceneViewer3D: Mesh direct affiché")
                
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur affichage: {e}")
    
    # Toutes les autres méthodes déjà implémentées dans VisualizationEngine
    # sont automatiquement disponibles via l'héritage
    # Signals existants
    mesh_selected = pyqtSignal(int)  # Émet l'index du mesh sélectionné
    right_click_position = pyqtSignal(float, float, float)
    # Nouveau signal
    mesh_hovered = pyqtSignal(str)  # Émet le nom du mesh survolé

    @staticmethod
    def get_friendly_name(technical_name):
        """Convertit un nom technique en nom convivial."""
        if not technical_name or not isinstance(technical_name, str):
            return "Objet Inconnu"
        
        # Mappings spécifiques pour les objets courants
        object_mappings = {
            "Block_0/Block_0/Block_0/Block_0/Block_0": "Bâtiment 1",
            "Block_0/Block_0/Block_1/Block_0/Block_0": "Bâtiment 2", 
            "Block_0/Block_0/Block_2/Block_0/Block_0": "Bâtiment 3",
            "Block_0/Block_0/Block_3/Block_0/Block_0": "Bâtiment 4",
            "Block_0/Block_0/Block_4/Block_0/Block_0": "Bâtiment 5"
        }
        
        # Si on a un mapping direct, l'utiliser
        if technical_name in object_mappings:
            return object_mappings[technical_name]
        
        # Sinon, essayer d'extraire un nom plus lisible
        # Chercher des patterns comme Block_X pour créer "Objet X"
        if "Block_" in technical_name:
            # Extraire le dernier numéro de Block_X
            parts = technical_name.split("/")
            for part in reversed(parts):
                if part.startswith("Block_") and len(part) > 6:
                    try:
                        num = int(part.split("_")[1]) + 1  # +1 pour commencer à 1 au lieu de 0
                        return f"Objet {num}"
                    except:
                        pass
        
        # Fallback : utiliser le nom technique mais raccourci
        if len(technical_name) > 20:
            return f"Objet ({technical_name[:15]}...)"
        
        return technical_name

    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialisation des attributs de la scène et des acteurs
        self.antenna_actors = []            # Liste des acteurs d'antennes (PyVista)
        self.mesh_actor = None              # Acteur principal du mesh affiché
        self._scene_actors = []             # Liste des acteurs de la scène (blocs, objets)
        self.object_actors = {}             # NOUVEAU: Dictionnaire des acteurs par nom d'objet
        self.antenna_coverage_actors = []   # Liste des acteurs de couverture (points de simulation)
        self.antenna_radius_actors = []     # Liste des acteurs de rayon d'antenne
        self.results_actor = None           # Acteur pour les résultats
        self.scalar_bar_actor = None        # Acteur pour la barre de couleur
        # NOUVEAU: Attributs pour la gestion des zones d'intérêt
        self.antenna_coverage_data = []     # Liste pour stocker les pv.PolyData des points de couverture
        self.interest_center = None         # Centre de la zone d'intérêt [x, y, z]
        self.interest_radius = 20.0         # Rayon de la zone d'intérêt en mètres
        self.zone_opacity_inside = 1.0      # Opacité à l'intérieur de la zone
        self.zone_opacity_outside = 0.1     # Opacité à l'extérieur de la zone
        self.is_2d_mode = False
        self.current_2d_plane = "XY (Horizontal)"
        self.cursor_actor_2d = None  # Acteur pour le curseur 2D
        # Nouveaux attributs pour la sélection
        self.current_selected_index = -1
        self.actor_colors = []
        self.highlight_color = [1, 0, 0]  # Rouge pour la surbrillance
        self.total_meshes = 0
        # NOUVEAU: Dictionnaire pour stocker les couleurs originales des acteurs
        self.actor_original_colors = {}  # Stockage externe des couleurs originales
        self.init_ui()
        # Ensure background is white at initialization
        if self.plotter:
            self.plotter.set_background('white')
        self.initialize_empty_scene()
        self.setup_mouse_interactions()

    def init_ui(self):
        """Initialise l'interface utilisateur du visualiseur 3D."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Créer le plotter PyVista
        self.plotter = QtInteractor(self)
        self.plotter.enable_parallel_projection()  # Pour une vue plus stable
        self.plotter.add_axes()  # Ajouter les axes
        self.plotter.show_grid()  # Afficher la grille
        self.plotter.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.plotter.setFocus()
        layout.addWidget(self.plotter)
        
        # Bouton de sortie du mode plein écran (initialement caché)
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
        button_container = QFrame(self)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.exit_fullscreen_button)
        button_layout.setContentsMargins(10, 10, 0, 0)
        button_container.setLayout(button_layout)
        layout.addWidget(button_container)
        layout.setAlignment(button_container, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        self.setLayout(layout)
        # Activer le focus pour capturer les événements clavier
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

    def setup_mouse_interactions(self):
        """Configure les interactions de la souris pour le suivi des coordonnées et le clic droit."""
        try:
            # Activer le suivi de la souris
            self.plotter.track_mouse_position = True
            
            # Utiliser les signaux Qt pour les événements de souris
            # CORRECTION: Utiliser l'API correcte pour PyVistaQt
            self.plotter.interactor.AddObserver('MouseMoveEvent', self.on_mouse_move_vtk)
            self.plotter.interactor.AddObserver('RightButtonPressEvent', self.on_right_click_vtk)
            
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la configuration des interactions souris: {e}")

    def on_mouse_move_vtk(self, obj, event):
        """Gère le mouvement de la souris via VTK."""
        try:
            # Obtenir les coordonnées 3D du point sous le curseur
            picker = self.plotter.pick_mouse_position()
            # CORRECTION: Gérer les différents formats de retour du picker
            point = self._extract_point_from_picker(picker)
            
            if point is not None and len(point) >= 3:
                x, y, z = point[0], point[1], point[2]
                self.update_coordinate_display(x, y, z)
        except Exception as e:
            logger.debug(f"SceneViewer3D: Erreur lors du suivi de la souris: {e}")

    def on_right_click_vtk(self, obj, event):
        """Gère les clics droits de la souris via VTK."""
        try:
            picker = self.plotter.pick_mouse_position()
            # CORRECTION: Gérer les différents formats de retour du picker
            point = self._extract_point_from_picker(picker)
            
            if point is not None and len(point) >= 3:
                x, y, z = point[0], point[1], point[2]
                # Émettre un signal avec les coordonnées
                self.right_click_position.emit(x, y, z)
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors du clic droit: {e}")

    def _extract_point_from_picker(self, picker):
        """
        Extrait les coordonnées 3D d'un objet picker, quel que soit son format.
        
        Args:
            picker: Objet retourné par self.plotter.pick_mouse_position()
            
        Returns:
            list or None: Coordonnées [x, y, z] ou None si non trouvées
        """
        try:
            # Si c'est un tuple, prendre le premier élément
            if isinstance(picker, tuple):
                if len(picker) > 0:
                    picker = picker[0]
                else:
                    return None
            
            # Si c'est un nombre (float), ce n'est pas un point valide
            if isinstance(picker, (int, float)):
                return None
                
            # Si c'est un objet avec un attribut 'point'
            if hasattr(picker, 'point'):
                point = picker.point
                # Vérifier que point est une séquence
                if hasattr(point, '__len__') and len(point) >= 3:
                    return point
                    
            # Si c'est directement un tableau numpy ou une liste
            if hasattr(picker, '__len__') and len(picker) >= 3:
                return picker
                
            # Si c'est un objet avec des attributs x, y, z
            if hasattr(picker, 'x') and hasattr(picker, 'y') and hasattr(picker, 'z'):
                return [picker.x, picker.y, picker.z]
                
        except Exception as e:
            logger.debug(f"SceneViewer3D: Erreur lors de l'extraction du point: {e}")
            
        return None

    def change_visualization_plane(self, plane_name):
        """Change le plan de visualisation."""
        try:
            logger.info(f"SceneViewer3D: Changement du plan de visualisation vers {plane_name}")
            # Mettre à jour la vue selon le plan sélectionné
            if plane_name == "XY (Horizontal)":
                self.plotter.view_xy()
            elif plane_name == "XZ (Vertical frontal)":
                self.plotter.view_xz()
            elif plane_name == "-XZ (Vertical arrière)":
                self.plotter.view_vector([-1, 0, 0])  # Regarder dans la direction -X
            elif plane_name == "YZ (Vertical latéral droit)":
                self.plotter.view_yz()
            elif plane_name == "-YZ (Vertical latéral gauche)":
                self.plotter.view_vector([0, -1, 0])  # Regarder dans la direction -Y
            elif plane_name == "ZX (Vertical frontal alternatif)":
                self.plotter.view_vector([0, 1, 0])  # Regarder dans la direction Y (plan ZX)
            elif plane_name == "-ZX (Vertical arrière alternatif)":
                self.plotter.view_vector([0, -1, 0])  # Regarder dans la direction -Y (plan -ZX)
            self.plotter.reset_camera()
            logger.info(f"SceneViewer3D: Plan de visualisation {plane_name} appliqué")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors du changement de plan: {e}")

    def set_orthogonal_position(self, position, axis):
        """
        Déplace la vue selon l'axe orthogonal au plan courant.
        Args:
            position (float): Position sur l'axe
            axis (str): Axe de déplacement ('X', 'Y', ou 'Z')
        """
        try:
            # Déplacer la caméra selon l'axe spécifié
            camera = self.plotter.camera
            camera_position = list(camera.position)
            focal_point = list(camera.focal_point)

            axis_index = {'X': 0, 'Y': 1, 'Z': 2}.get(axis.upper(), 2)

            # Déplacer la caméra et le point focal
            camera_position[axis_index] = position
            focal_point[axis_index] = position

            camera.position = camera_position
            camera.focal_point = focal_point

            self.plotter.render()
            logger.debug(f"SceneViewer3D: Position orthogonale {axis} mise à {position}")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors du déplacement orthogonal: {e}")

    def update_coordinate_display(self, x, y, z):
        """Met à jour l'affichage des coordonnées."""
        pass  # Méthode supprimée, plus d'affichage de coordonnées

    def copy_coordinates_to_clipboard(self, x=None, y=None, z=None):
        """Copie les coordonnées dans le presse-papiers."""
        pass  # Méthode supprimée, plus de copie de coordonnées

    def update_scene_bounds(self, bounds):
        """Met à jour les bornes de la scène."""
        try:
            if bounds and len(bounds) >= 6:
                # Stocker les bornes pour une utilisation ultérieure
                self.scene_bounds = bounds
                x_min, x_max, y_min, y_max, z_min, z_max = bounds
                logger.debug(f"SceneViewer3D: Bornes de la scène mises à jour: X[{x_min:.2f}, {x_max:.2f}], Y[{y_min:.2f}, {y_max:.2f}], Z[{z_min:.2f}, {z_max:.2f}]")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la mise à jour des bornes de la scène: {e}")

    def initialize_empty_scene(self):
        """Initialise la scène avec un contenu par défaut."""
        try:
            # CORRECTION: Texte en blanc pour être visible sur fond noir
            self.plotter.add_text("RF Simulator 3D - Chargez un fichier 3D", 
                                 position='upper_left', 
                                 font_size=14, 
                                 color='white')  # Blanc au lieu de noir
            # Réinitialiser la vue
            self.plotter.reset_camera()
            logger.info("SceneViewer3D: Scène vide initialisée")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de l'initialisation de la scène vide: {e}")

    def update_scene(self, scene):
        """Met à jour la scène 3D affichée."""
        try:
            # Stocker la référence à la scène pour les étiquettes
            self.scene = scene
            if self.plotter is None:
                logger.warning("SceneViewer3D: Plotter non initialisé")
                return
            
            # Effacer la scène précédente
            self.clear_scene()
            
            # NOUVEAU: Créer des acteurs séparés pour chaque mesh individuel
            if hasattr(scene, 'meshes') and scene.meshes:
                logger.info(f"SceneViewer3D: Création d'acteurs séparés pour {len(scene.meshes)} objets")
                
                # Dictionnaire pour stocker les acteurs par nom d'objet
                self.object_actors = {}
                total_points = 0
                
                for object_name, mesh in scene.meshes.items():
                    if mesh is not None and mesh.n_points > 0:
                        # Créer un acteur pour chaque objet
                        actor = self.plotter.add_mesh(
                            mesh,
                            name=object_name,  # Nom unique pour l'acteur
                            color=[0.7, 0.7, 0.7],  # Couleur par défaut grise
                            opacity=1.0,
                            smooth_shading=True,
                            specular=0.3,
                            diffuse=0.7,
                            ambient=0.1,
                            show_edges=False,  # NOUVEAU: Afficher les arêtes pour debug
                            reset_camera=False  # NOUVEAU: Ne pas réinitialiser la caméra pour chaque mesh
                        )
                        
                        # Stocker l'acteur dans notre dictionnaire
                        self.object_actors[object_name] = actor
                        self._scene_actors.append(actor)
                        total_points += mesh.n_points
                        logger.info(f"Acteur créé pour {object_name}: {mesh.n_points} points")
                
                logger.info(f"SceneViewer3D: {len(self.object_actors)} acteurs créés, total: {total_points} points")
                
                # NOUVEAU: Forcer le rendu pour s'assurer que les acteurs sont visibles
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
                    logger.info("Rendu forcé après création des acteurs")
                
            else:
                # Fallback: utiliser le mesh fusionné si pas d'objets individuels
                mesh = scene.get_pyvista_mesh()
                if mesh is not None:
                    # Appliquer une coloration différenciée selon le type de mesh
                    self._apply_differentiated_coloring(mesh)
                    logger.info(f"SceneViewer3D: Scène mise à jour avec {mesh.n_points} points (mesh fusionné)")
                else:
                    logger.warning("SceneViewer3D: Aucun mesh valide trouvé dans la scène")
                    # Afficher un message si aucun mesh n'est trouvé
                    self.plotter.add_text("Aucun mesh trouvé dans le fichier", 
                                         position='upper_left', 
                                         font_size=12, 
                                         color='red')  # Rouge vif
                    return
            
            # Centrer la caméra sur le mesh
            self.plotter.reset_camera()
            
            # NOUVEAU: Debug - vérifier que les acteurs sont bien présents
            active_actors = self.plotter.renderer.actors
            logger.info(f"DEBUG: Nombre d'acteurs actifs dans le renderer: {len(active_actors)}")
            for i, actor in enumerate(active_actors):
                try:
                    if hasattr(actor, 'GetBounds'):
                        bounds = actor.GetBounds()
                        logger.info(f"DEBUG: Acteur {i} - Bounds: {bounds}")
                    else:
                        logger.info(f"DEBUG: Acteur {i} - Pas de bounds (probablement texte)")
                except Exception as e:
                    logger.info(f"DEBUG: Acteur {i} - Erreur bounds: {e}")
            
            # Ajouter les étiquettes
            self.add_mesh_labels()
            
            # CORRECTION: Texte en vert clair pour être visible sur fond noir
            total_points = sum(mesh.n_points for mesh in scene.meshes.values()) if hasattr(scene, 'meshes') else (mesh.n_points if mesh else 0)
            self.plotter.add_text(f"Scène chargée: {total_points} points", 
                                 position='upper_left', 
                                 font_size=12, 
                                 color='lightgreen')  # Vert clair
                                 
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la mise à jour de la scène: {e}")
            import traceback
            traceback.print_exc()

    def _apply_differentiated_coloring_safe(self, mesh):
        """Applique une coloration différenciée de manière sécurisée."""
        try:
            self._apply_differentiated_coloring(mesh)
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la coloration différenciée: {e}")
            # Fallback: coloration uniforme
            try:
                self.mesh_actor = self.plotter.add_mesh(
                    mesh, 
                    color=[0.4, 0.7, 0.9],  # Bleu clair
                    opacity=1.0,
                    smooth_shading=True,
                    specular=0.3,
                    diffuse=0.7,
                    style='surface',
                    show_edges=False
                )
            except Exception as fallback_e:
                logger.error(f"SceneViewer3D: Erreur fallback coloration: {fallback_e}")

    def _apply_differentiated_coloring(self, mesh):
        """Applique une coloration différenciée selon les caractéristiques du mesh."""
        try:
            # Si c'est un MultiBlock, colorer chaque bloc différemment
            if isinstance(mesh, pv.MultiBlock):
                self._color_multiblock_scene(mesh)
            else:
                # Pour un mesh simple, utiliser une segmentation basée sur la géométrie
                self._color_simple_scene(mesh)
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la coloration différenciée: {e}")
            raise

    def _color_multiblock_scene(self, multiblock_mesh):
        """Colorer une scène MultiBlock avec stockage des couleurs."""
        color_palette = [
            [0.4, 0.6, 0.8],  # Bleu pastel
            [0.5, 0.8, 0.5],  # Vert pastel
            [0.8, 0.6, 0.4],  # Orange pastel
            [0.7, 0.5, 0.8],  # Violet pastel
            [0.4, 0.8, 0.8],  # Turquoise pastel
            [0.8, 0.8, 0.4],  # Jaune pastel
            [0.8, 0.4, 0.6],  # Rose pastel
            [0.6, 0.8, 0.6],  # Vert clair pastel
        ]
        self.actor_colors = []  # Réinitialiser les couleurs
        self._scene_actors = []  # Réinitialiser les acteurs
        for i in range(min(multiblock_mesh.n_blocks, len(color_palette))):
            try:
                block = multiblock_mesh[i]
                if isinstance(block, pv.PolyData) and block.n_points > 0:
                    color_index = i % len(color_palette)
                    color = color_palette[color_index]
                    actor = self.plotter.add_mesh(
                        block,
                        color=color,
                        opacity=1.0,
                        smooth_shading=True,
                        specular=0.2,
                        diffuse=0.8,
                        style='surface',
                        show_edges=False
                    )
                    self._scene_actors.append(actor)
                    self.actor_colors.append(color)  # Stocker la couleur originale
            except Exception as e:
                logger.warning(f"Erreur coloration bloc {i}: {e}")
                continue
        self.total_meshes = len(self._scene_actors)
        logger.info(f"{self.total_meshes} blocs colorés")

    def _color_simple_scene(self, mesh):
        """Colorier une scène simple et l'ajouter à la liste des acteurs."""
        try:
            if mesh.n_points > 5000:
                self._color_segmented_scene(mesh)
            else:
                self.mesh_actor = self.plotter.add_mesh(
                    mesh, 
                    color=[0.4, 0.7, 0.9],
                    opacity=1.0,
                    smooth_shading=True,
                    specular=0.3,
                    diffuse=0.7,
                    style='surface',
                    show_edges=False
                )
                # Ajouter à la liste des acteurs pour la sélection
                self._scene_actors = [self.mesh_actor]
                self.actor_colors = [[0.4, 0.7, 0.9]]  # Couleur originale
                self.total_meshes = 1
        except Exception as e:
            logger.error(f"Erreur coloration simple: {e}")
            # Fallback
            self.mesh_actor = self.plotter.add_mesh(
                mesh, 
                color=[0.4, 0.7, 0.9],
                opacity=1.0,
                smooth_shading=True,
                specular=0.3,
                diffuse=0.7,
                style='surface',
                show_edges=False
            )
            self._scene_actors = [self.mesh_actor]
            self.actor_colors = [[0.4, 0.7, 0.9]]
            self.total_meshes = 1

    def _color_segmented_scene(self, mesh):
        """Segmenter un gros mesh et appliquer des couleurs différentes."""
        try:
            # Utiliser les normales pour créer une coloration variée
            if hasattr(mesh, 'point_normals') and mesh.point_normals is not None and mesh.n_points > 0:
                # Créer une couleur basée sur les normales
                normals = mesh.point_normals
                # Normaliser les normales entre 0 et 1 pour créer des couleurs
                colors = (normals + 1) / 2
                mesh['normals_colors'] = colors
                self.mesh_actor = self.plotter.add_mesh(
                    mesh,
                    scalars='normals_colors',
                    opacity=1.0,
                    smooth_shading=True,
                    specular=0.3,
                    diffuse=0.7,
                    style='surface',
                    show_edges=False,
                    rgb=True  # Utiliser les valeurs RGB directement
                )
            else:
                # Fallback: segmentation par hauteur
                self._color_by_height(mesh)
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la segmentation: {e}")
            # Dernier fallback
            self.mesh_actor = self.plotter.add_mesh(
                mesh, 
                color=[0.4, 0.7, 0.9],
                opacity=1.0,
                smooth_shading=True,
                specular=0.3,
                diffuse=0.7,
                style='surface',
                show_edges=False
            )

    def _color_by_height(self, mesh):
        """Colorer un mesh selon la hauteur (coordonnée Z)."""
        try:
            # Obtenir les coordonnées Z
            z_coords = mesh.points[:, 2]
            z_min, z_max = np.min(z_coords), np.max(z_coords)
            # Normaliser entre 0 et 1
            normalized_heights = (z_coords - z_min) / (z_max - z_min)
            # Appliquer comme scalaires
            mesh['height'] = normalized_heights
            # Utiliser une colormap pour la hauteur
            self.mesh_actor = self.plotter.add_mesh(
                mesh,
                scalars='height',
                cmap='terrain',  # Colormap qui va du vert (bas) au marron (haut)
                opacity=1.0,
                smooth_shading=True,
                specular=0.3,
                diffuse=0.7,
                style='surface',
                show_edges=False,
                scalar_bar_args={'title': 'Altitude'}
            )
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la coloration par hauteur: {e}")
            # Fallback
            self.mesh_actor = self.plotter.add_mesh(
                mesh, 
                color=[0.4, 0.7, 0.9],
                opacity=1.0,
                smooth_shading=True,
                specular=0.3,
                diffuse=0.7,
                style='surface',
                show_edges=False
            )

    def clear_scene(self):
        """Efface tous les éléments de la scène."""
        try:
            # Supprimer tous les acteurs
            if self.mesh_actor:
                self.plotter.remove_actor(self.mesh_actor)
                self.mesh_actor = None
                
            # NOUVEAU: Nettoyer les acteurs d'objets individuels
            if hasattr(self, 'object_actors'):
                for object_name, actor in self.object_actors.items():
                    try:
                        self.plotter.remove_actor(actor)
                    except Exception:
                        pass
                self.object_actors.clear()
                
            for actor in self._scene_actors:
                try:
                    self.plotter.remove_actor(actor)
                except Exception:
                    pass
            self._scene_actors.clear()
            for actor in self.antenna_actors:
                try:
                    self.plotter.remove_actor(actor)
                except Exception:
                    pass
            self.antenna_actors.clear()
            for actor in self.antenna_radius_actors:
                try:
                    self.plotter.remove_actor(actor)
                except Exception:
                    pass
            self.antenna_radius_actors.clear()
            for actor in self.antenna_coverage_actors:
                try:
                    self.plotter.remove_actor(actor)
                except Exception:
                    pass
            self.antenna_coverage_actors.clear()
            if self.results_actor:
                try:
                    self.plotter.remove_actor(self.results_actor)
                except Exception:
                    pass
                self.results_actor = None
            if self.scalar_bar_actor:
                try:
                    self.plotter.remove_actor(self.scalar_bar_actor)
                except Exception:
                    pass
                self.scalar_bar_actor = None
            
            # CORRECTION: Ne pas utiliser clear() qui efface tout, retirer les acteurs individuellement
            # try:
            #     self.plotter.clear()  # Efface tous les éléments de la scène
            # except Exception:
            #     pass
            
            # Always set background to white after clearing
            try:
                self.plotter.set_background('white')
            except Exception:
                pass
            try:
                self.plotter.add_axes()
                self.plotter.show_grid()
            except Exception:
                pass
            # Réinitialiser la sélection
            self.current_selected_index = -1
            self.actor_colors = []
            self.total_meshes = 0
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de l'effacement de la scène: {e}")

    def add_antenna_visualization(self, antenna):
        """Ajoute la visualisation d'une antenne dans la scène 3D."""
        try:
            if self.plotter is None:
                logger.warning("SceneViewer3D: Plotter non initialisé pour l'antenne")
                return
            # Créer une représentation 3D de l'antenne (cylindre)
            position = antenna.position
            cylinder = pv.Cylinder(
                center=position,
                direction=[0, 0, 1],
                radius=0.1,
                height=0.5
            )
            # Couleur différente selon le type d'antenne
            color = 'red' if hasattr(antenna, 'ssid') else 'yellow'  # Jaune pour 5G pour contraste
            # Ajouter l'antenne à la scène
            actor = self.plotter.add_mesh(
                cylinder, 
                color=color, 
                opacity=0.9,
                smooth_shading=True
            )
            self.antenna_actors.append(actor)
            # Ajouter un label
            try:
                self.plotter.add_point_labels(
                    [position], 
                    [antenna.name], 
                    point_size=0,
                    font_size=10,
                    text_color='white'
                )
            except Exception as label_e:
                logger.warning(f"SceneViewer3D: Impossible d'ajouter le label pour {antenna.name}: {label_e}")
            logger.info(f"SceneViewer3D: Antenne '{antenna.name}' ajoutée à la visualisation")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de l'ajout de l'antenne: {e}")

    def update_results_visualization(self, results, antennas=None, point_settings=None):
        """Met à jour la visualisation avec les résultats de simulation."""
        try:
            if self.plotter is None:
                logger.warning("SceneViewer3D: Plotter non initialisé pour les résultats")
                return
            # Effacer les résultats précédents
            self.clear_results()
            logger.debug(f"update_results_visualization: Type de résultats = {type(results)}")
            if isinstance(results, dict):
                logger.debug(f"update_results_visualization: Clés des résultats = {list(results.keys())}")
            # Visualiser les résultats comme des points de couverture colorés
            if isinstance(results, dict):
                self._visualize_coverage_points(results, antennas)
            logger.info("SceneViewer3D: Visualisation des résultats mise à jour")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la mise à jour des résultats: {e}")
            import traceback
            traceback.print_exc()

    def _visualize_coverage_points(self, results_dict, antennas=None):
        """Visualise les résultats comme des points de couverture colorés selon la puissance."""
        try:
            logger.debug(f"[COVERAGE] Début visualisation points: {len(results_dict)} clés de résultats")
            logger.debug(f"[COVERAGE] Clés des résultats: {list(results_dict.keys())}")
            
            # Vérifier si les résultats sont au format direct (points/values) ou par antenne
            if 'points' in results_dict and 'values' in results_dict:
                # Format direct: points et values au niveau racine
                points = np.array(results_dict['points'])
                values = np.array(results_dict['values'])
                logger.debug(f"[COVERAGE] Format direct: {len(points)} points, {len(values)} valeurs")
            else:
                # Format par antenne: collecter tous les points et valeurs
                all_points = []
                all_values = []
                for ant_name, ant_data in results_dict.items():
                    logger.debug(f"[COVERAGE] Antenne '{ant_name}' - type: {type(ant_data)}")
                    if isinstance(ant_data, dict) and 'points' in ant_data and 'values' in ant_data:
                        points = np.array(ant_data['points'])
                        values = np.array(ant_data['values'])
                        logger.debug(f"[COVERAGE] '{ant_name}': {len(points)} points, {len(values)} valeurs")
                        if len(points) > 0 and len(values) > 0:
                            all_points.extend(points)
                            all_values.extend(values)
                            logger.debug(f"[COVERAGE] '{ant_name}': points et valeurs ajoutés")
                        else:
                            logger.warning(f"[COVERAGE] '{ant_name}': points ou valeurs vides")
                    else:
                        logger.warning(f"[COVERAGE] '{ant_name}': données invalides ({type(ant_data)}), clés: {list(ant_data.keys()) if isinstance(ant_data, dict) else 'N/A'}")
                
                # Si nous avons des points, les utiliser
                if len(all_points) > 0 and len(all_values) > 0:
                    points = np.array(all_points)
                    values = np.array(all_values)
                    logger.debug(f"[COVERAGE] Total: {len(points)} points, {len(values)} valeurs")
                else:
                    logger.warning("SceneViewer3D: Aucun point de couverture à visualiser")
                    return
            
            # Si nous avons des points, les visualiser
            if len(points) > 0 and len(values) > 0:
                logger.debug(f"[COVERAGE] Plage des valeurs: Min={np.min(values):.2f}dBm, Max={np.max(values):.2f}dBm")
                
                # Créer un nuage de points PyVista
                point_cloud = pv.PolyData(points)
                point_cloud['signal_strength'] = values
                
                # CORRECTION: Ajouter le maillage avec des paramètres qui permettent le contrôle interactif
                coverage_actor = self.plotter.add_mesh(
                    point_cloud,
                    scalars='signal_strength',
                    cmap='viridis',  # Colormap du violet (faible) au jaune (fort)
                    render_points_as_spheres=True,
                    smooth_shading=True,
                    scalar_bar_args={
                        'title': 'Puissance reçue (dBm)\n[Émission: +30dBm - Pertes]',
                        'vertical': True,
                        'position_x': 0.85,
                        'position_y': 0.1
                    }
                )
                self.antenna_coverage_actors.append(coverage_actor)
                
                # NOUVEAU: Stocker les données des points pour un accès futur
                self.antenna_coverage_data.append(point_cloud)
                
                logger.info(f"SceneViewer3D: {len(points)} points de couverture créés")
            else:
                logger.warning("SceneViewer3D: Aucun point de couverture à visualiser")
                
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la visualisation des points de couverture: {e}")
            import traceback
            traceback.print_exc()

    def clear_results(self):
        """Efface uniquement les résultats de simulation."""
        try:
            # Effacer les couvertures précédentes
            for actor in self.antenna_coverage_actors:
                try:
                    self.plotter.remove_actor(actor)
                except Exception:
                    pass
            self.antenna_coverage_actors.clear()
            
            # NOUVEAU: Effacer les données des points
            self.antenna_coverage_data.clear()
            
            # Effacer les résultats heatmap
            if self.results_actor:
                try:
                    self.plotter.remove_actor(self.results_actor)
                except Exception:
                    pass
                self.results_actor = None
            # Effacer la barre de couleur
            if self.scalar_bar_actor:
                try:
                    self.plotter.remove_actor(self.scalar_bar_actor)
                except Exception:
                    pass
                self.scalar_bar_actor = None
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de l'effacement des résultats: {e}")

    def show_exit_fullscreen_button(self, show):
        """Affiche ou masque le bouton de sortie du plein écran."""
        if self.exit_fullscreen_button:
            self.exit_fullscreen_button.setVisible(show)

    def exit_fullscreen_mode(self):
        """Signal pour sortir du mode plein écran."""
        # Cette méthode devrait être connectée à la MainWindow
        logger.info("SceneViewer3D: Demande de sortie du mode plein écran")
        # Dans une vraie implémentation, on enverrait un signal

    def resizeEvent(self, event):
        """Gère le redimensionnement du widget."""
        super().resizeEvent(event)
        if self.plotter:
            self.plotter.resize(1, 1)  # Forcer le redimensionnement
            self.plotter.resize(event.size().width(), event.size().height())

    def closeEvent(self, event):
        """Gère la fermeture du widget."""
        try:
            if self.plotter:
                self.plotter.close()
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la fermeture: {e}")
        finally:
            event.accept()

    # CORRECTION: Ajout des méthodes manquantes pour le contrôle des points
    def update_point_opacity(self, opacity):
        """Met à jour l'opacité des points de couverture."""
        try:
            for actor in self.antenna_coverage_actors:
                try:
                    actor.GetProperty().SetOpacity(opacity)
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de l'opacité: {e}")
            self.plotter.render()
            logger.debug(f"SceneViewer3D: Opacité des points mise à jour à {opacity}")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur globale lors de la mise à jour de l'opacité: {e}")

    def update_point_density(self, size):
        """Met à jour la taille des points de couverture."""
        try:
            for actor in self.antenna_coverage_actors:
                try:
                    actor.GetProperty().SetPointSize(size)
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de la taille des points: {e}")
            self.plotter.render()
            logger.debug(f"SceneViewer3D: Taille des points mise à jour à {size}")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur globale lors de la mise à jour de la taille des points: {e}")

    # NOUVEAU: Ajout de la méthode pour contrôler l'opacité de la scène 3D
    def update_scene_opacity(self, opacity):
        """Met à jour l'opacité de la scène 3D (modèle environnemental)."""
        try:
            # Mettre à jour l'opacité de l'acteur principal du mesh
            if self.mesh_actor:
                try:
                    self.mesh_actor.GetProperty().SetOpacity(opacity)
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de l'opacité du mesh principal: {e}")
            
            # Mettre à jour l'opacité de tous les acteurs de la scène
            for actor in self._scene_actors:
                try:
                    actor.GetProperty().SetOpacity(opacity)
                except Exception as e:
                    logger.error(f"Erreur lors de la mise à jour de l'opacité d'un acteur de scène: {e}")
            
            self.plotter.render()
            logger.debug(f"SceneViewer3D: Opacité de la scène mise à jour à {opacity}")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur globale lors de la mise à jour de l'opacité de la scène: {e}")

    # NOUVEAU: Ajout des méthodes pour la gestion des zones d'intérêt
    def set_interest_center(self, center):
        """Définit le centre de la zone d'intérêt."""
        self.interest_center = center
        logger.info(f"SceneViewer3D: Centre de la zone d'intérêt mis à jour: {center}")
        # Appliquer immédiatement
        self.apply_zone_opacity()

    def update_interest_radius(self, radius):
        """Met à jour le rayon de la zone d'intérêt."""
        self.interest_radius = radius
        logger.info(f"SceneViewer3D: Rayon de la zone d'intérêt mis à jour: {radius}m")
        # Appliquer immédiatement
        self.apply_zone_opacity()

    def update_zone_opacity_inside(self, opacity):
        """Met à jour l'opacité à l'intérieur de la zone."""
        self.zone_opacity_inside = opacity
        logger.debug(f"SceneViewer3D: Opacité intérieure de la zone mise à jour à {opacity:.2f}")
        # Appliquer immédiatement
        self.apply_zone_opacity()

    def update_zone_opacity_outside(self, opacity):
        """Met à jour l'opacité à l'extérieur de la zone."""
        self.zone_opacity_outside = opacity
        logger.debug(f"SceneViewer3D: Opacité extérieure de la zone mise à jour à {opacity:.2f}")
        # Appliquer immédiatement
        self.apply_zone_opacity()

    def apply_zone_opacity(self):
        """
        Applique les opacités internes/externes en fonction de la zone d'intérêt définie.
        Utilise self.interest_center, self.interest_radius, self.zone_opacity_inside, self.zone_opacity_outside.
        """
        try:
            # Vérifier qu'il y a des données et une zone définie
            if not self.antenna_coverage_data or not self.antenna_coverage_actors:
                logger.debug("SceneViewer3D: Aucune donnée de couverture ou acteur pour appliquer l'opacité par zone.")
                return

            if self.interest_center is None:
                logger.debug("SceneViewer3D: Aucun centre d'intérêt défini. Appliquer opacité globale.")
                # Si pas de centre, appliquer une opacité uniforme (ex: celle de 'intérieur')
                for actor in self.antenna_coverage_actors:
                    actor.GetProperty().SetOpacity(self.zone_opacity_inside)
                self.plotter.render()
                return

            center = np.array(self.interest_center)
            radius_sq = self.interest_radius ** 2  # Utiliser le carré pour éviter sqrt

            # Parcourir les jeux de données et les acteurs correspondants
            for polydata, actor in zip(self.antenna_coverage_data, self.antenna_coverage_actors):
                try:
                    # Récupérer les points
                    points = polydata.points  # Shape (N, 3)
                    if points.size == 0:
                        continue

                    # Calculer les distances au carré (plus rapide)
                    # Broadcasting: (N, 3) - (3,) -> (N, 3) -> sum(axis=1) -> (N,)
                    distances_sq = np.sum((points - center) ** 2, axis=1)
                    
                    # Créer un tableau d'opacités
                    opacities = np.full(points.shape[0], self.zone_opacity_outside)  # Par défaut, extérieur
                    # Masque pour les points intérieurs
                    inside_mask = distances_sq <= radius_sq
                    opacities[inside_mask] = self.zone_opacity_inside

                    # Appliquer les nouvelles opacités
                    # PyVista ne permet pas directement de définir une opacité par point de manière simple.
                    # La solution la plus directe est de recréer le maillage avec les nouvelles opacités.
                    # Cependant, pour éviter de tout recréer, on peut utiliser des scalaires d'opacité.
                    # Mais PyVista n'a pas de mécanisme direct pour cela non plus.
                    # La solution la plus robuste est de supprimer et recréer le maillage.
                    # Pour simplifier ici, on applique l'opacité moyenne ou une logique globale.
                    # Pour une solution précise, il faut recréer le point_cloud avec des couleurs RGBA ou 
                    # utiliser une approche plus avancée (non triviale).
                    
                    # APPROCHE SIMPLIFIÉE pour le MVP :
                    # Comme PyVista ne gère pas facilement l'opacité par point, 
                    # on va appliquer une opacité globale basée sur le ratio de points intérieurs/extérieurs.
                    # Ce n'est pas parfait mais fonctionnel.
                    
                    num_inside = np.sum(inside_mask)
                    num_total = len(inside_mask)
                    
                    if num_total > 0:
                        # Calculer une opacité moyenne pondérée
                        avg_opacity = (num_inside * self.zone_opacity_inside + (num_total - num_inside) * self.zone_opacity_outside) / num_total
                        actor.GetProperty().SetOpacity(avg_opacity)
                        logger.debug(f"SceneViewer3D: Acteur mis à jour avec opacité moyenne {avg_opacity:.2f} (Int: {num_inside}/{num_total} pts)")
                    else:
                         actor.GetProperty().SetOpacity(self.zone_opacity_outside)
                         
                except Exception as e:
                    logger.error(f"SceneViewer3D: Erreur lors du traitement d'un jeu de données: {e}")
                    # En cas d'erreur, appliquer l'opacité extérieure par défaut
                    actor.GetProperty().SetOpacity(self.zone_opacity_outside)

            self.plotter.render()
            logger.info("SceneViewer3D: Opacités par zone appliquées (approche simplifiée).")

        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur globale lors de l'application de l'opacité par zone: {e}")

    def update_2d_heatmap_visualization(self, results, plane_name):
        """
        Met à jour la visualisation avec une heatmap 2D sur le plan spécifié.
        Args:
            results (dict): Résultats de simulation au format 2D.
            plane_name (str): Nom du plan de visualisation.
        """
        try:
            if self.plotter is None:
                logger.warning("SceneViewer3D: Plotter non initialisé pour la heatmap 2D")
                return
            self.clear_results()
            logger.debug(f"update_2d_heatmap_visualization: Type de résultats = {type(results)}")
            if isinstance(results, dict):
                logger.debug(f"update_2d_heatmap_visualization: Clés des résultats = {list(results.keys())}")
            if isinstance(results, dict):
                self._visualize_2d_heatmap(results, plane_name)
            logger.info("SceneViewer3D: Visualisation de la heatmap 2D mise à jour")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la mise à jour de la heatmap 2D: {e}")
            import traceback
            traceback.print_exc()

    def _visualize_2d_heatmap(self, results_dict, plane_name):
        """Visualise les résultats comme une heatmap 2D sur le plan spécifié."""
        try:
            logger.debug(f"[HEATMAP_2D] Début visualisation heatmap 2D sur le plan {plane_name}")
            logger.debug(f"[HEATMAP_2D] Clés des résultats: {list(results_dict.keys())}")
            if 'X' in results_dict and 'Y' in results_dict and 'values' in results_dict:
                X = np.array(results_dict['X'])
                Y = np.array(results_dict['Y'])
                values = np.array(results_dict['values'])
                logger.debug(f"[HEATMAP_2D] Format direct: {len(X)} x {len(Y)} points, {len(values)} valeurs")
            else:
                all_X = []
                all_Y = []
                all_values = []
                for ant_name, ant_data in results_dict.items():
                    logger.debug(f"[HEATMAP_2D] Antenne '{ant_name}' - type: {type(ant_data)}")
                    if isinstance(ant_data, dict) and 'X' in ant_data and 'Y' in ant_data and 'values' in ant_data:
                        X = np.array(ant_data['X'])
                        Y = np.array(ant_data['Y'])
                        values = np.array(ant_data['values'])
                        logger.debug(f"[HEATMAP_2D] '{ant_name}': {len(X)} x {len(Y)} points, {len(values)} valeurs")
                        if len(X) > 0 and len(Y) > 0 and len(values) > 0:
                            all_X.extend(X)
                            all_Y.extend(Y)
                            all_values.extend(values)
                            logger.debug(f"[HEATMAP_2D] '{ant_name}': points et valeurs ajoutés")
                        else:
                            logger.warning(f"[HEATMAP_2D] '{ant_name}': points ou valeurs vides")
                    else:
                        logger.warning(f"[HEATMAP_2D] '{ant_name}': données invalides ({type(ant_data)}), clés: {list(ant_data.keys()) if isinstance(ant_data, dict) else 'N/A'}")
                if len(all_X) > 0 and len(all_Y) > 0 and len(all_values) > 0:
                    X = np.array(all_X)
                    Y = np.array(all_Y)
                    values = np.array(all_values)
                    logger.debug(f"[HEATMAP_2D] Total: {len(X)} x {len(Y)} points, {len(values)} valeurs")
                else:
                    logger.warning("SceneViewer3D: Aucun point de heatmap 2D à visualiser")
                    return
            if len(X) > 0 and len(Y) > 0 and len(values) > 0:
                logger.debug(f"[HEATMAP_2D] Plage des valeurs: Min={np.min(values):.2f}dBm, Max={np.max(values):.2f}dBm")
                if plane_name == "XY (Horizontal)":
                    points_3d = np.column_stack([X, Y, np.zeros_like(X)])
                elif plane_name == "XZ (Vertical frontal)":
                    points_3d = np.column_stack([X, np.zeros_like(X), Y])
                elif plane_name == "-XZ (Vertical arrière)":
                    points_3d = np.column_stack([X, np.zeros_like(X), -Y])
                elif plane_name == "YZ (Vertical latéral droit)":
                    points_3d = np.column_stack([np.zeros_like(X), X, Y])
                elif plane_name == "-YZ (Vertical latéral gauche)":
                    points_3d = np.column_stack([np.zeros_like(X), -X, Y])
                elif plane_name == "ZX (Vertical frontal alternatif)":
                    points_3d = np.column_stack([Y, np.zeros_like(X), X])
                elif plane_name == "-ZX (Vertical arrière alternatif)":
                    points_3d = np.column_stack([Y, np.zeros_like(X), -X])
                else:
                    points_3d = np.column_stack([X, Y, np.zeros_like(X)])
                point_cloud = pv.PolyData(points_3d)
                point_cloud['signal_strength'] = values
                heatmap_actor = self.plotter.add_mesh(
                    point_cloud,
                    scalars='signal_strength',
                    cmap='viridis',
                    render_points_as_spheres=True,
                    smooth_shading=True,
                    scalar_bar_args={
                        'title': 'Puissance reçue (dBm)\n[Émission: +30dBm - Pertes]',
                        'vertical': True,
                        'position_x': 0.85,
                        'position_y': 0.1
                    }
                )
                self.antenna_coverage_actors.append(heatmap_actor)
                logger.info(f"SceneViewer3D: Heatmap 2D créée avec {len(points_3d)} points")
            else:
                logger.warning("SceneViewer3D: Aucun point de heatmap 2D à visualiser")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la visualisation de la heatmap 2D: {e}")
            import traceback
            traceback.print_exc()

    def switch_to_2d_mode(self, plane_name="XY (Horizontal)"):
        """Bascule en mode de visualisation 2D."""
        try:
            logger.info(f"SceneViewer3D: Passage en mode 2D sur le plan {plane_name}")
            self.is_2d_mode = True
            self.current_2d_plane = plane_name
            self.clear_scene()
            self.setup_2d_view(plane_name)
            self.show_cursor_2d()
            logger.info("SceneViewer3D: Mode 2D activé")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors du passage en mode 2D: {e}")

    def switch_to_3d_mode(self):
        """Bascule en mode de visualisation 3D."""
        try:
            logger.info("SceneViewer3D: Passage en mode 3D")
            self.is_2d_mode = False
            self.current_2d_plane = "XY (Horizontal)"
            self.hide_cursor_2d()
            self.plotter.reset_camera()
            logger.info("SceneViewer3D: Mode 3D activé")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors du passage en mode 3D: {e}")

    def setup_2d_view(self, plane_name):
        """Configure la vue 2D pour le plan spécifié."""
        try:
            if plane_name == "XY (Horizontal)":
                self.plotter.view_xy()
            elif plane_name == "XZ (Vertical frontal)":
                self.plotter.view_xz()
            elif plane_name == "-XZ (Vertical arrière)":
                self.plotter.view_vector([-1, 0, 0])
            elif plane_name == "YZ (Vertical latéral droit)":
                self.plotter.view_yz()
            elif plane_name == "-YZ (Vertical latéral gauche)":
                self.plotter.view_vector([0, -1, 0])
            elif plane_name == "ZX (Vertical frontal alternatif)":
                self.plotter.view_vector([0, 1, 0])
            elif plane_name == "-ZX (Vertical arrière alternatif)":
                self.plotter.view_vector([0, -1, 0])
            self.plotter.reset_camera()
            logger.info(f"SceneViewer3D: Vue 2D {plane_name} configurée")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la configuration de la vue 2D: {e}")

    def show_cursor_2d(self):
        """Affiche le curseur 2D."""
        try:
            cursor_point = pv.PolyData([[0, 0, 0]])
            if self.cursor_actor_2d:
                self.plotter.remove_actor(self.cursor_actor_2d)
            self.cursor_actor_2d = self.plotter.add_mesh(
                cursor_point,
                color='red',
                point_size=10,
                render_points_as_spheres=True
            )
            logger.info("SceneViewer3D: Curseur 2D affiché")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de l'affichage du curseur 2D: {e}")

    def hide_cursor_2d(self):
        """Masque le curseur 2D."""
        try:
            if self.cursor_actor_2d:
                self.plotter.remove_actor(self.cursor_actor_2d)
                self.cursor_actor_2d = None
            logger.info("SceneViewer3D: Curseur 2D masqué")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors du masquage du curseur 2D: {e}")

    def move_cursor_2d(self, position):
        """
        Déplace le curseur 2D selon la position sur l'axe orthogonal au plan.
        Args:
            position (float): Position sur l'axe orthogonal au plan.
        """
        try:
            cursor_coords = self._get_cursor_coords_for_plane(position)
            if self.cursor_actor_2d:
                self.plotter.remove_actor(self.cursor_actor_2d)
            cursor_point = pv.PolyData([cursor_coords])
            self.cursor_actor_2d = self.plotter.add_mesh(
                cursor_point,
                color='red',
                point_size=10,
                render_points_as_spheres=True
            )
            projected_coords = self._project_cursor_on_plane(cursor_coords)
            if projected_coords is not None:
                self.update_heatmap_at_point(projected_coords)
            logger.debug(f"SceneViewer3D: Curseur 2D déplacé à {cursor_coords}")
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors du déplacement du curseur 2D: {e}")

    def _get_cursor_coords_for_plane(self, position):
        """
        Calcule les coordonnées 3D du curseur selon la position sur l'axe orthogonal au plan.
        Args:
            position (float): Position sur l'axe orthogonal au plan.
        Returns:
            list: Coordonnées [x, y, z] du curseur.
        """
        if self.current_2d_plane == "XY (Horizontal)":
            return [0, 0, position]
        elif self.current_2d_plane == "XZ (Vertical frontal)":
            return [0, position, 0]
        elif self.current_2d_plane == "-XZ (Vertical arrière)":
            return [0, position, 0]
        elif self.current_2d_plane == "YZ (Vertical latéral droit)":
            return [position, 0, 0]
        elif self.current_2d_plane == "-YZ (Vertical latéral gauche)":
            return [position, 0, 0]
        elif self.current_2d_plane == "ZX (Vertical frontal alternatif)":
            return [0, position, 0]
        elif self.current_2d_plane == "-ZX (Vertical arrière alternatif)":
            return [0, position, 0]
        else:
            return [0, 0, position]

    def _project_cursor_on_plane(self, cursor_coords):
        """
        Projette le curseur sur le plan de visualisation.
        Args:
            cursor_coords (list): Coordonnées [x, y, z] du curseur.
        Returns:
            list or None: Coordonnées projetées sur le plan, ou None si erreur.
        """
        try:
            if self.current_2d_plane == "XY (Horizontal)":
                return [cursor_coords[0], cursor_coords[1], 0]
            elif self.current_2d_plane == "XZ (Vertical frontal)":
                return [cursor_coords[0], 0, cursor_coords[2]]
            elif self.current_2d_plane == "-XZ (Vertical arrière)":
                return [cursor_coords[0], 0, cursor_coords[2]]
            elif self.current_2d_plane == "YZ (Vertical latéral droit)":
                return [0, cursor_coords[1], cursor_coords[2]]
            elif self.current_2d_plane == "-YZ (Vertical latéral gauche)":
                return [0, cursor_coords[1], cursor_coords[2]]
            elif self.current_2d_plane == "ZX (Vertical frontal alternatif)":
                return [cursor_coords[0], 0, cursor_coords[2]]
            elif self.current_2d_plane == "-ZX (Vertical arrière alternatif)":
                return [cursor_coords[0], 0, cursor_coords[2]]
            else:
                return [cursor_coords[0], cursor_coords[1], 0]
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la projection du curseur: {e}")
            return None

    def update_heatmap_at_point(self, point):
        """
        Met à jour la heatmap pour le point spécifié.
        Args:
            point (list): Coordonnées [x, y, z] du point d'intérêt.
        """
        try:
            logger.info(f"SceneViewer3D: Mise à jour de la heatmap au point {point}")
            self.plotter.add_text(
                f"Point d'intérêt: ({point[0]:.1f}, {point[1]:.1f}, {point[2]:.1f})",
                position='upper_right',
                font_size=10,
                color='red'
            )
        except Exception as e:
            logger.error(f"SceneViewer3D: Erreur lors de la mise à jour de la heatmap: {e}")

    def keyPressEvent(self, event):
        """Gère les presses de touches pour la navigation."""
        key = event.key()
        if key == Qt.Key.Key_Right:
            self.select_next_mesh()
        elif key == Qt.Key.Key_Left:
            self.select_previous_mesh()
        else:
            super().keyPressEvent(event)

    def select_next_mesh(self):
        """Sélectionne le mesh suivant dans la liste."""
        if self.total_meshes == 0:
            return
        new_index = self.current_selected_index + 1
        if new_index >= self.total_meshes:
            new_index = 0  # Boucler au début
        self.highlight_mesh(new_index)

    def select_previous_mesh(self):
        """Sélectionne le mesh précédent dans la liste."""
        if self.total_meshes == 0:
            return
        new_index = self.current_selected_index - 1
        if new_index < 0:
            new_index = self.total_meshes - 1  # Boucler à la fin
        self.highlight_mesh(new_index)

    def highlight_mesh(self, index):
        """Met en évidence le mesh sélectionné."""
        # Réinitialiser la couleur de l'acteur précédent
        if self.current_selected_index >= 0 and self.current_selected_index < self.total_meshes:
            previous_actor = self._scene_actors[self.current_selected_index]
            previous_color = self.actor_colors[self.current_selected_index]
            previous_actor.GetProperty().SetColor(previous_color)
        # Mettre en évidence le nouvel acteur
        if index >= 0 and index < self.total_meshes:
            actor = self._scene_actors[index]
            actor.GetProperty().SetColor(self.highlight_color)
            self.current_selected_index = index
            self.plotter.render()
            # Émettre un signal avec l'index du mesh sélectionné
            self.mesh_selected.emit(index)
            logger.info(f"Mesh {index} sélectionné")

    def highlight_mesh_by_name(self, mesh_name):
        """Met en évidence un mesh spécifique par son nom."""
        try:
            # Trouver l'index du mesh par son nom
            if hasattr(self, 'scene') and hasattr(self.scene, 'meshes'):
                mesh_names = list(self.scene.meshes.keys())
                if mesh_name in mesh_names:
                    index = mesh_names.index(mesh_name)
                    self.highlight_mesh(index)
                    return True
            return False
        except Exception as e:
            logger.error(f"Erreur lors de la mise en évidence par nom: {e}")
            return False

    def enable_mesh_hover_highlight(self, enable=True):
        """Active/désactive la surbrillance au survol de la souris."""
        try:
            if enable:
                # Utiliser l'API VTK directement pour ajouter l'observateur
                self.plotter.interactor.AddObserver("MouseMoveEvent", self.on_mouse_move_highlight)
            else:
                # Utiliser l'API VTK directement pour supprimer l'observateur
                self.plotter.interactor.RemoveObservers("MouseMoveEvent")
        except Exception as e:
            logger.error(f"Erreur lors de la configuration du survol: {e}")

    def on_mouse_move_highlight(self, obj, event):
        """Gère le survol de la souris pour la surbrillance."""
        try:
            # Obtenir la position de la souris
            picker = self.plotter.pick_mouse_position()
            point = self._extract_point_from_picker(picker)
            
            if point is not None:
                # Trouver le mesh le plus proche
                closest_mesh_index = self.find_closest_mesh_index(point)
                if closest_mesh_index >= 0:
                    self.highlight_mesh(closest_mesh_index)
                    
                    # Émettre le nom du mesh survolé
                    if hasattr(self, 'scene') and hasattr(self.scene, 'meshes'):
                        mesh_names = list(self.scene.meshes.keys())
                        if closest_mesh_index < len(mesh_names):
                            self.mesh_hovered.emit(mesh_names[closest_mesh_index])
        except Exception as e:
            logger.debug(f"Erreur lors du survol: {e}")

    def find_closest_mesh_index(self, point):
        """Trouve l'index du mesh le plus proche d'un point."""
        try:
            if not hasattr(self, '_scene_actors') or not self._scene_actors:
                return -1
                
            min_distance = float('inf')
            closest_index = -1
            
            for i, actor in enumerate(self._scene_actors):
                try:
                    # Obtenir les bounds de l'acteur
                    bounds = actor.GetBounds()
                    if bounds:
                        # Calculer le centre du mesh
                        center = [
                            (bounds[0] + bounds[1]) / 2,
                            (bounds[2] + bounds[3]) / 2,
                            (bounds[4] + bounds[5]) / 2
                        ]
                        
                        # Calculer la distance
                        distance = ((point[0] - center[0]) ** 2 + 
                                   (point[1] - center[1]) ** 2 + 
                                   (point[2] - center[2]) ** 2) ** 0.5
                        
                        if distance < min_distance:
                            min_distance = distance
                            closest_index = i
                except Exception as e:
                    logger.debug(f"Erreur avec l'acteur {i}: {e}")
                    continue
                
            return closest_index
        except Exception as e:
            logger.error(f"Erreur lors de la recherche du mesh le plus proche: {e}")
            return -1


    def add_mesh_labels(self):
        """Ajoute des étiquettes aux meshes pour les identifier."""
        try:
            if not hasattr(self, 'scene') or not hasattr(self.scene, 'meshes'):
                logger.warning("SceneViewer3D: Pas de scène ou de meshes pour ajouter les labels")
                return
            
            # Utiliser le nouveau système d'acteurs individuels
            for object_name, actor in self.object_actors.items():
                try:
                    bounds = actor.GetBounds()
                    if bounds and len(bounds) >= 6:
                        # Positionner l'étiquette au centre du mesh
                        position = [
                            (bounds[0] + bounds[1]) / 2,
                            (bounds[2] + bounds[3]) / 2,
                            (bounds[4] + bounds[5]) / 2
                        ]
                        # Utiliser un nom convivial pour l'affichage
                        display_name = self.get_friendly_name(object_name)
                        
                        # Ajouter l'étiquette
                        self.plotter.add_point_labels(
                            [position],
                            [display_name],
                            point_size=0,
                            font_size=12,
                            text_color='yellow',
                            shape_opacity=0.8
                        )
                        logger.info(f"SceneViewer3D: Label ajouté pour {object_name} à {position}")
                except Exception as e:
                    logger.warning(f"SceneViewer3D: Impossible d'ajouter le label pour {object_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des étiquettes: {e}")

    # === NOUVELLES MÉTHODES POUR LA NAVIGATION ET SURBRILLANCE D'OBJETS ===
    
    def highlight_object(self, object_name, highlight=True):
        """Met en surbrillance un objet spécifique dans la scène."""
        try:
            if not hasattr(self, 'scene') or not self.scene:
                return False
                
            # Trouver l'acteur correspondant à l'objet
            actor_found = False
            
            # Méthode 1: Chercher par nom de mesh
            if hasattr(self.scene, 'get_mesh_names'):
                mesh_names = self.scene.get_mesh_names()
                if object_name in mesh_names:
                    mesh_index = mesh_names.index(object_name)
                    if mesh_index < len(self._scene_actors):
                        actor = self._scene_actors[mesh_index]
                        self._apply_highlight_to_actor(actor, highlight)
                        actor_found = True
            
            # Méthode 2: Si pas trouvé, chercher l'acteur principal
            if not actor_found and object_name in ["main_scene", "unnamed_objects"]:
                if self.mesh_actor:
                    self._apply_highlight_to_actor(self.mesh_actor, highlight)
                    actor_found = True
                elif len(self._scene_actors) > 0:
                    # Surligner tous les acteurs de scène
                    for actor in self._scene_actors:
                        self._apply_highlight_to_actor(actor, highlight)
                    actor_found = True
            
            if actor_found:
                # Ajouter des flèches pointant vers l'objet si mise en surbrillance
                if highlight:
                    self._add_navigation_arrows(object_name)
                else:
                    self._remove_navigation_arrows(object_name)
                    
                # Rafraîchir l'affichage
                if hasattr(self.plotter, 'render'):
                    self.plotter.render()
                    
                return True
                
        except Exception as e:
            logger.error(f"Erreur lors de la surbrillance de l'objet {object_name}: {e}")
            
        return False
    
    def _apply_highlight_to_actor(self, actor, highlight=True):
        """Applique ou retire la surbrillance sur un acteur."""
        try:
            if not actor:
                return
                
            if highlight:
                # Sauvegarder la couleur originale dans notre dictionnaire externe
                actor_id = id(actor)
                if actor_id not in self.actor_original_colors:
                    self.actor_original_colors[actor_id] = actor.GetProperty().GetColor()
                
                # Appliquer la couleur de surbrillance (rouge/jaune pulsant)
                actor.GetProperty().SetColor(1.0, 0.8, 0.0)  # Jaune/Orange
                actor.GetProperty().SetOpacity(0.9)
                
                # Ajouter un effet de bordure
                actor.GetProperty().SetEdgeVisibility(True)
                actor.GetProperty().SetEdgeColor(1.0, 0.0, 0.0)  # Rouge pour les bordures
                actor.GetProperty().SetLineWidth(2)
                
            else:
                # Restaurer la couleur originale depuis notre dictionnaire
                actor_id = id(actor)
                if actor_id in self.actor_original_colors:
                    actor.GetProperty().SetColor(self.actor_original_colors[actor_id])
                    # Ne pas supprimer la couleur car elle peut être réutilisée
                else:
                    # Couleur par défaut si pas de couleur sauvegardée
                    actor.GetProperty().SetColor(0.8, 0.8, 0.8)
                
                actor.GetProperty().SetOpacity(1.0)
                actor.GetProperty().SetEdgeVisibility(False)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'application de la surbrillance: {e}")
    
    def _add_navigation_arrows(self, object_name):
        """Ajoute des flèches pointant vers l'objet."""
        try:
            # Retirer les anciennes flèches pour cet objet
            self._remove_navigation_arrows(object_name)
            
            # Calculer la position de l'objet
            object_center = self._get_object_center(object_name)
            if object_center is None:
                return
                
            # Créer des flèches pointant vers l'objet depuis différentes directions
            arrow_directions = [
                [1, 0, 0],   # Droite
                [-1, 0, 0],  # Gauche  
                [0, 1, 0],   # Devant
                [0, -1, 0],  # Derrière
                [0, 0, 1],   # Dessus
            ]
            
            arrow_actors = []
            arrow_distance = 50.0  # Distance des flèches par rapport à l'objet
            
            for direction in arrow_directions:
                # Position de départ de la flèche
                start_pos = [
                    object_center[0] + direction[0] * arrow_distance,
                    object_center[1] + direction[1] * arrow_distance,
                    object_center[2] + direction[2] * arrow_distance
                ]
                
                # Créer une flèche pointant vers l'objet
                arrow = pv.Arrow(start=start_pos, direction=[-d for d in direction], scale=20.0)
                
                # Ajouter la flèche à la scène
                arrow_actor = self.plotter.add_mesh(
                    arrow,
                    color='red',
                    opacity=0.8,
                    name=f"arrow_{object_name}_{len(arrow_actors)}"
                )
                arrow_actors.append(arrow_actor)
            
            # Sauvegarder les acteurs de flèches pour pouvoir les supprimer plus tard
            if not hasattr(self, '_navigation_arrows'):
                self._navigation_arrows = {}
            self._navigation_arrows[object_name] = arrow_actors
            
            # Ajouter un texte flottant au-dessus de l'objet
            text_pos = [object_center[0], object_center[1], object_center[2] + 30]
            text_actor = self.plotter.add_point_labels(
                [text_pos],
                [f"📍 {object_name}"],
                point_size=0,
                font_size=12,
                text_color='red',
                shape_opacity=0.8,
                name=f"label_{object_name}"
            )
            
            if object_name not in self._navigation_arrows:
                self._navigation_arrows[object_name] = []
            self._navigation_arrows[object_name].append(text_actor)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des flèches de navigation: {e}")
    
    def _remove_navigation_arrows(self, object_name):
        """Supprime les flèches de navigation pour un objet."""
        try:
            if not hasattr(self, '_navigation_arrows'):
                return
                
            if object_name in self._navigation_arrows:
                # Supprimer tous les acteurs de flèches/labels pour cet objet
                for actor in self._navigation_arrows[object_name]:
                    try:
                        if hasattr(self.plotter, 'remove_actor'):
                            self.plotter.remove_actor(actor)
                        else:
                            # Méthode alternative
                            actor.SetVisibility(False)
                    except:
                        pass
                
                # Nettoyer la liste
                del self._navigation_arrows[object_name]
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression des flèches: {e}")
    
    def _get_object_center(self, object_name):
        """Obtient le centre d'un objet."""
        try:
            if not hasattr(self, 'scene') or not self.scene:
                return None
                
            # Méthode 1: Utiliser les informations de la scène
            if hasattr(self.scene, 'get_mesh_names'):
                mesh_names = self.scene.get_mesh_names()
                if object_name in mesh_names:
                    mesh_index = mesh_names.index(object_name)
                    if mesh_index < len(self._scene_actors):
                        actor = self._scene_actors[mesh_index]
                        bounds = actor.GetBounds()
                        return [
                            (bounds[0] + bounds[1]) / 2,
                            (bounds[2] + bounds[3]) / 2,
                            (bounds[4] + bounds[5]) / 2
                        ]
            
            # Méthode 2: Utiliser le mesh principal
            if object_name in ["main_scene", "unnamed_objects"]:
                if hasattr(self.scene, 'get_center'):
                    return list(self.scene.get_center())
                elif self.mesh_actor:
                    bounds = self.mesh_actor.GetBounds()
                    return [
                        (bounds[0] + bounds[1]) / 2,
                        (bounds[2] + bounds[3]) / 2,
                        (bounds[4] + bounds[5]) / 2
                    ]
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du centre de l'objet: {e}")
            return None
    
    def center_on_object(self, object_name):
        """Centre la caméra sur un objet spécifique."""
        try:
            object_center = self._get_object_center(object_name)
            if object_center is None:
                return False
                
            # Centrer la caméra sur l'objet
            self.plotter.camera_position = 'xy'  # Vue de dessus d'abord
            self.plotter.camera.SetFocalPoint(object_center)
            
            # Ajuster la distance de la caméra pour bien voir l'objet
            camera_distance = 100.0  # Distance par défaut
            camera_pos = [
                object_center[0],
                object_center[1] - camera_distance,
                object_center[2] + camera_distance/2
            ]
            self.plotter.camera.SetPosition(camera_pos)
            
            # Rafraîchir l'affichage
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
                
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du centrage sur l'objet: {e}")
            return False
    
    def clear_all_highlights(self):
        """Efface toutes les surbrillances et flèches de navigation."""
        try:
            # Supprimer toutes les flèches de navigation
            if hasattr(self, '_navigation_arrows'):
                for object_name in list(self._navigation_arrows.keys()):
                    self._remove_navigation_arrows(object_name)
            
            # Restaurer les couleurs originales de tous les acteurs
            all_actors = []
            if self.mesh_actor:
                all_actors.append(self.mesh_actor)
            all_actors.extend(self._scene_actors)
            
            for actor in all_actors:
                self._apply_highlight_to_actor(actor, highlight=False)
            
            # Rafraîchir l'affichage
            if hasattr(self.plotter, 'render'):
                self.plotter.render()
                
        except Exception as e:
            logger.error(f"Erreur lors de l'effacement des surbrillances: {e}")
    
    def apply_material_color(self, object_name, material_properties):
        """Applique la couleur du matériau à l'objet dans la visualisation 3D."""
        logger.info(f"apply_material_color appelée pour {object_name} avec {material_properties}")
        try:
            # Extraire la couleur depuis les propriétés du matériau
            color_hex = material_properties.get('color', '#FF6464')
            logger.info(f"Couleur extraite: {color_hex}")
            
            # Convertir la couleur hex en RGB normalisé (0-1)
            if color_hex.startswith('#'):
                hex_color = color_hex[1:]
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16) / 255.0
                    g = int(hex_color[2:4], 16) / 255.0 
                    b = int(hex_color[4:6], 16) / 255.0
                    color_rgb = [r, g, b]
                else:
                    color_rgb = [1.0, 0.4, 0.4]  # Rouge par défaut
            else:
                color_rgb = [1.0, 0.4, 0.4]  # Rouge par défaut
            
            logger.info(f"Couleur RGB normalisée: {color_rgb}")
            
            # NOUVEAU: Appliquer la couleur à l'acteur spécifique par nom d'objet
            color_applied = False
            
            # Chercher l'acteur correspondant à l'objet
            if hasattr(self, 'object_actors') and object_name in self.object_actors:
                try:
                    actor = self.object_actors[object_name]
                    actor.GetProperty().SetColor(color_rgb)
                    color_applied = True
                    logger.info(f"Couleur appliquée à l'acteur spécifique {object_name}: {color_rgb}")
                except Exception as e:
                    logger.warning(f"Impossible d'appliquer la couleur à l'acteur {object_name}: {e}")
            else:
                logger.warning(f"Acteur non trouvé pour {object_name}")
                
                # Fallback: utiliser l'ancien système si pas d'acteurs séparés
                if self.mesh_actor:
                    try:
                        self.mesh_actor.GetProperty().SetColor(color_rgb)
                        color_applied = True
                        logger.info(f"Couleur appliquée à l'acteur principal (fallback): {color_rgb}")
                    except Exception as e:
                        logger.warning(f"Impossible d'appliquer la couleur à l'acteur principal: {e}")
                
                # Vérifier les acteurs de scène
                logger.info(f"Nombre d'acteurs de scène: {len(self._scene_actors)}")
                for i, actor in enumerate(self._scene_actors):
                    try:
                        actor.GetProperty().SetColor(color_rgb)
                        color_applied = True
                        logger.info(f"Couleur appliquée à l'acteur de scène {i}: {color_rgb}")
                    except Exception as e:
                        logger.warning(f"Impossible d'appliquer la couleur à l'acteur de scène {i}: {e}")
            
            # Rafraîchir l'affichage
            if color_applied and hasattr(self.plotter, 'render'):
                self.plotter.render()
                logger.info(f"Rendu mis à jour pour {object_name}: {color_hex}")
            else:
                logger.warning(f"Aucun acteur trouvé pour appliquer la couleur à {object_name}")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'application de la couleur du matériau: {e}")
