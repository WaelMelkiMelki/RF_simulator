#!/usr/bin/env python3
"""
Script pour tester les différents backends de calcul RF du SimulationOrchestrator.
Teste les backends : default, optimized, pytorch
"""

import sys
import os
import time
import numpy as np
from pathlib import Path

# Ajouter le dossier src au chemin Python
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_backend(backend_name, config_base, orchestrator, scene_file_path, antenna_config):
    """Teste un backend spécifique et retourne les résultats."""
    print(f"\n{'='*60}")
    print(f"🧪 Test du backend: {backend_name.upper()}")
    print(f"{'='*60}")
    
    # Configuration spécifique au backend
    config = config_base.copy()
    config["rf_calculator_backend"] = backend_name
    
    try:
        # Réinitialiser l'orchestrateur pour chaque test
        orchestrator.scene = None
        orchestrator.antennas = []
        
        # Recharger la scène
        print(f"   📁 Chargement de la scène...")
        scene = orchestrator.load_scene(str(scene_file_path))
        print(f"   ✅ Scène chargée: {type(scene)}")
        
        # Réajouter l'antenne
        print(f"   📡 Ajout de l'antenne...")
        antenna = orchestrator.add_antenna("wifi", antenna_config)
        print(f"   ✅ Antenne ajoutée: {antenna.name}")
        
        # Callback de progression
        def progress_callback(percent, message):
            if percent % 25 == 0:  # Afficher tous les 25%
                print(f"   🔄 {percent}% - {message}")
        
        # Lancer la simulation
        print(f"   ⚡ Lancement de la simulation avec backend '{backend_name}'...")
        start_time = time.time()
        
        results = orchestrator.start_simulation(config, progress_callback)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Analyser les résultats
        if results and "coverage" in results:
            coverage_points = len(results["coverage"])
            print(f"   ✅ Simulation terminée avec succès!")
            print(f"   📊 Points de couverture calculés: {coverage_points}")
            print(f"   🕐 Temps d'exécution: {execution_time:.2f} secondes")
            
            # Afficher quelques résultats
            if coverage_points > 0:
                print(f"   📈 Exemples de résultats:")
                for i, point in enumerate(results["coverage"][:3]):  # Afficher les 3 premiers
                    signal_dbm = point['signal_strength']
                    position = point['position']
                    print(f"     Point {i+1}: Position {position}, Signal: {signal_dbm:.2f} dBm")
            
            # Vérifier la cohérence des résultats
            signal_values = [p['signal_strength'] for p in results["coverage"]]
            if signal_values:
                avg_signal = np.mean(signal_values)
                min_signal = np.min(signal_values)
                max_signal = np.max(signal_values)
                print(f"   📊 Statistiques des signaux:")
                print(f"     Moyenne: {avg_signal:.2f} dBm")
                print(f"     Minimum: {min_signal:.2f} dBm")
                print(f"     Maximum: {max_signal:.2f} dBm")
                
                # Vérifier qu'il n'y a pas de valeurs aberrantes
                if np.isnan(avg_signal) or np.isinf(avg_signal):
                    print(f"   ⚠️  Attention: Valeurs NaN ou infinies détectées!")
                elif avg_signal > 50 or avg_signal < -300:
                    print(f"   ⚠️  Attention: Valeurs de signal suspectes!")
                else:
                    print(f"   ✅ Résultats numériquement cohérents")
            
            return {
                "success": True,
                "execution_time": execution_time,
                "coverage_points": coverage_points,
                "results": results
            }
        else:
            print(f"   ❌ Aucun résultat de couverture trouvé")
            return {
                "success": False,
                "error": "Aucun résultat de couverture",
                "execution_time": execution_time
            }
            
    except Exception as e:
        print(f"   ❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "execution_time": 0
        }

def test_all_backends():
    """Teste tous les backends de calcul RF."""
    print("🚀 Test des Backends de Calcul RF")
    print("=" * 60)
    
    try:
        # Importer les composants nécessaires
        from core.application.simulation_orchestrator import SimulationOrchestrator
        
        # Créer l'orchestrateur
        orchestrator = SimulationOrchestrator()
        print("✅ SimulationOrchestrator initialisé")
        
        # Configuration de base
        config_base = {
            "resolution": 1.0,
            "propagation_model": "free_space"
        }
        
        # Configuration de l'antenne
        antenna_config = {
            "name": "Test WiFi Antenna",
            "position": [0, 0, 1],
            "frequency": "2.4GHz",
            "power_dbm": 20.0,
            "ssid": "TestNetwork"
        }
        
        # Chemin de la scène
        scene_file_path = project_root / "data" / "test_scene.obj"
        if not scene_file_path.exists():
            print(f"❌ Fichier de scène non trouvé: {scene_file_path}")
            return
        
        print(f"📂 Utilisation de la scène: {scene_file_path}")
        
        # Tester chaque backend
        backends = ["default", "optimized", "pytorch"]
        results_summary = {}
        
        for backend in backends:
            result = test_backend(backend, config_base, orchestrator, scene_file_path, antenna_config)
            results_summary[backend] = result
        
        # Résumé final
        print(f"\n{'='*60}")
        print(f"📊 RÉSUMÉ DES TESTS")
        print(f"{'='*60}")
        
        successful_backends = []
        failed_backends = []
        
        for backend, result in results_summary.items():
            status = "✅ SUCCÈS" if result["success"] else "❌ ÉCHEC"
            time_info = f"{result['execution_time']:.2f}s" if result["execution_time"] > 0 else "N/A"
            print(f"   {backend.upper():12} : {status} ({time_info})")
            
            if result["success"]:
                successful_backends.append((backend, result["execution_time"]))
            else:
                failed_backends.append((backend, result.get("error", "Erreur inconnue")))
        
        # Comparaison des performances
        if successful_backends:
            print(f"\n⚡ COMPARAISON DES PERFORMANCES:")
            # Trier par temps d'exécution
            successful_backends.sort(key=lambda x: x[1])
            for i, (backend, time_taken) in enumerate(successful_backends):
                marker = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else "  "
                print(f"   {marker} {backend:12} : {time_taken:.2f} secondes")
        
        # Détails des échecs
        if failed_backends:
            print(f"\n💥 DÉTAILS DES ÉCHECS:")
            for backend, error in failed_backends:
                print(f"   {backend.upper():12} : {error}")
        
        print(f"\n🏁 Tests des backends terminés")
        return results_summary
        
    except Exception as e:
        print(f"❌ Erreur fatale lors des tests: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_backend_fallback():
    """Teste le mécanisme de fallback entre backends."""
    print(f"\n{'='*60}")
    print(f"🔄 Test du Mécanisme de Fallback")
    print(f"{'='*60}")
    
    try:
        from core.application.simulation_orchestrator import SimulationOrchestrator
        
        # Créer l'orchestrateur
        orchestrator = SimulationOrchestrator()
        
        # Configuration avec un backend qui pourrait échouer
        config = {
            "resolution": 1.0,
            "propagation_model": "free_space",
            "rf_calculator_backend": "pytorch"  # On suppose que PyTorch pourrait ne pas être disponible
        }
        
        # Configuration de l'antenne
        antenna_config = {
            "name": "Test WiFi Antenna",
            "position": [0, 0, 1],
            "frequency": "2.4GHz",
            "power_dbm": 20.0,
            "ssid": "TestNetwork"
        }
        
        # Chemin de la scène
        scene_file_path = project_root / "data" / "test_scene.obj"
        if not scene_file_path.exists():
            print(f"❌ Fichier de scène non trouvé: {scene_file_path}")
            return
        
        # Charger la scène et ajouter l'antenne
        orchestrator.load_scene(str(scene_file_path))
        orchestrator.add_antenna("wifi", antenna_config)
        
        print(f"   🎯 Test avec backend 'pytorch' (avec fallback)...")
        
        # Callback de progression
        def progress_callback(percent, message):
            print(f"   🔄 {percent}% - {message}")
        
        # Lancer la simulation
        try:
            results = orchestrator.start_simulation(config, progress_callback)
            print(f"   ✅ Simulation terminée avec succès (fallback fonctionnel si nécessaire)")
            
            if results and "coverage" in results:
                print(f"   📊 Points de couverture: {len(results['coverage'])}")
            
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de fallback: {e}")

if __name__ == "__main__":
    # Exécuter les tests
    results = test_all_backends()
    
    # Tester le fallback
    test_backend_fallback()
    
    print(f"\n🎯 Test des Calculs RF terminé")
