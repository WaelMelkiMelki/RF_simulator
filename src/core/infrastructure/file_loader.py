# src/core/infrastructure/file_loader.py
"""
Chargeur de fichiers pour la simulation RF.
Gère le chargement de différents formats de fichiers 3D.
"""

import logging
import pyvista as pv
import os
from core.domain.scene import Scene3D
from PyQt6.QtCore import QThread, pyqtSignal, QObject

logger = logging.getLogger(__name__)

class FileLoaderWorker(QObject):
    """Worker pour charger les fichiers en arrière-plan."""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            logger.info(f"FileLoaderWorker: Chargement du fichier {self.file_path}")
            
            # Charger les données avec PyVista
            data = pv.read(self.file_path)
            
            # Créer une scène
            scene = Scene3D()
            scene.load_from_data(data)
                
            logger.info(f"FileLoaderWorker: Fichier chargé avec succès")
            self.finished.emit(scene)
            
        except Exception as e:
            logger.error(f"FileLoaderWorker: Erreur lors du chargement: {e}")
            self.error.emit(str(e))

class FileLoader:
    """Chargeur de fichiers 3D pour la simulation avec cache."""

    def __init__(self):
        self._cache = {}  # file_path -> (timestamp, scene_data)

    def load_file_async(self, file_path: str):
        self.worker = FileLoaderWorker(file_path)
        self.thread = QThread()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.error.connect(self.thread.quit)
        return self.thread, self.worker

    def load_file(self, file_path: str) -> Scene3D:
        """
        Charge un fichier 3D et retourne une scène (synchrone), avec cache.
        """
        import time
        try:
            # Vérifier le cache
            if file_path in self._cache:
                logger.info(f"FileLoader: Chargement depuis le cache {file_path}")
                # Retourne une copie pour éviter les effets de bord
                cached_scene = self._cache[file_path][1]
                import copy
                return copy.deepcopy(cached_scene)

            logger.info(f"Chargement de {file_path}")

            # Vérification préalable des fichiers binaires pour GLTF
            if file_path.lower().endswith((".gltf", ".glb")):
                self._validate_gltf_files(file_path)

            data = pv.read(file_path)
            scene = Scene3D()
            scene.load_from_data(data)

            # Stocker dans le cache
            self._cache[file_path] = (time.time(), scene)

            logger.info(f"FileLoader: Fichier chargé avec succès")
            return scene

        except Exception as e:
            # Gestion spécifique des erreurs GLTF
            if "Failed to open file" in str(e) and ".bin" in str(e):
                error_msg = f"Fichier binaire manquant pour {file_path}. Assurez-vous que tous les fichiers .bin sont présents."
                logger.error(error_msg)
                raise Exception(error_msg) from e
            else:
                logger.error(f"FileLoader: Erreur lors du chargement: {e}")
                raise

    def _validate_gltf_files(self, file_path: str):
        import os, json
        if file_path.lower().endswith(".gltf"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    gltf_data = json.load(f)
                for buffer in gltf_data.get("buffers", []):
                    uri = buffer.get("uri", "")
                    if uri.endswith(".bin"):
                        bin_path = os.path.join(os.path.dirname(file_path), uri)
                        if not os.path.exists(bin_path):
                            raise FileNotFoundError(f"Fichier binaire .bin manquant: {bin_path}")
            except Exception as e:
                logger.error(f"Erreur de validation GLTF: {e}")
                raise