#!/usr/bin/env python3
"""
Script pour tester le lancement de la simulation complète.
Étapes :
1. Initialisation de SimulationOrchestrator
2. Chargement de la scène et des antennes (pré-requis)
3. Configuration et lancement via start_simulation
4. Validation et pré-traitement
5. Sélection du modèle de propagation
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au chemin Python
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_simulation_launch():
    """Teste le lancement complet de la simulation."""
    print("=== Test du Lancement de la Simulation ===")
    
    try:
        # 1. Initialisation de SimulationOrchestrator
        print("\n1. Initialisation de SimulationOrchestrator...")
        from core.application.simulation_orchestrator import SimulationOrchestrator
        orchestrator = SimulationOrchestrator()
        print("✅ SimulationOrchestrator initialisé avec succès")
        
        # 2. Chargement de la scène (pré-requis)
        print("\n2. Chargement de la scène 3D...")
        scene_file_path = project_root / "data" / "test_scene.obj"
        if scene_file_path.exists():
            scene = orchestrator.load_scene(str(scene_file_path))
            print(f"✅ Scène chargée depuis {scene_file_path}")
            print(f"   Type de scène: {type(scene)}")
        else:
            print("❌ Fichier de scène non trouvé")
            return False
        
        # 3. Ajout des antennes (pré-requis)
        print("\n3. Ajout d'antennes...")
        wifi_config = {
            "name": "Test WiFi Antenna",
            "position": [0, 0, 1],
            "frequency": "2.4GHz",
            "power_dbm": 20.0,
            "ssid": "TestNetwork"
        }
        
        antenna = orchestrator.add_antenna("wifi", wifi_config)
        print("✅ Antenne WiFi ajoutée")
        print(f"   Nom: {antenna.name}")
        print(f"   Position: {antenna.position}")
        
        # 4. Configuration pour la simulation
        print("\n4. Configuration de la simulation...")
        config = {
            "resolution": 1.0,
            "propagation_model": "free_space",
            "rf_calculator_backend": "default"  # ou "optimized" ou "pytorch"
        }
        print("✅ Configuration définie")
        print(f"   Résolution: {config['resolution']} m")
        print(f"   Modèle de propagation: {config['propagation_model']}")
        print(f"   Backend RF: {config['rf_calculator_backend']}")
        
        # 5. Callback de progression (optionnel)
        def progress_callback(percent, message):
            print(f"   Progression: {percent}% - {message}")
        
        # 6. Lancement de la simulation
        print("\n5. Lancement de la simulation...")
        print("   (Cela peut prendre quelques secondes...)")
        
        results = orchestrator.start_simulation(config, progress_callback)
        
        print("✅ Simulation terminée avec succès")
        
        # 7. Affichage des résultats
        print("\n6. Résultats de la simulation:")
        if results and "coverage" in results:
            coverage_points = len(results["coverage"])
            print(f"   Nombre de points de couverture calculés: {coverage_points}")
            
            # Afficher quelques points d'exemple
            if coverage_points > 0:
                print("   Exemples de points de couverture:")
                for i, point in enumerate(results["coverage"][:3]):  # Afficher les 3 premiers
                    print(f"     Point {i+1}: Position {point['position']}, Signal: {point['signal_strength']:.2f} dBm")
        else:
            print("   ❌ Aucun résultat de couverture trouvé")
            
        # 8. Validation des données
        print("\n7. Validation des données...")
        try:
            validation_result = orchestrator.validate_data()
            if validation_result:
                print("✅ Validation des données réussie")
            else:
                print("❌ Validation des données échouée")
        except Exception as e:
            print(f"❌ Erreur lors de la validation: {e}")
            
        # 9. Test de sélection du modèle de propagation
        print("\n8. Test de sélection du modèle de propagation...")
        try:
            free_space_model = orchestrator._get_propagation_model("free_space")
            ray_tracing_model = orchestrator._get_propagation_model("ray_tracing")
            print("✅ Modèles de propagation sélectionnés avec succès")
            print(f"   FreeSpaceModel: {type(free_space_model).__name__}")
            print(f"   RayTracingModel: {type(ray_tracing_model).__name__}")
        except Exception as e:
            print(f"❌ Erreur lors de la sélection des modèles: {e}")
            
        print("\n=== Fin du test de lancement de la simulation ===")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simulation_edge_cases():
    """Teste les cas limites de la simulation."""
    print("\n=== Test des Cas Limites ===")
    
    try:
        from core.application.simulation_orchestrator import SimulationOrchestrator
        
        # Cas 1: Lancement sans scène
        print("\n1. Test: Lancement sans scène...")
        orchestrator = SimulationOrchestrator()
        # Ajouter une antenne mais pas de scène
        orchestrator.add_antenna("base", {
            "name": "Test Antenna",
            "position": [0, 0, 1],
            "frequency": "2.4GHz",
            "power_dbm": 20.0
        })
        
        try:
            orchestrator.start_simulation({"resolution": 1.0})
            print("   ❌ La simulation aurait dû échouer (pas de scène)")
        except ValueError as e:
            if "Scene or antennas not configured" in str(e):
                print("   ✅ Erreur correctement levée pour scène manquante")
            else:
                print(f"   ⚠️  Erreur différente: {e}")
        except Exception as e:
            print(f"   ❌ Erreur inattendue: {e}")
        
        # Cas 2: Lancement sans antennes
        print("\n2. Test: Lancement sans antennes...")
        orchestrator2 = SimulationOrchestrator()
        # Charger une scène mais pas d'antennes
        scene_file_path = project_root / "data" / "test_scene.obj"
        if scene_file_path.exists():
            orchestrator2.load_scene(str(scene_file_path))
            
            try:
                orchestrator2.start_simulation({"resolution": 1.0})
                print("   ❌ La simulation aurait dû échouer (pas d'antennes)")
            except ValueError as e:
                if "Scene or antennas not configured" in str(e):
                    print("   ✅ Erreur correctement levée pour antennes manquantes")
                else:
                    print(f"   ⚠️  Erreur différente: {e}")
            except Exception as e:
                print(f"   ❌ Erreur inattendue: {e}")
        else:
            print("   ⚠️  Fichier de scène non trouvé pour ce test")
            
        print("\n=== Fin des tests de cas limites ===")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests de cas limites: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Test du Lancement de la Simulation")
    print("=" * 50)
    
    # Test principal
    success = test_simulation_launch()
    
    # Test des cas limites
    if success:
        test_simulation_edge_cases()
    
    print("\n🏁 Tests terminés")
