"""
Adaptateur entre l'interface graphique et le backend de l'application.
Fournit une API simplifiée pour l'interface utilisateur.
"""

import logging
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from core.application.simulation_orchestrator import SimulationOrchestrator
from core.infrastructure.file_loader import FileLoader
from core.domain.antenna_factory import AntennaFactory

logger = logging.getLogger(__name__)

class FileLoaderWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            loader = FileLoader()
            scene = loader.load_file(self.file_path)
            self.finished.emit(scene)
        except Exception as e:
            self.error.emit(str(e))

class BackendAdapter(QObject):
    """Adaptateur entre la GUI et le backend."""
    
    # Signaux pour communiquer avec la GUI
    scene_loaded = pyqtSignal(object)  # Émet la scène chargée
    antenna_added = pyqtSignal(object)  # Émet l'antenne ajoutée
    antenna_selected = pyqtSignal(object)  # Émet la liste des antennes sélectionnées
    simulation_started = pyqtSignal()
    simulation_progress = pyqtSignal(int, str)  # Progrès (0-100), message
    simulation_finished = pyqtSignal(object)  # Émet les résultats
    error_occurred = pyqtSignal(str)  # Émet un message d'erreur
    
    def __init__(self):
        super().__init__()
        logger.debug("BackendAdapter: Initialisation...")
        
        self.orchestrator = SimulationOrchestrator()
        self.file_loader = FileLoader()
        self.antenna_factory = AntennaFactory()
        self.current_scene = None
        self.antennas = []
        self.selected_antennas = []
        self.last_simulation_results = None
        logger.info("BackendAdapter: Initialisation terminée")

    def load_scene_async(self, file_path):
        """Charge une scène de manière asynchrone."""
        try:
            logger.info(f"BackendAdapter: Chargement asynchrone de la scène depuis {file_path}")
            self.loading_thread = QThread()
            self.loading_worker = FileLoaderWorker(file_path)
            self.loading_worker.moveToThread(self.loading_thread)
            
            self.loading_thread.started.connect(self.loading_worker.run)
            self.loading_worker.finished.connect(self.loading_thread.quit)
            self.loading_worker.finished.connect(self.loading_worker.deleteLater)
            self.loading_thread.finished.connect(self.loading_thread.deleteLater)
            self.loading_worker.finished.connect(self.on_scene_loaded_async)
            self.loading_worker.error.connect(self.on_scene_load_error_async)
            
            self.loading_thread.start()
        except Exception as e:
            error_msg = f"Erreur lors du chargement asynchrone: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)

    def on_scene_loaded_async(self, scene):
        """Callback asynchrone lorsque la scène est chargée."""
        self.current_scene = scene
        self.scene_loaded.emit(scene)
        logger.info(f"BackendAdapter: Scène chargée avec succès (async)")

    def on_scene_load_error_async(self, error_msg):
        """Callback asynchrone en cas d'erreur de chargement."""
        logger.error(f"BackendAdapter: Erreur de chargement async: {error_msg}")
        self.error_occurred.emit(error_msg)

    def load_scene(self, file_path):
        """Charge une scène depuis un fichier."""
        try:
            logger.info(f"BackendAdapter: Chargement de la scène depuis {file_path}")
            scene = self.file_loader.load_file(file_path)
            self.current_scene = scene
            self.scene_loaded.emit(scene)
            logger.info(f"BackendAdapter: Scène chargée avec succès depuis {file_path}")
        except Exception as e:
            error_msg = f"Erreur lors du chargement de la scène '{file_path}': {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise

    def add_antenna(self, antenna):
        """Ajoute une antenne à la simulation."""
        try:
            logger.info(f"BackendAdapter: Ajout de l'antenne {antenna.name}")
            self.antennas.append(antenna)
            self.antenna_added.emit(antenna)
            logger.info(f"BackendAdapter: Antenne {antenna.name} ajoutée avec succès")
        except Exception as e:
            error_msg = f"Erreur lors de l'ajout de l'antenne '{antenna.name}': {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise

    def select_antenna(self, antenna_ids):
        """Sélectionne les antennes par leurs IDs."""
        try:
            logger.info(f"BackendAdapter: Sélection des antennes {antenna_ids}")
            self.selected_antennas = [ant for ant in self.antennas if ant.name in antenna_ids]
            self.antenna_selected.emit(self.selected_antennas)
            logger.info(f"BackendAdapter: {len(self.selected_antennas)} antennes sélectionnées")
        except Exception as e:
            error_msg = f"Erreur lors de la sélection des antennes: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise

    def start_simulation(self, config=None):
        """Démarre la simulation avec la configuration donnée."""
        try:
            logger.info("BackendAdapter: Démarrage de la simulation")
            self.simulation_started.emit()

            if not self.current_scene:
                raise ValueError("Aucune scène chargée")
            if not self.selected_antennas:
                raise ValueError("Aucune antenne sélectionnée")

            # Utiliser la configuration fournie ou une configuration par défaut
            if config is None:
                config = {
                    "resolution": 1.0,
                    "height_levels": 3,
                    "propagation_model": "free_space",
                    "rf_calculator_backend": "optimized"
                }

            # Configurer la simulation
            self.orchestrator.set_scene(self.current_scene)
            self.orchestrator.set_antennas(self.selected_antennas)

            # Connecter les callbacks de progression
            def progress_callback(progress, message):
                self.simulation_progress.emit(progress, message)

            # Exécuter la simulation
            results = self.orchestrator.start_simulation(
                config,
                progress_callback=progress_callback,
                selected_antennas=self.selected_antennas
            )

            simulation_data = {
                'results': results,
                'antennas': self.antennas.copy()
            }

            self.last_simulation_results = simulation_data
            self.simulation_finished.emit(simulation_data)
            logger.info("BackendAdapter: Simulation terminée avec succès")
        except Exception as e:
            error_msg = f"Erreur lors du démarrage de la simulation: {e}"
            logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            raise

    def get_antennas(self):
        """Retourne la liste des antennes."""
        return self.antennas.copy()