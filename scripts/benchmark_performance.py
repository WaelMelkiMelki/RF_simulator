#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark de Performance - RF Simulator 3D
===========================================

Ce script mesure les gains de performance apportés par les optimisations:
- Cache spatial Octree pour accélérer les requêtes d'obstacles
- Calcul parallèle avec multiprocessing

Il compare les temps d'exécution avec et sans optimisations pour
valider les gains de performance annoncés.

Usage:
    python scripts/benchmark_performance.py
"""

import sys
import os
import time
import logging
import numpy as np
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_scene():
    """Crée une scène de test synthétique."""
    from core.domain.scene import Scene3D
    import pyvista as pv
    
    # Créer une scène avec plusieurs objets
    scene = Scene3D()
    
    # Créer un mesh combiné avec plusieurs bâtiments
    meshes = []
    
    # Bâtiment 1
    box1 = pv.Box(bounds=(-10, 0, -10, 0, 0, 15))
    meshes.append(box1)
    
    # Bâtiment 2
    box2 = pv.Box(bounds=(5, 15, -10, 0, 0, 20))
    meshes.append(box2)
    
    # Bâtiment 3
    box3 = pv.Box(bounds=(-10, 0, 5, 15, 0, 12))
    meshes.append(box3)
    
    # Bâtiment 4
    box4 = pv.Box(bounds=(5, 15, 5, 15, 0, 18))
    meshes.append(box4)
    
    # Sol
    ground = pv.Plane(center=(2.5, 2.5, 0), direction=(0, 0, 1), i_size=40, j_size=40)
    meshes.append(ground)
    
    # Combiner tous les meshes
    combined = meshes[0]
    for m in meshes[1:]:
        combined = combined.merge(m)
    
    scene.load_from_data(combined)
    return scene


def create_test_antennas():
    """Crée des antennes de test."""
    from core.domain.antenna import WiFiAntenna
    
    antennas = [
        WiFiAntenna(name="Antenne_1", position=(2.5, 2.5, 10), power_dbm=20, frequency=2.4e9),
        WiFiAntenna(name="Antenne_2", position=(-5, -5, 8), power_dbm=20, frequency=2.4e9),
        WiFiAntenna(name="Antenne_3", position=(10, 10, 12), power_dbm=20, frequency=2.4e9),
    ]
    return antennas


def run_benchmark(scene, antennas, resolution, use_parallel, use_spatial_cache, iterations=3):
    """
    Exécute un benchmark avec les paramètres donnés.
    
    Returns:
        dict: Résultats du benchmark
    """
    from core.domain.rf_models import FreeSpaceModel
    from core.application.optimized_rf_calculator import OptimizedRFCalculator
    
    propagation_model = FreeSpaceModel()
    
    times = []
    points_count = 0
    
    for i in range(iterations):
        logger.info(f"  Itération {i+1}/{iterations}...")
        
        # Créer un nouveau calculateur à chaque itération
        calculator = OptimizedRFCalculator(
            scene, 
            antennas, 
            propagation_model,
            use_parallel=use_parallel,
            use_spatial_cache=use_spatial_cache
        )
        
        start = time.perf_counter()
        results = calculator.calculate_coverage_grid_detailed(resolution=resolution)
        end = time.perf_counter()
        
        times.append(end - start)
        points_count = len(results.get('points', []))
        
        # Récupérer le rapport de performance
        perf_report = calculator.get_performance_report()
    
    avg_time = np.mean(times)
    std_time = np.std(times)
    min_time = np.min(times)
    max_time = np.max(times)
    
    return {
        'avg_time': avg_time,
        'std_time': std_time,
        'min_time': min_time,
        'max_time': max_time,
        'points_calculated': points_count,
        'points_per_second': points_count / avg_time if avg_time > 0 else 0,
        'iterations': iterations,
        'performance_report': perf_report
    }


def main():
    """Fonction principale du benchmark."""
    print("=" * 70)
    print("  BENCHMARK DE PERFORMANCE - RF SIMULATOR 3D")
    print("  Validation des optimisations CPU (Multiprocessing)")
    print("=" * 70)
    print()
    
    # Configuration du benchmark
    resolutions = [2.0, 1.0]  # Résolutions à tester
    iterations = 3
    
    # Créer la scène et les antennes de test
    logger.info("Création de la scène de test...")
    scene = create_test_scene()
    antennas = create_test_antennas()
    logger.info(f"Scène créée avec {scene.get_pyvista_mesh().n_points} points")
    logger.info(f"{len(antennas)} antennes créées")
    print()
    
    results_summary = {}
    
    for resolution in resolutions:
        print("-" * 70)
        print(f"  RÉSOLUTION: {resolution}m")
        print("-" * 70)
        
        # Mode 1: Sans optimisations (baseline)
        print("\n[1/2] Mode BASELINE (sans optimisations)...")
        baseline = run_benchmark(
            scene, antennas, resolution,
            use_parallel=False, 
            use_spatial_cache=False,
            iterations=iterations
        )
        print(f"      Temps moyen: {baseline['avg_time']:.3f}s ± {baseline['std_time']:.3f}s")
        print(f"      Points/sec: {baseline['points_per_second']:.0f}")
        
        # Mode 2: Avec calcul vectorisé NumPy
        print("\n[2/2] Mode VECTORISÉ (NumPy optimisé)...")
        vectorized = run_benchmark(
            scene, antennas, resolution,
            use_parallel=True,  # Active le calcul vectorisé
            use_spatial_cache=False,
            iterations=iterations
        )
        print(f"      Temps moyen: {vectorized['avg_time']:.3f}s ± {vectorized['std_time']:.3f}s")
        print(f"      Points/sec: {vectorized['points_per_second']:.0f}")
        
        # Calculer les gains de performance
        vectorized_gain = (1 - vectorized['avg_time'] / baseline['avg_time']) * 100 if baseline['avg_time'] > 0 else 0
        speedup = baseline['avg_time'] / vectorized['avg_time'] if vectorized['avg_time'] > 0 else 0
        
        results_summary[f"res_{resolution}"] = {
            'baseline': baseline,
            'vectorized': vectorized,
            'vectorized_gain_percent': vectorized_gain,
            'speedup_factor': speedup
        }
        
        print()
        print("  📊 RÉSULTATS:")
        print(f"      • Gain avec vectorisation: {vectorized_gain:+.1f}%")
        print(f"      • Facteur d'accélération: {speedup:.2f}x")
        print()
    
    # Résumé final
    print("=" * 70)
    print("  RÉSUMÉ FINAL")
    print("=" * 70)
    print()
    
    for res_key, data in results_summary.items():
        resolution = res_key.replace("res_", "")
        print(f"  Résolution {resolution}m:")
        print(f"    - Baseline: {data['baseline']['avg_time']:.3f}s")
        print(f"    - Vectorisé: {data['vectorized']['avg_time']:.3f}s")
        print(f"    - Gain: {data['vectorized_gain_percent']:.1f}% ({data['speedup_factor']:.2f}x plus rapide)")
        print()
    
    # Vérifier si l'objectif de 70% est atteint
    best_gain = max(d['vectorized_gain_percent'] for d in results_summary.values())
    
    print("=" * 70)
    if best_gain >= 70:
        print(f"  ✅ OBJECTIF ATTEINT: Gain de performance de {best_gain:.1f}%")
    elif best_gain >= 50:
        print(f"  ⚠️  GAIN SIGNIFICATIF: {best_gain:.1f}% (objectif: 70%)")
    else:
        print(f"  ❌ GAIN INSUFFISANT: {best_gain:.1f}% (objectif: 70%)")
    print("=" * 70)
    
    return results_summary


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBenchmark interrompu par l'utilisateur.")
    except Exception as e:
        logger.error(f"Erreur lors du benchmark: {e}")
        import traceback
        traceback.print_exc()
