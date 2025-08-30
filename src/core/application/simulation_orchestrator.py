# src/core/application/simulation_orchestrator.py
import logging
logger = logging.getLogger(__name__)
import time
from concurrent.futures import ThreadPoolExecutor
from core.domain.scene import Scene3D
from core.domain.antenna import BaseAntenna
from core.infrastructure.file_loader import FileLoader
from core.domain.rf_models import PropagationStrategy
from core.application.optimized_rf_calculator import OptimizedRFCalculator
from core.application.data_validator import DataValidator, DataValidationError
from core.infrastructure.grid_generator import GridGenerator
from core.infrastructure.cache_manager import SimulationCache
from extensions.application.memory_manager import MemoryManager
from core.infrastructure.performance_monitor import PerformanceMonitor


class SimulationOrchestrator:
    def start(self, config=None):
        """
        Démarre le processus de simulation.
        Args:
            config (dict): Configuration de la simulation.
        """
        try:
            logger.info("SimulationOrchestrator: Démarrage de la simulation")
            self.is_running = True
            # Charger la configuration
            if config is None:
                config = {}
            resolution = config.get("resolution", 1.0)  # Utiliser la résolution de la config
            height_levels = config.get("height_levels", 3)
            propagation_model = config.get("propagation_model", "free_space")
            rf_calculator_backend = config.get("rf_calculator_backend", "optimized")
            logger.info(f"SimulationOrchestrator: Paramètres - Résolution={resolution}m, Niveaux={height_levels}")
            # Validation des données
            logger.info("SimulationOrchestrator: Étape 1/5 - Validation des données...")
            self.validate_data()
            # Pré-traitement
            logger.info("SimulationOrchestrator: Étape 2/5 - Pré-traitement...")
            # ... (votre code de pré-traitement) ...
            # Calculs RF
            logger.info("SimulationOrchestrator: Étape 3/5 - Calculs RF...")
            calculator = OptimizedRFCalculator(self.scene, self.antennas, propagation_model)
            # Utilisez directement la résolution de la configuration
            results = calculator.calculate_coverage_grid_detailed(resolution=resolution)
            # ... (le reste du code de post-traitement et d'envoi des résultats) ...
            return results
        except Exception as e:
            logger.error(f"SimulationOrchestrator: Erreur lors de la simulation: {e}")
            raise
    """Orchestrateur principal de la simulation RF."""

    def __init__(self):
        logger.debug("DEBUG: Création d'une nouvelle instance de SimulationOrchestrator")
        self.scene = None
        self.antennas = []
        self.config = None
        self.is_running = False
        self.cache = SimulationCache()
        self.memory_manager = MemoryManager()
        self.performance_monitor = PerformanceMonitor()
        self.file_loader = FileLoader()

    def validate_data(self, config: dict = None):
        """
        Valide les données de la scène, des antennes et de la configuration.
        Utilise DataValidator pour effectuer les vérifications.
        Args:
            config (dict, optional): Configuration de la simulation.
        """
        logger.info("SimulationOrchestrator: Validation des données...")
        validator = DataValidator()
        try:
            validator.validate_all(self.scene, self.antennas, config)
            logger.info("SimulationOrchestrator: Toutes les données sont valides.")
            return True
        except DataValidationError as e:
            logger.error(f"SimulationOrchestrator: Erreur de validation des données: {e}")
            raise e
        except Exception as e:
            logger.error(f"SimulationOrchestrator: Erreur inattendue lors de la validation: {e}")
            raise e

    def load_scene(self, file_path: str) -> Scene3D:
        scene = self.file_loader.load_file(file_path)
        self.scene = scene
        return self.scene

    def set_scene(self, scene: Scene3D):
        """
        Définit la scène 3D utilisée pour la simulation.
        """
        self.scene = scene

    def add_antenna(self, antenna: BaseAntenna) -> None:
        """
        Ajoute une antenne à la simulation.
        
        Args:
            antenna (BaseAntenna): Instance d'antenne à ajouter
        """
        self.antennas.append(antenna)
        logger.info(f"SimulationOrchestrator: Antenne '{antenna.name}' ajoutée")

    def set_antennas(self, antennas):
        """Configure les antennes pour la simulation."""
        self.antennas = antennas
        logger.info(f"SimulationOrchestrator: {len(antennas)} antennes configurées")

    def start_simulation(self, config: dict, progress_callback=None, selected_antennas=None) -> dict:
        if not self.scene or not self.antennas:
            raise ValueError("Scene or antennas not configured")

        self.is_running = True
        self.config = config

        try:
            logger.info("SimulationOrchestrator: Étape 1/5 - Validation des données...")
            self.validate_data()

            # Sélection des antennes (si none, toutes)
            if selected_antennas is None or not selected_antennas:
                selected_antennas = self.antennas[:] if self.antennas else []

            logger.info(f"SimulationOrchestrator: {len(selected_antennas)} antennes sélectionnées pour la simulation")
            for ant in selected_antennas:
                logger.debug(f"SimulationOrchestrator: Antenne sélectionnée: {ant.name}")

            logger.info("SimulationOrchestrator: Étape 2/5 - Pré-traitement...")
            mesh = self.scene.get_pyvista_mesh() if hasattr(self.scene, 'get_pyvista_mesh') else self.scene.mesh

            rf_backend = config.get("rf_calculator_backend", "optimized").lower()
            heatmap_mode = config.get("visualization_mode", "heatmap")  # Nouveau paramètre
            results = {}
            if rf_backend == "optimized":
                logger.info("SimulationOrchestrator: Étape 3/5 - Calculs RF avec OptimizedRFCalculator...")
                try:
                    propagation_model = self._get_propagation_model(
                        config.get("propagation_model", "ray_tracing"),
                        config  # Passer la configuration complète
                    )
                    rf_calculator = OptimizedRFCalculator(
                        scene=self.scene,
                        antennas=selected_antennas,
                        propagation_model=propagation_model
                    )
                    # CORRECTION: Calculer la heatmap détaillée
                    if heatmap_mode == "heatmap":
                        logger.info("SimulationOrchestrator: Calcul de la heatmap détaillée...")
                        results = rf_calculator.calculate_coverage_grid_detailed(
                            resolution=config.get("resolution", 1.0)
                        )
                    else:
                        # Mode par antenne (ancien mode)
                        results = {}
                        for ant in selected_antennas:
                            pattern = rf_calculator.calculate_radiation_pattern(ant)
                            results[ant.name] = pattern
                    logger.info("SimulationOrchestrator: Calculs RF avec OptimizedRFCalculator terminés.")
                    self.is_running = False
                    return results
                except Exception as e:
                    logger.error(f"SimulationOrchestrator: Erreur avec OptimizedRFCalculator: {e}")
                    import traceback
                    traceback.print_exc()
                    self.is_running = False
                    raise

            elif rf_backend == "pytorch":
                logger.info("SimulationOrchestrator: Étape 3/5 - Calculs RF avec PyTorchSimulationOrchestrator...")
                try:
                    from extensions.application.pytorch_orchestrator import PyTorchSimulationOrchestrator
                    from extensions.domain.rf_models_pytorch import PyTorchPropagationModel
                    import numpy as np
                    scene_tensor = self.scene.to_tensor('cpu')
                    pytorch_propagation_model = PyTorchPropagationModel(scene_tensor)
                    grid_array = np.array(GridGenerator.generate(
                        mesh.bounds,
                        resolution=config.get("resolution", 1.0),
                        height_levels=config.get("height_levels", 3)
                    ), dtype=np.float32)
                    pytorch_orch = PyTorchSimulationOrchestrator(num_workers=0)
                    coverage_values = pytorch_orch.calculate_coverage(
                        grid_points=grid_array,
                        antennas=selected_antennas,
                        scene_tensor=scene_tensor,
                        propagation_model=pytorch_propagation_model
                    )
                    logger.info("SimulationOrchestrator: Conversion des résultats PyTorch au format standard...")
                    points = grid_array.tolist()
                    values = coverage_values.tolist()
                    results = {'points': points, 'values': values}
                    logger.info("SimulationOrchestrator: Calculs RF avec PyTorchSimulationOrchestrator terminés.")
                    self.is_running = False
                    return results
                except ImportError as e:
                    logger.error(f"SimulationOrchestrator: PyTorch non disponible ou erreur d'import: {e}")
                    logger.info("SimulationOrchestrator: Retour au backend par défaut.")
                except Exception as e:
                    logger.error(f"SimulationOrchestrator: Erreur avec PyTorchSimulationOrchestrator, retour au mode par défaut: {e}")
                    import traceback
                    traceback.print_exc()

            logger.info("SimulationOrchestrator: Étape 3/5 - Calculs RF (mode par défaut)...")
            voxel_size = config.get("voxel_size")
            if voxel_size is not None:
                grid = GridGenerator.generate(mesh.bounds, voxel_size=voxel_size)
            else:
                grid = GridGenerator.generate(
                    mesh.bounds,
                    resolution=config.get("resolution", 1.0),
                    height_levels=config.get("height_levels", 3)
                )
            logger.info(f"SimulationOrchestrator: Grille générée: {len(grid)} points")
            propagation_model = self._get_propagation_model(
                config.get("propagation_model", "free_space"),
                config  # Passer la configuration complète
            )
            total_points = len(grid)
            completed = 0
            coverage = []
            with self.performance_monitor.track_performance("simulation"):
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = []
                    for point in grid:
                        futures.append(executor.submit(
                            self._calculate_point_coverage,
                            point,
                            propagation_model
                        ))
                    for future in futures:
                        if not self.is_running:
                            break
                        coverage.append(future.result())
                        completed += 1
                        if completed % 100 == 0:
                            self.memory_manager.limit_memory(2000)
                            if progress_callback:
                                progress = int((completed / total_points) * 100)
                                progress_callback(progress, f"Calcul en cours... {completed}/{total_points}")
            points = [c['position'] for c in coverage]
            values = [c['signal_strength'] for c in coverage]
            results = {'points': points, 'values': values}
            logger.info("SimulationOrchestrator: Étape 4/5 - Post-traitement des résultats...")
            logger.info("SimulationOrchestrator: Étape 5/5 - Mise en cache des résultats...")
            if progress_callback:
                progress_callback(100, "Génération des résultats...")
            params = {
                "scene": str(self.scene),
                "antennas": [str(a) for a in self.antennas],
                "config": config
            }
            self.cache.cache_results(params, results)
            self.is_running = False
            auto_export_flag = config.get("auto_export", False)
            logger.debug(f"[DEBUG] Vérification de auto_export: flag={auto_export_flag}")
            if auto_export_flag:
                logger.debug("[DEBUG] auto_export est True, tentative d'export...")
                try:
                    export_formats = config.get("export_formats", ["csv"])
                    logger.debug(f"[DEBUG] Formats d'export configurés: {export_formats}")
                    import time
                    default_export_path = f"simulation_results_{int(time.time())}"
                    export_path = config.get("export_path", default_export_path)
                    logger.debug(f"[DEBUG] Chemin d'export de base: {export_path}")
                    self.export_results(results, export_formats, export_path, config)
                    logger.debug("[DEBUG] Méthode export_results appelée.")
                except Exception as e:
                    logger.error(f"[ERREUR] Erreur lors de l'appel à export_results: {e}")
                    import traceback
                    traceback.print_exc()
            return results
        except DataValidationError:
            self.is_running = False
            raise
        except Exception as e:
            self.is_running = False
            logger.error(f"SimulationOrchestrator: Erreur fatale dans start_simulation: {e}")
            raise e

    def run_simulation(self, resolution=1.0):
        """Exécute la simulation complète."""
        try:
            logger.info("SimulationOrchestrator: Démarrage de la simulation")
            # Étape 1: Validation des données
            logger.info("SimulationOrchestrator: Étape 1/5 - Validation des données...")
            self.validate_data()
            # Étape 2: Pré-traitement
            logger.info("SimulationOrchestrator: Étape 2/5 - Pré-traitement...")
            # (Ajoutez ici le pré-traitement si nécessaire)
            # Étape 3: Calculs RF
            logger.info("SimulationOrchestrator: Étape 3/5 - Calculs RF...")
            rf_results = self._calculate_rf(resolution=resolution)
            # Étape 4: Post-traitement
            logger.info("SimulationOrchestrator: Étape 4/5 - Post-traitement...")
            # (Ajoutez ici le post-traitement si nécessaire)
            # Étape 5: Export des résultats
            logger.info("SimulationOrchestrator: Étape 5/5 - Export des résultats...")
            # (Ajoutez ici l'export si nécessaire)
            logger.info("SimulationOrchestrator: Simulation terminée avec succès")
            return rf_results
        except Exception as e:
            logger.error(f"SimulationOrchestrator: Erreur lors de la simulation: {e}")
            raise

    def _calculate_rf(self, resolution=1.0):
        """Calcule les valeurs RF avec la résolution donnée."""
        try:
            logger.info("SimulationOrchestrator: Calcul des valeurs RF...")
            calculator = OptimizedRFCalculator(
                self.scene,
                self.antennas,
                self.config.get("propagation_model", "free_space")
            )
            logger.info(f"SimulationOrchestrator: Calcul de la heatmap détaillée avec résolution {resolution}m...")
            heatmap_data = calculator.calculate_coverage_grid_detailed(resolution=resolution)
            logger.info("SimulationOrchestrator: Calculs RF terminés")
            return heatmap_data
        except Exception as e:
            logger.error(f"SimulationOrchestrator: Erreur lors du calcul RF: {e}")
            raise

    def _get_propagation_model(self, model_name: str, config: dict = None) -> PropagationStrategy:
        from core.domain.rf_models import FreeSpaceModel, MaterialAwareModel, OkumuraHataModel, ITUIndoorModel
        # Récupérer la configuration du modèle de propagation
        model_config = config.get("propagation_model_config", {}) if config else {}
        if model_name == "material_aware" or model_name == "ray_tracing":
            max_reflections = model_config.get("max_reflections", 3)
            return MaterialAwareModel(max_reflections=max_reflections)
        elif model_name == "okumura_hata":
            h_b = model_config.get("h_b", 30.0)  # Hauteur antenne base
            h_m = model_config.get("h_m", 1.5)   # Hauteur antenne mobile
            environment = model_config.get("environment", "urbain")
            return OkumuraHataModel(h_b=h_b, h_m=h_m, environment=environment)
        elif model_name == "itu_indoor":
            n = model_config.get("n", 28)        # Facteur de perte de distance
            pf = model_config.get("pf", 0)       # Facteur de perte par plancher
            environment = model_config.get("environment", "residential")
            return ITUIndoorModel(n=n, pf=pf, environment=environment)
        else:  # free_space par défaut
            return FreeSpaceModel()

    def _calculate_point_coverage(self, point, propagation_model):
        total_signal = 0
        for antenna in self.antennas:
            loss = propagation_model.calculate_path_loss(
                antenna.position,
                point,
                self.scene,
                antenna.frequency
            )
            rssi = antenna.power_dbm - loss
            total_signal += rssi
        return {
            "position": point,
            "signal_strength": total_signal
        }

    def export_results(self, results, formats, base_path, config=None):
        """
        Exporte les résultats de la simulation en utilisant ExportManager.
        """
        logger.debug(f"[DEBUG] export_results appelée avec: formats={formats}, base_path={base_path}")
        try:
            from core.application.exporter import ExportManager
            logger.debug("[DEBUG] ExportManager importé avec succès.")
        except ImportError as e:
            logger.error(f"[ERREUR] Impossible d'importer ExportManager: {e}")
            return

        try:
            exporter = ExportManager()
            logger.debug(f"[DEBUG] ExportManager instancié: {exporter}")

            export_config = config.copy() if config else {}
            export_config.update({
                'simulation_config': config,
                'antennas': [{'type': type(antenna).__name__, 'position': antenna.position, 'frequency': antenna.frequency, 'power_dbm': antenna.power_dbm} for antenna in self.antennas] if self.antennas else [],
                'scene_mesh': self.scene.mesh if self.scene and hasattr(self.scene, 'mesh') else None
            })
            logger.debug(f"[DEBUG] Configuration d'export préparée.")

            logger.debug(f"[DEBUG] Appel de exporter.batch_export avec base_path='{base_path}', formats={formats}")
            paths = exporter.batch_export(results, base_path, formats, export_config)
            logger.debug(f"[DEBUG] Export réussi. Fichiers créés: {paths}")

        except Exception as e:
            logger.error(f"[ERREUR] Une erreur s'est produite lors de l'export: {e}")
            import traceback
            traceback.print_exc()