# src/core/infrastructure/parallel_engine.py
"""
Moteur d'exécution parallèle pour les tâches de simulation.
Utilise le multiprocessing pour distribuer les calculs.
"""

import multiprocessing as mp
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Callable, Iterable, Any, List
import os

# Configuration du logger pour ce module
logger = logging.getLogger(__name__)

class ParallelEngine:
    """
    Gère l'exécution parallèle de tâches à l'aide de ProcessPoolExecutor.
    Permet de configurer le nombre de workers et d'exécuter des fonctions
    sur des itérables de données.
    """

    def __init__(self, max_workers: int = None):
        """
        Initialise le moteur parallèle.

        Args:
            max_workers (int, optional): Nombre maximum de processus workers.
                                         Si None, utilise le nombre de CPUs du système.
        """
        if max_workers is None:
            # Utiliser un nombre raisonnable de workers, par exemple le nombre de CPU
            # ou un nombre légèrement inférieur pour ne pas saturer la machine.
            self.max_workers = max(1, os.cpu_count() - 1)
        else:
            self.max_workers = max(1, max_workers)
            
        logger.info(f"ParallelEngine initialisé avec max_workers={self.max_workers}")

    def get_worker_count(self) -> int:
        """
        Renvoie le nombre de workers configurés.

        Returns:
            int: Le nombre de workers.
        """
        return self.max_workers

    def map(self, func: Callable, iterable: Iterable, chunksize: int = 1) -> List[Any]:
        """
        Applique une fonction à chaque élément d'un itérable en parallèle.

        Args:
            func (Callable): La fonction à appliquer.
            iterable (Iterable): L'itérable d'éléments.
            chunksize (int): Taille des morceaux à envoyer aux workers.

        Returns:
            List[Any]: Une liste des résultats, dans le même ordre que l'itérable d'entrée.
        """
        logger.debug(f"Démarrage de ParallelEngine.map avec {len(iterable) if hasattr(iterable, '__len__') else 'N/A'} éléments.")
        results = []
        try:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # map retourne les résultats dans l'ordre
                results = list(executor.map(func, iterable, chunksize=chunksize))
            logger.debug("ParallelEngine.map terminé avec succès.")
        except Exception as e:
            logger.error(f"Erreur dans ParallelEngine.map: {e}")
            raise
        return results

    def submit(self, func: Callable, *args, **kwargs):
        """
        Soumet une tâche unique pour exécution asynchrone.

        Args:
            func (Callable): La fonction à exécuter.
            *args: Arguments positionnels pour la fonction.
            **kwargs: Arguments nommés pour la fonction.

        Returns:
            concurrent.futures.Future: Un objet Future représentant la tâche.
        """
        logger.debug("Soumission d'une tâche unique au ParallelEngine.")
        try:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                future = executor.submit(func, *args, **kwargs)
            logger.debug("Tâche unique soumise.")
            return future
        except Exception as e:
            logger.error(f"Erreur lors de la soumission de la tâche: {e}")
            raise

    # --- Exemple de méthode utilitaire pour des calculs spécifiques ---
    # Cette méthode est plus spécifique à un cas d'usage et peut être adaptée.
    def compute_on_chunks(self, func: Callable, data_chunks: List, initializer=None, initargs=()):
        """
        Exécute une fonction sur une liste de "chunks" de données en parallèle.
        Utile pour des tâches où les données sont déjà découpées.

        Args:
            func (Callable): La fonction à exécuter sur chaque chunk.
                             Doit prendre un seul argument (le chunk).
            data_chunks (List): Une liste de chunks de données.
            initializer (Callable, optional): Fonction d'initialisation pour chaque worker.
            initargs (tuple, optional): Arguments pour la fonction d'initialisation.

        Returns:
            List[Any]: Une liste des résultats pour chaque chunk.
        """
        logger.debug(f"Démarrage de compute_on_chunks avec {len(data_chunks)} chunks.")
        results = [None] * len(data_chunks)
        try:
            with ProcessPoolExecutor(
                max_workers=self.max_workers,
                initializer=initializer,
                initargs=initargs
            ) as executor:
                # Soumettre toutes les tâches
                future_to_index = {
                    executor.submit(func, chunk): i for i, chunk in enumerate(data_chunks)
                }
                
                # Récupérer les résultats au fur et à mesure
                for future in as_completed(future_to_index):
                    index = future_to_index[future]
                    try:
                        result = future.result()
                        results[index] = result
                    except Exception as e:
                        logger.error(f"Erreur lors du calcul du chunk {index}: {e}")
                        results[index] = None # Ou lever une exception
                        
            logger.debug("compute_on_chunks terminé.")
        except Exception as e:
            logger.error(f"Erreur dans compute_on_chunks: {e}")
            raise
        return results

# --- Exemple de fonction compatible pour multiprocessing ---
# (À placer en dehors de la classe, ou dans un module séparé si nécessaire)
# Les fonctions passées à ParallelEngine doivent être sérialisables (picklable).
# Elles ne peuvent pas être des méthodes d'instance d'une classe non picklable.

def example_worker_function(data_item):
    """
    Exemple de fonction de travail compatible avec ParallelEngine.map.
    Cette fonction DOIT être définie au niveau du module (pas dans une classe)
    ou dans un module séparé pour être picklable.
    """
    # Simuler un calcul
    import time
    time.sleep(0.01) # 10ms
    result = data_item ** 2
    return result
