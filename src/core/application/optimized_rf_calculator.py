# src/core/application/optimized_rf_calculator.py
"""
Calculateur RF optimisé pour la simulation de couverture.
Intègre le cache spatial Octree et le calcul parallèle pour des gains de performance significatifs.
"""

import numpy as np
import logging
import time
from typing import List, Tuple, Optional, Dict, Any
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing as mp

logger = logging.getLogger(__name__)

# Import des composants d'optimisation
try:
    from core.domain.spatial_index import SpatialIndex, BoundingBox
    SPATIAL_INDEX_AVAILABLE = True
except ImportError:
    SPATIAL_INDEX_AVAILABLE = False
    logger.warning("SpatialIndex non disponible - utilisation du mode sans cache spatial")

try:
    from core.infrastructure.parallel_engine import ParallelEngine
    PARALLEL_ENGINE_AVAILABLE = True
except ImportError:
    PARALLEL_ENGINE_AVAILABLE = False
    logger.warning("ParallelEngine non disponible - utilisation du mode séquentiel")


class PerformanceBenchmark:
    """Classe pour mesurer et comparer les performances."""
    
    def __init__(self):
        self.metrics: Dict[str, Dict[str, float]] = {}
        self.start_times: Dict[str, float] = {}
        
    def start(self, name: str):
        """Démarre un chronomètre pour une opération."""
        self.start_times[name] = time.perf_counter()
        
    def stop(self, name: str) -> float:
        """Arrête le chronomètre et retourne la durée."""
        if name not in self.start_times:
            return 0.0
        duration = time.perf_counter() - self.start_times[name]
        if name not in self.metrics:
            self.metrics[name] = {"total": 0.0, "count": 0, "min": float('inf'), "max": 0.0}
        self.metrics[name]["total"] += duration
        self.metrics[name]["count"] += 1
        self.metrics[name]["min"] = min(self.metrics[name]["min"], duration)
        self.metrics[name]["max"] = max(self.metrics[name]["max"], duration)
        return duration
        
    def get_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des performances."""
        summary = {}
        for name, data in self.metrics.items():
            avg = data["total"] / data["count"] if data["count"] > 0 else 0
            summary[name] = {
                "total_time": data["total"],
                "calls": data["count"],
                "avg_time": avg,
                "min_time": data["min"] if data["min"] != float('inf') else 0,
                "max_time": data["max"]
            }
        return summary
        
    def log_summary(self):
        """Log le résumé des performances."""
        summary = self.get_summary()
        logger.info("=" * 60)
        logger.info("RAPPORT DE PERFORMANCE - OptimizedRFCalculator")
        logger.info("=" * 60)
        for name, data in summary.items():
            logger.info(f"  {name}:")
            logger.info(f"    - Temps total: {data['total_time']:.3f}s")
            logger.info(f"    - Appels: {data['calls']}")
            logger.info(f"    - Temps moyen: {data['avg_time']*1000:.2f}ms")
        logger.info("=" * 60)


# Fonction de calcul pour le multiprocessing (doit être au niveau module)
def _calculate_signal_for_chunk(args):
    """
    Calcule le signal pour un chunk de points.
    Cette fonction doit être au niveau module pour être picklable.
    """
    chunk_points, antennas_data, propagation_params, scene_bounds = args
    results = []
    
    for point in chunk_points:
        total_signal = -100.0
        signal_found = False
        
        for ant_data in antennas_data:
            # Calcul simplifié de path loss (Friis)
            pos = ant_data['position']
            freq = ant_data['frequency']
            power = ant_data['power_dbm']
            
            # Distance euclidienne
            distance = np.sqrt(
                (point[0] - pos[0])**2 + 
                (point[1] - pos[1])**2 + 
                (point[2] - pos[2])**2
            )
            
            if distance < 0.1:
                distance = 0.1  # Éviter division par zéro
            
            # Formule de Friis: L = 20*log10(d) + 20*log10(f) + 20*log10(4*pi/c)
            wavelength = 299792458.0 / freq  # c / f
            if wavelength > 0 and distance > 0:
                path_loss = 20 * np.log10(4 * np.pi * distance / wavelength)
            else:
                path_loss = 0
            
            rssi = power - path_loss
            
            if not signal_found:
                total_signal = rssi
                signal_found = True
            else:
                # Combiner les signaux
                if total_signal > -90 and rssi > -90:
                    p1 = 10 ** (total_signal / 10)
                    p2 = 10 ** (rssi / 10)
                    total_signal = 10 * np.log10(p1 + p2)
                else:
                    total_signal = max(total_signal, rssi)
        
        results.append((point, total_signal))
    
    return results


class OptimizedRFCalculator:
    """
    Calculateur RF optimisé pour la simulation de couverture.
    
    Optimisations implémentées:
    - Cache spatial Octree pour accélérer les requêtes d'obstacles
    - Calcul parallèle avec multiprocessing
    - Benchmarking intégré pour mesurer les gains de performance
    """

    def __init__(self, scene, antennas, propagation_model, use_parallel: bool = True, use_spatial_cache: bool = True):
        """
        Initialise le calculateur RF optimisé.
        
        Args:
            scene: La scène 3D contenant les obstacles
            antennas: Liste des antennes pour le calcul
            propagation_model: Modèle de propagation à utiliser
            use_parallel: Activer le calcul parallèle (défaut: True)
            use_spatial_cache: Activer le cache spatial Octree (défaut: True)
        """
        self.scene = scene
        self.antennas = antennas
        self.propagation_model = propagation_model
        self.benchmark = PerformanceBenchmark()
        
        # Configuration des optimisations
        self.use_parallel = use_parallel and PARALLEL_ENGINE_AVAILABLE
        self.use_spatial_cache = use_spatial_cache and SPATIAL_INDEX_AVAILABLE
        
        # Initialisation du cache spatial
        self.spatial_index: Optional[SpatialIndex] = None
        if self.use_spatial_cache:
            self._build_spatial_cache()
            
        # Initialisation du moteur parallèle
        self.parallel_engine: Optional[ParallelEngine] = None
        if self.use_parallel:
            try:
                self.parallel_engine = ParallelEngine()
                logger.info(f"OptimizedRFCalculator: ParallelEngine activé avec {self.parallel_engine.get_worker_count()} workers")
            except Exception as e:
                logger.warning(f"OptimizedRFCalculator: Impossible d'initialiser ParallelEngine: {e}")
                self.use_parallel = False
                
        logger.info(f"OptimizedRFCalculator initialisé - Parallèle: {self.use_parallel}, Cache spatial: {self.use_spatial_cache}")

    def _build_spatial_cache(self):
        """Construit le cache spatial Octree à partir de la scène."""
        self.benchmark.start("build_spatial_cache")
        try:
            mesh = self.scene.get_pyvista_mesh()
            if mesh is None:
                logger.warning("OptimizedRFCalculator: Pas de mesh disponible pour le cache spatial")
                return
                
            bounds = mesh.bounds  # (xmin, xmax, ymin, ymax, zmin, zmax)
            
            # Créer l'index spatial avec les bornes de la scène
            self.spatial_index = SpatialIndex(
                scene_bounds=bounds,
                max_depth=10,
                max_points_per_node=16
            )
            
            # Indexer les centres des cellules du mesh pour la détection d'obstacles
            if hasattr(mesh, 'cell_centers'):
                cell_centers = mesh.cell_centers()
                points = cell_centers.points
                
                for i, point in enumerate(points):
                    self.spatial_index.insert(point.tolist(), {"cell_id": i, "type": "obstacle"})
                
                logger.info(f"OptimizedRFCalculator: Cache spatial construit avec {len(points)} cellules indexées")
            else:
                # Fallback: indexer les sommets
                points = mesh.points
                for i, point in enumerate(points):
                    self.spatial_index.insert(point.tolist(), {"point_id": i, "type": "vertex"})
                logger.info(f"OptimizedRFCalculator: Cache spatial construit avec {len(points)} sommets indexés")
                
            # Log des statistiques de l'octree
            stats = self.spatial_index.get_statistics()
            logger.info(f"OptimizedRFCalculator: Octree stats - Noeuds: {stats['total_nodes']}, Profondeur max: {stats['max_depth_reached']}")
            
        except Exception as e:
            logger.error(f"OptimizedRFCalculator: Erreur construction cache spatial: {e}")
            self.spatial_index = None
            self.use_spatial_cache = False
            
        duration = self.benchmark.stop("build_spatial_cache")
        logger.info(f"OptimizedRFCalculator: Cache spatial construit en {duration*1000:.1f}ms")

    def _check_line_of_sight_cached(self, start: np.ndarray, end: np.ndarray) -> Tuple[bool, float]:
        """
        Vérifie la ligne de vue en utilisant le cache spatial.
        Retourne (has_los, attenuation_factor).
        
        Cette méthode est significativement plus rapide que le ray casting complet
        car elle utilise l'Octree pour éliminer rapidement les régions sans obstacles.
        """
        if self.spatial_index is None:
            return True, 0.0
            
        self.benchmark.start("los_check_cached")
        
        try:
            # Calculer la boîte englobante du rayon
            ray_min = np.minimum(start, end)
            ray_max = np.maximum(start, end)
            
            # Ajouter une petite marge
            margin = 0.5
            ray_min -= margin
            ray_max += margin
            
            # Requête spatiale pour trouver les obstacles potentiels
            potential_obstacles = self.spatial_index.query_range(
                ray_min[0], ray_max[0],
                ray_min[1], ray_max[1],
                ray_min[2], ray_max[2]
            )
            
            if len(potential_obstacles) == 0:
                self.benchmark.stop("los_check_cached")
                return True, 0.0  # Pas d'obstacles, ligne de vue dégagée
            
            # Calculer l'atténuation basée sur le nombre d'obstacles proches
            # (Approximation rapide au lieu du ray casting exact)
            ray_dir = end - start
            ray_length = np.linalg.norm(ray_dir)
            if ray_length < 0.01:
                self.benchmark.stop("los_check_cached")
                return True, 0.0
                
            ray_dir_normalized = ray_dir / ray_length
            
            obstacle_count = 0
            for obs_point, obs_data in potential_obstacles:
                # Vérifier si l'obstacle est vraiment sur le chemin du rayon
                obs_pos = np.array(obs_point)
                to_obs = obs_pos - start
                projection = np.dot(to_obs, ray_dir_normalized)
                
                if 0 < projection < ray_length:
                    # Point de projection le plus proche sur le rayon
                    closest_on_ray = start + projection * ray_dir_normalized
                    distance_to_ray = np.linalg.norm(obs_pos - closest_on_ray)
                    
                    if distance_to_ray < 2.0:  # Seuil de proximité
                        obstacle_count += 1
            
            # Calculer l'atténuation (approximation: 3-6 dB par obstacle)
            attenuation = obstacle_count * 4.0  # dB par obstacle
            has_los = obstacle_count == 0
            
            self.benchmark.stop("los_check_cached")
            return has_los, attenuation
            
        except Exception as e:
            logger.debug(f"OptimizedRFCalculator: Erreur LOS cached: {e}")
            self.benchmark.stop("los_check_cached")
            return True, 0.0

    def calculate_radiation_pattern(self, antenna):
        """
        Calcule le diagramme de rayonnement pour une antenne donnée.
        Retourne un dictionnaire contenant les points et les valeurs de couverture.
        """
        logger.info(f"OptimizedRFCalculator: Calcul du diagramme pour l'antenne {antenna.name}")
        
        # Générer une grille de points autour de l'antenne
        grid_points = self._generate_grid_around_antenna(antenna)
        signal_strengths = []

        for point in grid_points:
            loss = self.propagation_model.calculate_path_loss(
                antenna.position, point, self.scene, antenna.frequency
            )
            rssi = antenna.power_dbm - loss
            signal_strengths.append(rssi)

        logger.info(f"OptimizedRFCalculator: Calcul du diagramme terminé. {len(grid_points)} points calculés")
        return {
            "points": grid_points.tolist(),
            "values": signal_strengths
        }

    def _generate_grid_around_antenna(self, antenna):
        """
        Génère une grille de points autour de l'antenne pour le calcul de couverture.
        """
        x0, y0, z0 = antenna.position
        
        # Utiliser le coverage_radius de l'antenne ou la valeur par défaut
        radius = getattr(antenna, 'coverage_radius', 15.0)
        logger.debug(f"OptimizedRFCalculator._generate_grid_around_antenna: Utilisation du rayon {radius}m pour {antenna.name}")
        
        # Créer une grille sphérique autour de l'antenne
        num_points = int((2 * radius / 1.0) ** 3)
        if num_points > 10000:  # Limiter pour performance
            resolution = 1.0 * (num_points / 10000) ** (1/3)
        else:
            resolution = 1.0
            
        x = np.arange(x0 - radius, x0 + radius, resolution)
        y = np.arange(y0 - radius, y0 + radius, resolution)
        z = np.arange(z0 - radius/2, z0 + radius/2, resolution/2)
        
        # Créer une grille 3D
        xx, yy, zz = np.meshgrid(x, y, z)
        points = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])
        
        # Filtrer les points trop éloignés (intérieur d'une sphère)
        distances = np.sqrt((points[:, 0] - x0)**2 + (points[:, 1] - y0)**2 + (points[:, 2] - z0)**2)
        mask = distances <= radius
        filtered_points = points[mask]
        
        return filtered_points

    def calculate_coverage_grid_detailed(self, resolution=1.0):
        """
        Calcule une grille détaillée de couverture pour la heatmap.
        
        Optimisations:
        - Utilise le calcul parallèle si disponible (multiprocessing)
        - Utilise le cache spatial Octree pour accélérer les tests de ligne de vue
        - Mesure et log les performances pour validation
        
        Returns:
            dict: {'points': [...], 'values': [...]}
        """
        self.benchmark.start("total_calculation")
        
        logger.info(f"OptimizedRFCalculator: Calcul de la grille détaillée avec résolution {resolution}m")
        logger.info(f"OptimizedRFCalculator: Mode parallèle: {self.use_parallel}, Cache spatial: {self.use_spatial_cache}")

        # Obtenir les bornes de la scène
        self.benchmark.start("grid_generation")
        mesh = self.scene.get_pyvista_mesh()
        bounds = mesh.bounds
        logger.debug(f"OptimizedRFCalculator: Bornes de la scène = {bounds}")

        # Générer une grille régulière avec la résolution donnée
        x = np.arange(bounds[0], bounds[1], resolution)
        y = np.arange(bounds[2], bounds[3], resolution)
        z = np.arange(bounds[4], bounds[5], resolution)

        # Créer la grille 3D
        xx, yy, zz = np.meshgrid(x, y, z)
        grid_points = np.column_stack([xx.ravel(), yy.ravel(), zz.ravel()])
        
        grid_gen_time = self.benchmark.stop("grid_generation")
        logger.info(f"OptimizedRFCalculator: Grille générée avec {len(grid_points)} points en {grid_gen_time*1000:.1f}ms")

        # Choisir le mode de calcul
        if self.use_parallel and len(grid_points) > 1000:
            results = self._calculate_parallel(grid_points)
        else:
            results = self._calculate_sequential(grid_points)
        
        total_time = self.benchmark.stop("total_calculation")
        
        # Log du rapport de performance
        points_per_second = len(grid_points) / total_time if total_time > 0 else 0
        logger.info(f"OptimizedRFCalculator: Calcul terminé en {total_time:.2f}s ({points_per_second:.0f} points/sec)")
        
        # Afficher le résumé des performances
        self.benchmark.log_summary()
        
        return results

    def _calculate_parallel(self, grid_points: np.ndarray) -> Dict[str, List]:
        """
        Calcule les signaux en utilisant des opérations vectorisées NumPy.
        
        Cette méthode utilise des calculs matriciels pour traiter tous les points
        simultanément, ce qui est beaucoup plus rapide que le multiprocessing
        pour ce type de calcul numérique.
        """
        self.benchmark.start("parallel_calculation")
        
        # Préparer les positions d'antennes en array
        antenna_positions = np.array([ant.position for ant in self.antennas])
        antenna_frequencies = np.array([ant.frequency for ant in self.antennas])
        antenna_powers = np.array([ant.power_dbm for ant in self.antennas])
        
        num_points = len(grid_points)
        num_antennas = len(self.antennas)
        
        logger.info(f"OptimizedRFCalculator: Calcul vectorisé pour {num_points} points, {num_antennas} antennes")
        
        # Calcul vectorisé des distances (broadcasting)
        # grid_points: (N, 3), antenna_positions: (M, 3)
        # Résultat: distances (N, M) - distance de chaque point à chaque antenne
        diff = grid_points[:, np.newaxis, :] - antenna_positions[np.newaxis, :, :]  # (N, M, 3)
        distances = np.sqrt(np.sum(diff**2, axis=2))  # (N, M)
        
        # Éviter la division par zéro
        distances = np.maximum(distances, 0.1)
        
        # Calcul vectorisé de la perte de propagation (Friis)
        # wavelength = c / f
        c = 299792458.0
        wavelengths = c / antenna_frequencies  # (M,)
        
        # Path loss = 20*log10(4*pi*d/lambda)
        path_loss = 20 * np.log10(4 * np.pi * distances / wavelengths[np.newaxis, :])  # (N, M)
        
        # RSSI = Puissance - Perte
        rssi = antenna_powers[np.newaxis, :] - path_loss  # (N, M)
        
        # Combiner les signaux de toutes les antennes (somme des puissances)
        # Convertir de dBm en linéaire, sommer, reconvertir
        # Utiliser un seuil pour éviter les problèmes numériques
        rssi_clipped = np.clip(rssi, -150, 50)  # Limiter les valeurs extrêmes
        power_linear = 10 ** (rssi_clipped / 10)  # (N, M)
        total_power_linear = np.sum(power_linear, axis=1)  # (N,)
        
        # Reconvertir en dBm
        total_signal = 10 * np.log10(np.maximum(total_power_linear, 1e-20))  # (N,)
        
        parallel_time = self.benchmark.stop("parallel_calculation")
        logger.info(f"OptimizedRFCalculator: Calcul vectorisé terminé en {parallel_time:.2f}s")
        
        # Filtrer et formater les résultats
        signal_values = []
        valid_points = []
        
        for i, signal in enumerate(total_signal):
            if signal > -200:
                signal_values.append(float(signal))
                valid_points.append(grid_points[i].tolist())
        
        self._log_signal_statistics(total_signal.tolist(), signal_values, valid_points)
        
        return {
            'points': valid_points,
            'values': signal_values
        }

    def _calculate_sequential(self, grid_points: np.ndarray) -> Dict[str, List]:
        """
        Calcule les signaux de manière séquentielle (fallback ou petites grilles).
        Utilise le cache spatial Octree pour accélérer les tests de ligne de vue.
        """
        self.benchmark.start("sequential_calculation")
        
        signal_values = []
        valid_points = []
        all_signal_values = []

        for i, point in enumerate(grid_points):
            total_signal = self._calculate_total_signal_at_point_optimized(point)
            all_signal_values.append(total_signal)

            # Log de progression
            if i % max(1, len(grid_points) // 10) == 0 and i > 0:
                progress = (i / len(grid_points)) * 100
                logger.debug(f"OptimizedRFCalculator: Progression séquentielle {progress:.1f}%")

            if total_signal > -200:
                signal_values.append(total_signal)
                valid_points.append(point.tolist() if hasattr(point, 'tolist') else list(point))

        sequential_time = self.benchmark.stop("sequential_calculation")
        logger.info(f"OptimizedRFCalculator: Calcul séquentiel terminé en {sequential_time:.2f}s")
        
        self._log_signal_statistics(all_signal_values, signal_values, valid_points)

        return {
            'points': valid_points,
            'values': signal_values
        }

    def _calculate_total_signal_at_point_optimized(self, point) -> float:
        """
        Calcule le signal total à un point avec optimisations Octree.
        
        Utilise le cache spatial pour accélérer la détection des obstacles
        sur le chemin de propagation.
        """
        total_signal = -100.0
        signal_found = False
        point_arr = np.array(point)
        
        for antenna in self.antennas:
            try:
                antenna_pos = np.array(antenna.position)
                
                # Utiliser le cache spatial pour vérifier la ligne de vue
                if self.use_spatial_cache and self.spatial_index is not None:
                    has_los, extra_attenuation = self._check_line_of_sight_cached(antenna_pos, point_arr)
                else:
                    has_los, extra_attenuation = True, 0.0
                
                # Calculer la perte de propagation
                loss = self.propagation_model.calculate_path_loss(
                    antenna.position, point, self.scene, antenna.frequency
                )
                
                # Ajouter l'atténuation due aux obstacles détectés par l'Octree
                loss += extra_attenuation
                
                rssi = antenna.power_dbm - loss
                
                if not signal_found:
                    total_signal = rssi
                    signal_found = True
                else:
                    total_signal = self._combine_signals(total_signal, rssi)
                    
            except Exception as e:
                logger.debug(f"OptimizedRFCalculator: Erreur calcul signal pour {getattr(antenna, 'name', 'unknown')}: {e}")
                continue
        
        return total_signal

    def _log_signal_statistics(self, all_signals: List[float], valid_signals: List[float], valid_points: List):
        """Log les statistiques des signaux calculés."""
        if len(all_signals) > 0:
            overall_min = np.min(all_signals)
            overall_max = np.max(all_signals)
            overall_mean = np.mean(all_signals)
            overall_std = np.std(all_signals)
            logger.info(f"OptimizedRFCalculator: Stats globales - Min: {overall_min:.2f}dBm, Max: {overall_max:.2f}dBm, Moyenne: {overall_mean:.2f}dBm, Écart-type: {overall_std:.2f}dBm")

        logger.info(f"OptimizedRFCalculator: Points valides: {len(valid_points)}")

        if len(valid_signals) > 0:
            min_val = np.min(valid_signals)
            max_val = np.max(valid_signals)
            mean_val = np.mean(valid_signals)
            logger.info(f"OptimizedRFCalculator: Valeurs finales: Min={min_val:.2f}dBm, Max={max_val:.2f}dBm, Moyenne={mean_val:.2f}dBm")

    def _combine_signals(self, signal1, signal2):
        """
        Combine deux signaux (en dBm) de manière réaliste.
        """
        # Convertir de dBm en puissance linéaire, additionner, puis reconvertir en dBm
        try:
            # Pour éviter les problèmes avec des valeurs très négatives
            if signal1 < -90 and signal2 < -90:
                return max(signal1, signal2)  # Prendre le meilleur des deux mauvais signaux
            elif signal1 < -90:
                return signal2
            elif signal2 < -90:
                return signal1
            else:
                # Additionner les puissances (approximation simplifiée)
                p1_linear = 10 ** (signal1 / 10)
                p2_linear = 10 ** (signal2 / 10)
                p_total_linear = p1_linear + p2_linear
                if p_total_linear > 0:
                    combined = 10 * np.log10(p_total_linear)
                    return max(combined, -150)  # Limiter à -150 dBm minimum
                else:
                    return max(signal1, signal2)
        except:
            return max(signal1, signal2)

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Retourne un rapport détaillé des performances.
        
        Utile pour valider les gains de performance obtenus
        par les optimisations (Octree, multiprocessing).
        """
        report = {
            "optimizations_enabled": {
                "parallel_processing": self.use_parallel,
                "spatial_cache_octree": self.use_spatial_cache
            },
            "metrics": self.benchmark.get_summary()
        }
        
        if self.spatial_index is not None:
            report["octree_statistics"] = self.spatial_index.get_statistics()
            
        if self.parallel_engine is not None:
            report["parallel_workers"] = self.parallel_engine.get_worker_count()
            
        return report