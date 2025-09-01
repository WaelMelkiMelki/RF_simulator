# src/gui/widgets/visualization_engine.py
"""
Moteur de Visualisation 3D - NETDATA INNOVATION
COUCHE INFRASTRUCTURE - External Services

Moteur de visualisation haute performance PyVista/VTK.
Conforme à l'architecture NETDATA avec séparation des responsabilités.

Responsabilités :
- Rendu 3D PyVista/VTK  
- Gestion des acteurs et meshes
- Optimisations de performance
- Interface avec GPU si disponible
- Calculs de visualisation
"""
import logging
import time
import numpy as np
import psutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import pyvista as pv
from pyvistaqt import QtInteractor

logger = logging.getLogger(__name__)

class VisualizationEngine(QWidget):
    """
    Moteur de Visualisation 3D haute performance - NETDATA INNOVATION
    
    COUCHE INFRASTRUCTURE - External Services
    Responsabilités :
    - Rendu 3D PyVista/VTK avec optimisations
    - Gestion des acteurs et meshes 3D
    - Calculs de visualisation haute performance
    - Interface GPU si disponible
    - Cache de rendu intelligent
    - Monitoring des performances
    
    Utilisé par :
    - GUI (Presentation Layer) via SceneViewer3DWidget
    - EXPORTER (Application Layer) pour génération de rapports
    """
    
    # Signaux pour communication avec les couches supérieures
    mesh_selected = pyqtSignal(int)
    right_click_position = pyqtSignal(float, float, float)  
    mesh_hovered = pyqtSignal(str)
    performance_metrics = pyqtSignal(dict)  # Métriques de performance temps réel
    render_completed = pyqtSignal(dict)     # Signal de fin de rendu avec statistiques
    
    def __init__(self, parent=None):
        """Initialise le moteur de visualisation."""
        super().__init__(parent)
        
        # Configuration PyVista pour performances optimales NETDATA
        self._configure_pyvista_performance()
        
        # Initialisation des structures de données du moteur
        self._init_engine_data()
        
        # Interface de rendu PyVista
        self._init_rendering_interface()
        
        # Monitoring des performances  
        self._init_performance_monitoring()
        
        # Configuration des interactions de base
        self._setup_engine_interactions()
        
        logger.info("VisualizationEngine: Moteur de visualisation NETDATA initialisé")
    
    def _configure_pyvista_performance(self):
        """Configure PyVista pour performances optimales selon spécifications NETDATA."""
        try:
            # Détection et configuration GPU
            gpu_available = self._detect_gpu_support()
            
            if gpu_available:
                # Configuration GPU avec vérification des attributs disponibles
                if hasattr(pv.global_theme, 'gpu_info'):
                    pv.global_theme.gpu_info = True
                if hasattr(pv.global_theme, 'use_gpu'):
                    pv.global_theme.use_gpu = True
                logger.info("VisualizationEngine: Configuration GPU activée")
            
            # Optimisations de rendu haute performance (avec vérifications)
            if hasattr(pv.global_theme, 'multi_samples'):
                pv.global_theme.multi_samples = 8  # Anti-aliasing
            if hasattr(pv.global_theme, 'use_depth_peeling'):
                pv.global_theme.use_depth_peeling = True  # Transparence avancée
            if hasattr(pv.global_theme, 'enable_anti_aliasing'):
                pv.global_theme.enable_anti_aliasing = True
            if hasattr(pv.global_theme, 'smooth_shading'):
                pv.global_theme.smooth_shading = True
            
            # Configuration mémoire pour gros datasets
            if hasattr(pv.global_theme, 'use_fxaa'):
                pv.global_theme.use_fxaa = True  # Fast Approximate Anti-Aliasing
            
            logger.info("VisualizationEngine: Configuration PyVista haute performance activée")
            
        except Exception as e:
            logger.warning(f"VisualizationEngine: Erreur configuration performance: {e}")
    
    def _detect_gpu_support(self):
        """Détecte le support GPU pour accélération."""
        try:
            # Test simple de disponibilité GPU
            import platform
            system = platform.system()
            
            # Sur Windows, vérifier les drivers GPU
            if system == "Windows":
                try:
                    import subprocess
                    result = subprocess.run(['wmic', 'path', 'win32_VideoController', 'get', 'name'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and ('NVIDIA' in result.stdout or 'AMD' in result.stdout):
                        return True
                except:
                    pass
            
            # Test PyVista GPU capabilities
            try:
                pl = pv.Plotter(off_screen=True)
                pl.add_mesh(pv.Sphere())
                pl.close()
                return True
            except:
                pass
                
            return False
            
        except Exception as e:
            logger.debug(f"VisualizationEngine: GPU non détecté: {e}")
            return False
    
    def _init_engine_data(self):
        """Initialise les structures de données du moteur."""
        # Acteurs et meshes (optimisé pour accès rapide)
        self.antenna_actors = []
        self.mesh_actor = None
        self._scene_actors = []
        self.object_actors = {}  # Index par nom pour accès O(1)
        self.antenna_coverage_actors = []
        self.antenna_radius_actors = []
        self.results_actor = None
        self.scalar_bar_actor = None
        
        # Cache de rendu intelligent
        self._render_cache = {}
        self._mesh_cache = {}
        
        # Données de performance et couverture
        self.antenna_coverage_data = []
        self.interest_center = None
        self.interest_radius = 20.0
        self.zone_opacity_inside = 1.0
        self.zone_opacity_outside = 0.1
        
        # État du moteur
        self.is_2d_mode = False
        self.current_2d_plane = "XY (Horizontal)"
        self.cursor_actor_2d = None
        
        # Sélection et interaction
        self.current_selected_index = -1
        self.actor_colors = []
        self.highlight_color = [1, 0, 0]  # Rouge
        self.total_meshes = 0
        self.actor_original_colors = {}
        
        # Métriques de performance
        self.performance_stats = {
            'render_time': 0.0,
            'frame_count': 0,
            'memory_usage': 0.0,
            'gpu_utilization': 0.0
        }
    
    def _init_rendering_interface(self):
        """Initialise l'interface de rendu PyVista."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Plotter PyVista optimisé
        self.plotter = QtInteractor(self)
        self.plotter.enable_parallel_projection()
        self.plotter.add_axes()
        self.plotter.show_grid()
        self.plotter.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Configuration background optimal pour visualisation
        self.plotter.set_background('white')
        
        layout.addWidget(self.plotter)
        self.setLayout(layout)
        
        # Focus pour interactions
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()
        
        # Initialiser scène vide
        self._initialize_empty_scene()
    
    def _init_performance_monitoring(self):
        """Initialise le monitoring des performances.""" 
        try:
            self.performance_timer = QTimer()
            self.performance_timer.timeout.connect(self._collect_performance_metrics)
            self.performance_timer.start(1000)  # Collecte chaque seconde
            
            logger.info("VisualizationEngine: Monitoring de performance activé")
            
        except Exception as e:
            logger.warning(f"VisualizationEngine: Erreur init monitoring: {e}")
    
    def _collect_performance_metrics(self):
        """Collecte les métriques de performance en temps réel."""
        try:
            # Métriques système
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            
            # Métriques de rendu
            frame_time = getattr(self, '_last_render_time', 0.0)
            
            metrics = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_info.percent,
                'memory_used_mb': memory_info.used / (1024 * 1024),
                'frame_time_ms': frame_time * 1000,
                'fps': 1.0 / frame_time if frame_time > 0 else 0,
                'active_actors': len(self._scene_actors) + len(self.antenna_actors),
                'total_points': self._calculate_total_points()
            }
            
            self.performance_stats.update(metrics)
            self.performance_metrics.emit(metrics)
            
        except Exception as e:
            logger.debug(f"VisualizationEngine: Erreur collecte métriques: {e}")
    
    def _calculate_total_points(self):
        """Calcule le nombre total de points dans la scène."""
        total = 0
        try:
            for actor in self._scene_actors:
                if hasattr(actor, 'GetMapper') and actor.GetMapper():
                    input_data = actor.GetMapper().GetInput()
                    if hasattr(input_data, 'GetNumberOfPoints'):
                        total += input_data.GetNumberOfPoints()
        except:
            pass
        return total
    
    def _setup_engine_interactions(self):
        """Configure les interactions de base du moteur."""
        try:
            # Suivi de la souris pour interactions
            self.plotter.track_mouse_position = True
            
            # Événements VTK pour interactions avancées
            self.plotter.interactor.AddObserver('MouseMoveEvent', self._on_mouse_move_vtk)
            self.plotter.interactor.AddObserver('RightButtonPressEvent', self._on_right_click_vtk)
            
            logger.info("VisualizationEngine: Interactions configurées")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur configuration interactions: {e}")
    
    def _initialize_empty_scene(self):
        """Initialise une scène vide optimisée."""
        try:
            self.plotter.clear()
            self.plotter.add_axes()
            self.plotter.show_grid()
            self.plotter.reset_camera()
            
            # Ajouter un texte d'info initial
            self.plotter.add_text("Moteur de Visualisation NETDATA\nPrêt pour affichage", 
                                 position='upper_left', 
                                 font_size=10, 
                                 color='gray')
            
            logger.info("VisualizationEngine: Scène vide initialisée")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur initialisation scène: {e}")
    
    def _on_mouse_move_vtk(self, obj, event):
        """Gère le mouvement de la souris via VTK."""
        try:
            picker = self.plotter.pick_mouse_position()
            point = self._extract_point_from_picker(picker)
            
            if point is not None and len(point) >= 3:
                x, y, z = point[0], point[1], point[2]
                # Logique de détection de survol d'objets
                self._handle_object_hover(x, y, z)
        except Exception as e:
            logger.debug(f"VisualizationEngine: Erreur suivi souris: {e}")
    
    def _on_right_click_vtk(self, obj, event):
        """Gère les clics droits via VTK."""
        try:
            picker = self.plotter.pick_mouse_position()
            point = self._extract_point_from_picker(picker)
            
            if point is not None and len(point) >= 3:
                x, y, z = point[0], point[1], point[2]
                self.right_click_position.emit(x, y, z)
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur clic droit: {e}")
    
    def _extract_point_from_picker(self, picker):
        """Extrait les coordonnées 3D d'un picker."""
        try:
            if picker is None:
                return None
            
            # Si c'est directement un tableau numpy
            if isinstance(picker, np.ndarray) and picker.size >= 3:
                return picker.flatten()[:3]
            
            # Si c'est une liste ou tuple
            if hasattr(picker, '__len__') and len(picker) >= 3:
                return list(picker)[:3]
            
            # Si c'est un objet VTK avec GetPosition
            if hasattr(picker, 'GetPosition'):
                pos = picker.GetPosition()
                if pos and len(pos) >= 3:
                    return list(pos)[:3]
            
            return None
            
        except Exception as e:
            logger.debug(f"VisualizationEngine: Erreur extraction point: {e}")
            return None
    
    def _handle_object_hover(self, x, y, z):
        """Gère le survol d'objets."""
        try:
            # Logique de détection d'objets sous le curseur
            # Pour l'instant, émettre un signal générique
            self.mesh_hovered.emit(f"Point ({x:.1f}, {y:.1f}, {z:.1f})")
        except Exception as e:
            logger.debug(f"VisualizationEngine: Erreur gestion survol: {e}")
    
    # Interface publique pour les couches supérieures
    
    def update_scene(self, scene):
        """
        Met à jour la scène 3D.
        
        Interface principale pour la couche Application.
        """
        try:
            start_time = time.time()
            
            logger.info("VisualizationEngine: Mise à jour de la scène")
            
            # Effacer la scène précédente
            self.clear_scene()
            
            # Rendu optimisé selon le type de scène
            if hasattr(scene, 'meshes') and scene.meshes:
                # Préférer le rendu multi-mesh quand disponible
                self._render_multi_mesh_scene(scene)
            elif hasattr(scene, 'get_pyvista_mesh'):
                # Fallback vers single-mesh si pas de meshes individuels
                self._render_single_mesh_scene(scene)
            else:
                logger.warning("VisualizationEngine: Format de scène non reconnu")
                return
            
            # Ajuster la caméra
            self.plotter.reset_camera()
            
            # Métriques de performance
            render_time = time.time() - start_time
            self._last_render_time = render_time
            
            # Signal de fin de rendu
            self.render_completed.emit({
                'render_time': render_time,
                'total_actors': len(self._scene_actors),
                'total_points': self._calculate_total_points()
            })
            
            logger.info(f"VisualizationEngine: Scène mise à jour en {render_time:.3f}s")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur mise à jour scène: {e}")
            import traceback
            traceback.print_exc()
    
    def _render_multi_mesh_scene(self, scene):
        """Rendu optimisé pour scène multi-mesh."""
        try:
            total_points = 0
            
            for object_name, mesh in scene.meshes.items():
                if mesh is None or mesh.n_points == 0:
                    continue
                
                # Optimisations de rendu
                color = self._get_optimized_color_for_object(object_name)
                
                # Ajout avec optimisations
                actor = self.plotter.add_mesh(
                    mesh,
                    color=color,
                    opacity=0.8,
                    smooth_shading=True,
                    name=object_name
                )
                
                self._scene_actors.append(actor)
                self.object_actors[object_name] = actor
                total_points += mesh.n_points
                
                logger.debug(f"VisualizationEngine: Objet {object_name} rendu ({mesh.n_points} points)")
            
            logger.info(f"VisualizationEngine: {len(scene.meshes)} objets rendus, total: {total_points} points")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur rendu multi-mesh: {e}")
    
    def _render_single_mesh_scene(self, scene):
        """Rendu optimisé pour scène single-mesh."""
        try:
            mesh = scene.get_pyvista_mesh()
            if mesh is None or mesh.n_points == 0:
                logger.warning("VisualizationEngine: Mesh vide ou None")
                return
            
            # Rendu avec différentiation automatique des couleurs
            self._apply_differentiated_coloring(mesh)
            
            actor = self.plotter.add_mesh(
                mesh,
                scalars=mesh.active_scalars_name if mesh.active_scalars_name else None,
                opacity=0.8,
                smooth_shading=True
            )
            
            self._scene_actors.append(actor)
            self.mesh_actor = actor
            
            logger.info(f"VisualizationEngine: Mesh unique rendu ({mesh.n_points} points)")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur rendu single-mesh: {e}")
    
    def _get_optimized_color_for_object(self, object_name):
        """Génère une couleur optimisée pour un objet."""
        # Palette de couleurs optimisée pour la visualisation
        colors = [
            [0.8, 0.8, 0.9],   # Bleu clair
            [0.9, 0.8, 0.8],   # Rouge clair  
            [0.8, 0.9, 0.8],   # Vert clair
            [0.9, 0.9, 0.8],   # Jaune clair
            [0.9, 0.8, 0.9],   # Magenta clair
            [0.8, 0.9, 0.9],   # Cyan clair
        ]
        
        # Hash simple pour assigner une couleur consistante
        hash_val = sum(ord(c) for c in object_name) % len(colors)
        return colors[hash_val]
    
    def _apply_differentiated_coloring(self, mesh):
        """Applique une coloration différenciée à un mesh."""
        try:
            if mesh.n_points == 0:
                return
            
            # Générer des couleurs basées sur la position Z pour différenciation
            z_coords = mesh.points[:, 2]
            normalized_z = (z_coords - z_coords.min()) / (z_coords.max() - z_coords.min() + 1e-8)
            
            mesh['height_colors'] = normalized_z
            mesh.set_active_scalars('height_colors')
            
        except Exception as e:
            logger.debug(f"VisualizationEngine: Erreur coloration: {e}")
    
    def clear_scene(self):
        """Efface la scène actuelle."""
        try:
            # Effacer tous les acteurs
            self.plotter.clear()
            
            # Réinitialiser les listes
            self._scene_actors.clear()
            self.object_actors.clear()
            self.antenna_actors.clear()
            self.antenna_coverage_actors.clear()
            self.antenna_coverage_data.clear()
            
            # Remettre les éléments de base
            self.plotter.add_axes()
            self.plotter.show_grid()
            
            logger.info("VisualizationEngine: Scène effacée")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur effacement scène: {e}")
    
    def show_antenna_coverage(self, results_dict, antennas=None):
        """Affiche la couverture d'antennes de manière optimisée."""
        try:
            logger.info("VisualizationEngine: Affichage couverture antennes")
            
            # Effacer les résultats précédents
            self._clear_coverage_results()
            
            # Rendu optimisé des points de couverture
            self._visualize_coverage_points_optimized(results_dict, antennas)
            
            logger.info("VisualizationEngine: Couverture antennes affichée")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur affichage couverture: {e}")
    
    def _clear_coverage_results(self):
        """Efface les résultats de couverture précédents."""
        try:
            # Supprimer les acteurs de couverture
            for actor in self.antenna_coverage_actors:
                if actor in self.plotter.actors:
                    self.plotter.remove_actor(actor)
            
            self.antenna_coverage_actors.clear()
            self.antenna_coverage_data.clear()
            
            # Supprimer la barre de couleur si présente
            if self.scalar_bar_actor:
                self.plotter.remove_actor(self.scalar_bar_actor)
                self.scalar_bar_actor = None
                
        except Exception as e:
            logger.debug(f"VisualizationEngine: Erreur effacement couverture: {e}")
    
    def _visualize_coverage_points_optimized(self, results_dict, antennas=None):
        """Visualisation optimisée des points de couverture."""
        try:
            if not results_dict:
                logger.warning("VisualizationEngine: Aucun résultat à afficher")
                return
            
            points = []
            values = []
            
            # Extraire les données
            for position, signal_strength in results_dict.items():
                if isinstance(position, (tuple, list)) and len(position) >= 3:
                    points.append(list(position))
                    values.append(float(signal_strength))
            
            if not points:
                logger.warning("VisualizationEngine: Aucun point valide trouvé")
                return
            
            points = np.array(points)
            values = np.array(values)
            
            logger.info(f"VisualizationEngine: Rendu de {len(points)} points de couverture")
            
            # Créer le nuage de points optimisé
            point_cloud = pv.PolyData(points)
            point_cloud['signal_strength'] = values
            
            # Configuration de rendu haute performance
            coverage_actor = self.plotter.add_mesh(
                point_cloud,
                scalars='signal_strength',
                cmap='viridis',
                render_points_as_spheres=True,
                point_size=8,
                opacity=0.8,
                smooth_shading=True,
                scalar_bar_args={
                    'title': 'Puissance (dBm)',
                    'title_font_size': 16,
                    'label_font_size': 12,
                    'position_x': 0.85,
                    'position_y': 0.1,
                    'width': 0.12,
                    'height': 0.8
                }
            )
            
            self.antenna_coverage_actors.append(coverage_actor)
            self.antenna_coverage_data.append(point_cloud)
            
            logger.info(f"VisualizationEngine: Couverture affichée - {len(points)} points")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation couverture: {e}")
    
    def add_antenna(self, position, antenna_type="base", name=None, properties=None):
        """Ajoute une antenne de manière optimisée."""
        try:
            if len(position) < 3:
                logger.error("VisualizationEngine: Position d'antenne invalide")
                return None
            
            # Créer la géométrie d'antenne
            antenna_mesh = self._create_antenna_geometry(antenna_type, properties)
            
            # Positionner l'antenne
            antenna_mesh = antenna_mesh.translate(position)
            
            # Couleur selon le type
            color = self._get_antenna_color(antenna_type)
            
            # Ajouter à la scène
            actor = self.plotter.add_mesh(
                antenna_mesh,
                color=color,
                opacity=0.9,
                smooth_shading=True,
                name=name or f"Antenne_{len(self.antenna_actors)}"
            )
            
            self.antenna_actors.append(actor)
            
            logger.info(f"VisualizationEngine: Antenne {antenna_type} ajoutée en {position}")
            return actor
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur ajout antenne: {e}")
            return None
    
    def _create_antenna_geometry(self, antenna_type, properties=None):
        """Crée la géométrie d'une antenne."""
        try:
            if antenna_type == "wifi":
                # Antenne WiFi - cylindre avec cône
                base = pv.Cylinder(radius=0.5, height=2.0, resolution=8)
                tip = pv.Cone(radius=0.3, height=1.0, resolution=8)
                tip = tip.translate([0, 0, 1.5])
                return base + tip
            
            elif antenna_type == "5g":
                # Antenne 5G - structure plus complexe
                base = pv.Box(bounds=[-0.5, 0.5, -0.5, 0.5, 0, 3])
                panel = pv.Box(bounds=[-1, 1, -0.1, 0.1, 1, 2.5])
                return base + panel
            
            else:
                # Antenne de base - simple cylindre
                return pv.Cylinder(radius=0.3, height=2.0, resolution=8)
                
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur création géométrie antenne: {e}")
            return pv.Cylinder(radius=0.3, height=2.0, resolution=6)  # Fallback
    
    def _get_antenna_color(self, antenna_type):
        """Retourne la couleur d'une antenne selon son type."""
        colors = {
            "wifi": [0.2, 0.6, 1.0],    # Bleu
            "5g": [1.0, 0.4, 0.2],      # Orange/Rouge
            "base": [0.6, 0.6, 0.6]     # Gris
        }
        return colors.get(antenna_type, colors["base"])
    
    def clear_antennas(self):
        """Efface toutes les antennes."""
        try:
            for actor in self.antenna_actors:
                if actor in self.plotter.actors:
                    self.plotter.remove_actor(actor)
            
            self.antenna_actors.clear()
            logger.info("VisualizationEngine: Antennes effacées")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur effacement antennes: {e}")
    
    def cleanup(self):
        """Nettoyage du moteur."""
        try:
            if hasattr(self, 'performance_timer') and self.performance_timer:
                self.performance_timer.stop()
            
            self.clear_scene()
            
            if hasattr(self, 'plotter') and self.plotter:
                self.plotter.close()
            
            logger.info("VisualizationEngine: Nettoyage terminé")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur nettoyage: {e}")
    
    # Méthodes de compatibilité pour l'interface existante
    def update_point_opacity(self, opacity):
        """Met à jour l'opacité des points de simulation et antennes."""
        try:
            opacity = max(0.0, min(1.0, opacity))  # S'assurer que l'opacité est entre 0 et 1
            actors_updated = 0
            
            # Mettre à jour l'opacité des points de simulation
            if hasattr(self, 'results_actor') and self.results_actor:
                if hasattr(self.results_actor, 'GetProperty'):
                    self.results_actor.GetProperty().SetOpacity(opacity)
                    actors_updated += 1
            
            # Mettre à jour l'opacité des antennes
            for actor in self.antenna_actors:
                if hasattr(actor, 'GetProperty'):
                    actor.GetProperty().SetOpacity(opacity)
                    actors_updated += 1
            
            # Mettre à jour l'opacité des acteurs de couverture
            for actor in self.antenna_coverage_actors:
                if hasattr(actor, 'GetProperty'):
                    actor.GetProperty().SetOpacity(opacity)
                    actors_updated += 1
            
            # Forcer le rendu
            self.plotter.render()
            logger.info(f"VisualizationEngine: Opacité des points mise à jour à {opacity:.2f} sur {actors_updated} acteurs")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur opacité points: {e}")
    
    def update_point_density(self, size):
        """Met à jour la taille des points de simulation uniquement (pas les antennes).""" 
        try:
            size = max(1.0, min(20.0, size))  # Limiter la taille entre 1 et 20
            actors_updated = 0
            
            # Mettre à jour UNIQUEMENT la taille des points de simulation
            if hasattr(self, 'results_actor') and self.results_actor:
                if hasattr(self.results_actor, 'GetProperty'):
                    self.results_actor.GetProperty().SetPointSize(size)
                    actors_updated += 1
            
            # NE PAS modifier les antennes - elles gardent leur taille d'origine
            # Les antennes ne doivent pas changer avec la densité des points
            
            # Mettre à jour la taille des points de couverture seulement
            for actor in self.antenna_coverage_actors:
                if hasattr(actor, 'GetProperty'):
                    actor.GetProperty().SetPointSize(size)
                    actors_updated += 1
            
            # Forcer le rendu
            self.plotter.render()
            logger.info(f"VisualizationEngine: Taille des points mise à jour à {size:.1f} sur {actors_updated} acteurs (antennes exclues)")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur taille points: {e}")
    
    def update_scene_opacity(self, opacity):
        """Met à jour l'opacité de la scène 3D (bâtiments et objets)."""
        try:
            opacity = max(0.0, min(1.0, opacity))  # S'assurer que l'opacité est entre 0 et 1
            actors_updated = 0
            
            # Mettre à jour l'opacité de tous les objets de la scène (bâtiments, etc.)
            for actor in self._scene_actors:
                if hasattr(actor, 'GetProperty'):
                    actor.GetProperty().SetOpacity(opacity)
                    actors_updated += 1
            
            # Mettre à jour l'opacité des objets individuels
            for object_name, actor in self.object_actors.items():
                if hasattr(actor, 'GetProperty'):
                    actor.GetProperty().SetOpacity(opacity)
                    actors_updated += 1
            
            # Mettre à jour l'opacité du mesh principal si présent
            if hasattr(self, 'mesh_actor') and self.mesh_actor:
                if hasattr(self.mesh_actor, 'GetProperty'):
                    self.mesh_actor.GetProperty().SetOpacity(opacity)
                    actors_updated += 1
            
            # Forcer le rendu
            self.plotter.render()
            logger.info(f"VisualizationEngine: Opacité de la scène mise à jour à {opacity:.2f} sur {actors_updated} acteurs")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur opacité scène: {e}")
    
    def set_interest_center(self, center):
        """Définit le centre d'intérêt."""
        self.interest_center = center
        logger.info(f"VisualizationEngine: Centre d'intérêt: {center}")
    
    def update_interest_radius(self, radius):
        """Met à jour le rayon d'intérêt."""
        self.interest_radius = radius
        logger.info(f"VisualizationEngine: Rayon d'intérêt: {radius}m")
    
    def switch_to_2d_mode(self, plane_name="XY (Horizontal)"):
        """Bascule en mode 2D."""
        try:
            self.is_2d_mode = True
            self.current_2d_plane = plane_name
            self._setup_2d_view(plane_name)
            logger.info(f"VisualizationEngine: Mode 2D {plane_name}")
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur mode 2D: {e}")
    
    def switch_to_3d_mode(self):
        """Bascule en mode 3D."""
        try:
            self.is_2d_mode = False
            self.plotter.reset_camera()
            logger.info("VisualizationEngine: Mode 3D")
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur mode 3D: {e}")
    
    def _setup_2d_view(self, plane_name):
        """Configure la vue 2D."""
        try:
            if plane_name == "XY (Horizontal)":
                self.plotter.view_xy()
            elif plane_name == "XZ (Vertical frontal)":
                self.plotter.view_xz()
            elif plane_name == "YZ (Vertical latéral droit)":
                self.plotter.view_yz()
            
            self.plotter.reset_camera()
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur setup 2D: {e}")
    
    # Événements Qt
    def keyPressEvent(self, event):
        """Gère les événements clavier pour le moteur."""
        try:
            # Navigation par touches fléchées pour modes 2D
            if self.is_2d_mode:
                if event.key() == Qt.Key.Key_Left:
                    self.plotter.camera.azimuth += 90
                elif event.key() == Qt.Key.Key_Right:
                    self.plotter.camera.azimuth -= 90
                elif event.key() == Qt.Key.Key_Up:
                    self.plotter.camera.elevation += 10
                elif event.key() == Qt.Key.Key_Down:
                    self.plotter.camera.elevation -= 10
                    
                self.plotter.render()
                
        except Exception as e:
            logger.debug(f"VisualizationEngine: Erreur gestion clavier: {e}")
        
        super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        """Gère le redimensionnement."""
        super().resizeEvent(event)
        try:
            if hasattr(self, 'plotter') and self.plotter:
                self.plotter.render()
        except Exception as e:
            logger.debug(f"VisualizationEngine: Erreur redimensionnement: {e}")
    
    def apply_material_color(self, material_name, color=None):
        """
        Applique une couleur de matériau à un objet spécifique.
        
        Args:
            material_name: Nom du matériau à appliquer
            color: Couleur RGB [r, g, b] ou None pour utiliser le mapping par défaut
        """
        try:
            # Utiliser la couleur fournie ou mapping par défaut
            if color and len(color) >= 3:
                # Utiliser la couleur spécifiée
                final_color = color[:3]  # Prendre seulement RGB
                logger.info(f"VisualizationEngine: Utilisation couleur spécifiée {final_color}")
            else:
                # Mapping des matériaux vers des couleurs par défaut
                material_colors = {
                    'concrete': [0.7, 0.7, 0.7],     # Gris béton
                    'brick': [0.8, 0.4, 0.2],        # Rouge brique
                    'glass': [0.6, 0.8, 0.9],        # Bleu verre
                    'metal': [0.5, 0.5, 0.6],        # Gris métallique
                    'wood': [0.6, 0.4, 0.2],         # Brun bois
                    'default': [0.8, 0.8, 0.8]       # Gris par défaut
                }
                
                final_color = material_colors.get(material_name.lower(), material_colors['default'])
                logger.info(f"VisualizationEngine: Utilisation couleur par défaut {final_color}")
            
            # Extraire le nom de l'objet depuis le nom du matériau
            # Format: "Material_Block_0/Block_0/Block_0/Block_0/Block_0" -> "Block_0/Block_0/Block_0/Block_0/Block_0"
            object_name = material_name
            if material_name.startswith("Material_"):
                object_name = material_name[9:]  # Supprimer le préfixe "Material_"
            
            # Chercher l'acteur correspondant à cet objet spécifique
            target_actor = None
            actors_updated = 0
            
            if hasattr(self, 'plotter') and self.plotter:
                # Méthode 1: Chercher dans object_actors (mapping direct)
                if hasattr(self, 'object_actors') and object_name in self.object_actors:
                    target_actor = self.object_actors[object_name]
                    if hasattr(target_actor, 'GetProperty'):
                        target_actor.GetProperty().SetColor(final_color)
                        actors_updated = 1
                        logger.info(f"VisualizationEngine: Objet {object_name} trouvé via mapping direct")
                else:
                    # Méthode 2: Chercher par nom dans tous les acteurs
                    for actor in self.plotter.renderer.GetActors():
                        if hasattr(actor, 'GetProperty'):
                            # Vérifier si c'est le bon acteur par son nom ou propriétés
                            actor_name = getattr(actor, 'name', '')
                            if actor_name == object_name or object_name in str(actor_name):
                                actor.GetProperty().SetColor(final_color)
                                actors_updated += 1
                                target_actor = actor
                                logger.info(f"VisualizationEngine: Objet {object_name} trouvé via recherche par nom")
                                break
                
                # Si aucun acteur spécifique trouvé, appliquer à tous (fallback)
                if actors_updated == 0:
                    logger.warning(f"VisualizationEngine: Objet {object_name} non trouvé, application à tous les acteurs")
                    for actor in self.plotter.renderer.GetActors():
                        if hasattr(actor, 'GetProperty'):
                            actor.GetProperty().SetColor(final_color)
                            actors_updated += 1
                
                # Forcer le rendu immédiatement
                self.plotter.render()
                logger.info(f"VisualizationEngine: Matériau {material_name} appliqué avec couleur {final_color} sur {actors_updated} acteur(s)")
            else:
                logger.warning("VisualizationEngine: Plotter non disponible pour application couleur")
            
        except Exception as e:
            logger.warning(f"VisualizationEngine: Erreur application matériau {material_name}: {e}")
    
    def enable_mesh_hover_highlight(self, enabled=True):
        """
        Active/désactive le surlignage au survol des meshes.
        
        Args:
            enabled: True pour activer, False pour désactiver
        """
        try:
            # Cette fonctionnalité peut être implémentée plus tard
            # Pour l'instant, on log juste l'état
            self.mesh_hover_enabled = enabled
            logger.debug(f"VisualizationEngine: Surlignage mesh hover {'activé' if enabled else 'désactivé'}")
            
        except Exception as e:
            logger.warning(f"VisualizationEngine: Erreur configuration mesh hover: {e}")
    
    def add_antenna_visualization(self, antenna):
        """
        Ajoute la visualisation d'une antenne à la scène.
        
        Args:
            antenna: Objet antenne à visualiser
        """
        try:
            # Obtenir les propriétés de l'antenne
            antenna_name = getattr(antenna, 'name', 'Antenne_Inconnue')
            position = getattr(antenna, 'position', [0, 0, 0])
            
            # Créer une sphère pour représenter l'antenne
            import pyvista as pv
            sphere = pv.Sphere(radius=0.5, center=position)
            
            # Ajouter l'antenne à la scène avec une couleur distinctive
            antenna_actor = self.plotter.add_mesh(
                sphere,
                color=[1.0, 0.0, 0.0],  # Rouge pour les antennes
                opacity=0.9,
                name=f"antenna_{antenna_name}"
            )
            
            # Stocker l'acteur antenne
            self.antenna_actors.append(antenna_actor)
            
            # Forcer le rendu
            self.plotter.render()
            
            logger.info(f"VisualizationEngine: Antenne {antenna_name} ajoutée à la position {position}")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur ajout antenne: {e}")
    
    def update_results_visualization(self, simulation_results, antennas, point_settings):
        """
        Met à jour la visualisation avec les résultats de simulation.
        
        Args:
            simulation_results: Dictionnaire contenant les résultats de simulation
            antennas: Liste des antennes de la simulation
            point_settings: Paramètres des points de simulation
        """
        try:
            if not simulation_results:
                logger.warning("VisualizationEngine: Résultats vides reçus")
                return
            
            # Effacer les résultats précédents s'ils existent
            if hasattr(self, 'results_actor') and self.results_actor:
                try:
                    self.plotter.remove_actor(self.results_actor)
                except:
                    pass
            
            # Log des informations reçues
            logger.info(f"VisualizationEngine: Traitement résultats avec {len(antennas) if antennas else 0} antennes")
            logger.debug(f"VisualizationEngine: Point settings: {point_settings}")
            
            # Log détaillé des clés de résultats
            logger.info(f"VisualizationEngine: Clés des résultats: {list(simulation_results.keys())}")
            for key, value in simulation_results.items():
                if hasattr(value, '__len__'):
                    logger.info(f"VisualizationEngine: {key}: {type(value)} avec {len(value)} éléments")
                else:
                    logger.info(f"VisualizationEngine: {key}: {type(value)} = {value}")
            
            # Traiter les différents types de résultats
            if 'field_strength' in simulation_results:
                self._visualize_field_strength(simulation_results['field_strength'])
            elif 'coverage_map' in simulation_results:
                self._visualize_coverage_map(simulation_results['coverage_map'])
            elif 'signal_propagation' in simulation_results:
                self._visualize_signal_propagation(simulation_results['signal_propagation'])
            elif 'heatmap' in simulation_results or 'grid' in simulation_results:
                # Chercher des données de heatmap/grille
                heatmap_data = simulation_results.get('heatmap') or simulation_results.get('grid')
                self._visualize_heatmap_data(heatmap_data)
            else:
                logger.info("VisualizationEngine: Type de résultats non reconnu, affichage générique")
                self._visualize_generic_results(simulation_results)
            
            # Forcer le rendu
            self.plotter.render()
            
            logger.info("VisualizationEngine: Résultats de simulation visualisés")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation résultats: {e}")
            import traceback
            traceback.print_exc()
    
    def _visualize_field_strength(self, field_data):
        """Visualise les données de force de champ."""
        try:
            # Implémentation basique - peut être étendue
            logger.info("VisualizationEngine: Visualisation de la force de champ")
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation force de champ: {e}")
    
    def _visualize_coverage_map(self, coverage_data):
        """Visualise la carte de couverture."""
        try:
            # Implémentation basique - peut être étendue
            logger.info("VisualizationEngine: Visualisation de la carte de couverture")
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation couverture: {e}")
    
    def _visualize_signal_propagation(self, propagation_data):
        """Visualise la propagation du signal."""
        try:
            # Implémentation basique - peut être étendue
            logger.info("VisualizationEngine: Visualisation de la propagation du signal")
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation propagation: {e}")
    
    def _visualize_heatmap_data(self, heatmap_data):
        """Visualise les données de heatmap."""
        try:
            if heatmap_data is None:
                logger.warning("VisualizationEngine: Données de heatmap nulles")
                return
            
            logger.info(f"VisualizationEngine: Visualisation heatmap avec données {type(heatmap_data)}")
            
            # Si c'est un dictionnaire, chercher les coordonnées et valeurs
            if isinstance(heatmap_data, dict):
                points = None
                values = None
                
                for key, value in heatmap_data.items():
                    logger.info(f"VisualizationEngine: Heatmap {key}: {type(value)}")
                    if 'coord' in key.lower() or 'point' in key.lower():
                        points = value
                    elif 'value' in key.lower() or 'power' in key.lower() or 'signal' in key.lower():
                        values = value
                
                if points is not None:
                    self._visualize_simulation_points(points, values)
                else:
                    logger.warning("VisualizationEngine: Pas de coordonnées trouvées dans la heatmap")
            else:
                logger.warning(f"VisualizationEngine: Format de heatmap non supporté: {type(heatmap_data)}")
                
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation heatmap: {e}")
            import traceback
            traceback.print_exc()
    
    def _visualize_generic_results(self, results):
        """Visualisation générique pour tout type de résultats."""
        try:
            # Affichage basique des résultats
            logger.info(f"VisualizationEngine: Résultats génériques reçus avec {len(results)} éléments")
            
            # Essayer de trouver des données de points de simulation
            simulation_points = None
            simulation_values = None
            
            for key, value in results.items():
                logger.debug(f"VisualizationEngine: {key}: {type(value)}")
                
                # Chercher des données de points/coordonnées
                if 'points' in key.lower() or 'coordinates' in key.lower():
                    simulation_points = value
                elif 'values' in key.lower() or 'power' in key.lower() or 'dbm' in key.lower():
                    simulation_values = value
                elif hasattr(value, '__len__') and len(value) > 0:
                    # Si c'est une liste/array, essayer de l'interpréter
                    if isinstance(value, (list, tuple)) and len(value) > 0:
                        first_item = value[0]
                        if hasattr(first_item, '__len__') and len(first_item) >= 3:
                            # Probable que ce soit des coordonnées
                            simulation_points = value
                        elif isinstance(first_item, (int, float)):
                            # Probable que ce soit des valeurs
                            simulation_values = value
            
            # Si on a trouvé des points, les visualiser
            if simulation_points is not None:
                self._visualize_simulation_points(simulation_points, simulation_values)
            else:
                logger.warning("VisualizationEngine: Aucun point de simulation trouvé dans les résultats")
                
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation générique: {e}")
            import traceback
            traceback.print_exc()
    
    def initialize_empty_scene(self):
        """
        Initialise une scène vide.
        """
        try:
            # Effacer la scène actuelle
            self.clear_scene()
            
            # Réinitialiser la caméra
            self.plotter.reset_camera()
            
            # Remettre les axes et la grille
            self.plotter.add_axes()
            self.plotter.show_grid()
            
            logger.info("VisualizationEngine: Scène vide initialisée")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur initialisation scène vide: {e}")
    
    def clear_results(self):
        """
        Efface tous les résultats de simulation de la visualisation.
        """
        try:
            results_cleared = 0
            
            # Effacer l'acteur de résultats principal
            if hasattr(self, 'results_actor') and self.results_actor:
                try:
                    self.plotter.remove_actor(self.results_actor)
                    self.results_actor = None
                    results_cleared += 1
                except Exception as e:
                    logger.debug(f"VisualizationEngine: Erreur suppression results_actor: {e}")
            
            # Effacer les antennes
            for actor in self.antenna_actors[:]:  # Copie pour éviter la modification pendant l'itération
                try:
                    self.plotter.remove_actor(actor)
                    results_cleared += 1
                except Exception as e:
                    logger.debug(f"VisualizationEngine: Erreur suppression antenne: {e}")
            self.antenna_actors.clear()
            
            # Effacer les acteurs de couverture
            for actor in self.antenna_coverage_actors[:]:
                try:
                    self.plotter.remove_actor(actor)
                    results_cleared += 1
                except Exception as e:
                    logger.debug(f"VisualizationEngine: Erreur suppression couverture: {e}")
            self.antenna_coverage_actors.clear()
            
            # Effacer les acteurs de rayon
            for actor in self.antenna_radius_actors[:]:
                try:
                    self.plotter.remove_actor(actor)
                    results_cleared += 1
                except Exception as e:
                    logger.debug(f"VisualizationEngine: Erreur suppression rayon: {e}")
            self.antenna_radius_actors.clear()
            
            # Effacer la barre scalaire si présente
            if hasattr(self, 'scalar_bar_actor') and self.scalar_bar_actor:
                try:
                    self.plotter.remove_actor(self.scalar_bar_actor)
                    self.scalar_bar_actor = None
                    results_cleared += 1
                except Exception as e:
                    logger.debug(f"VisualizationEngine: Erreur suppression barre scalaire: {e}")
            
            # Vider les données de couverture
            self.antenna_coverage_data.clear()
            
            # Forcer le rendu
            self.plotter.render()
            
            logger.info(f"VisualizationEngine: {results_cleared} éléments de résultats effacés")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur effacement résultats: {e}")
            import traceback
            traceback.print_exc()
    
    def _visualize_simulation_points(self, points, values=None):
        """
        Visualise les points de simulation avec leurs valeurs.
        
        Args:
            points: Array ou liste de coordonnées [x, y, z]
            values: Array optionnel de valeurs associées aux points
        """
        try:
            import numpy as np
            import pyvista as pv
            
            # Convertir les points en array numpy
            if not isinstance(points, np.ndarray):
                points = np.array(points)
            
            if points.shape[0] == 0:
                logger.warning("VisualizationEngine: Aucun point à visualiser")
                return
            
            # S'assurer que nous avons des coordonnées 3D
            if points.shape[1] < 3:
                logger.warning("VisualizationEngine: Points sans coordonnées 3D complètes")
                return
            
            # Créer un cloud de points PyVista
            point_cloud = pv.PolyData(points[:, :3])
            
            # Ajouter les valeurs si disponibles
            if values is not None:
                if not isinstance(values, np.ndarray):
                    values = np.array(values)
                
                if len(values) == len(points):
                    point_cloud['signal_strength'] = values
                    point_cloud.set_active_scalars('signal_strength')
                    
                    # Visualiser avec une colormap
                    self.results_actor = self.plotter.add_mesh(
                        point_cloud,
                        scalars='signal_strength',
                        point_size=8.0,
                        render_points_as_spheres=True,
                        cmap='viridis',  # Colormap viridis (bleu->vert->jaune)
                        opacity=0.8,
                        name="simulation_results"
                    )
                    
                    # Ajouter une barre de couleur
                    self.plotter.add_scalar_bar(
                        title="Signal Strength (dBm)",
                        n_labels=5,
                        position_x=0.85,
                        position_y=0.1
                    )
                    
                    logger.info(f"VisualizationEngine: {len(points)} points de simulation visualisés avec valeurs")
                else:
                    logger.warning("VisualizationEngine: Nombre de valeurs ne correspond pas au nombre de points")
                    # Visualiser sans valeurs
                    self._visualize_points_without_values(point_cloud)
            else:
                # Visualiser sans valeurs
                self._visualize_points_without_values(point_cloud)
                
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation points de simulation: {e}")
            import traceback
            traceback.print_exc()
    
    def _visualize_points_without_values(self, point_cloud):
        """Visualise les points sans valeurs associées."""
        try:
            self.results_actor = self.plotter.add_mesh(
                point_cloud,
                color=[1.0, 0.5, 0.0],  # Orange pour les points sans valeurs
                point_size=6.0,
                render_points_as_spheres=True,
                opacity=0.7,
                name="simulation_points"
            )
            
            logger.info(f"VisualizationEngine: {point_cloud.n_points} points de simulation visualisés sans valeurs")
            
        except Exception as e:
            logger.error(f"VisualizationEngine: Erreur visualisation points sans valeurs: {e}")
