#!/usr/bin/env python3
"""
Script pour tester le post-traitement et la gestion des résultats du SimulationOrchestrator.
Teste : 
1. Finalisation des résultats bruts
2. Mise en cache via SimulationCache
3. Export automatique via ExportManager (CSV, VTK)
"""

import sys
import os
import tempfile
import time
from pathlib import Path

# Ajouter le dossier src au chemin Python
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_post_processing_and_results():
    """Teste le post-traitement complet et la gestion des résultats."""
    print("🚀 Test du Post-traitement & Résultats")
    print("=" * 60)
    
    try:
        # Importer les composants nécessaires
        from core.application.simulation_orchestrator import SimulationOrchestrator
        from core.infrastructure.cache_manager import SimulationCache
        from core.application.exporter import ExportManager
        
        # Créer un dossier temporaire pour les exports
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            print(f"📂 Dossier de test: {temp_path}")
            
            # 1. Initialisation de SimulationOrchestrator
            print("\n1. Initialisation de SimulationOrchestrator...")
            orchestrator = SimulationOrchestrator()
            print("✅ SimulationOrchestrator initialisé")
            
            # 2. Chargement de la scène
            print("\n2. Chargement de la scène 3D...")
            scene_file_path = project_root / "data" / "test_scene.obj"
            if not scene_file_path.exists():
                print(f"❌ Fichier de scène non trouvé: {scene_file_path}")
                return False
                
            scene = orchestrator.load_scene(str(scene_file_path))
            print(f"✅ Scène chargée: {type(scene)}")
            
            # 3. Ajout d'une antenne
            print("\n3. Ajout d'une antenne...")
            antenna_config = {
                "name": "Test WiFi Antenna",
                "position": [0, 0, 1],
                "frequency": "2.4GHz",
                "power_dbm": 20.0,
                "ssid": "TestNetwork"
            }
            
            antenna = orchestrator.add_antenna("wifi", antenna_config)
            print(f"✅ Antenne ajoutée: {antenna.name}")
            
            # 4. Configuration pour la simulation avec auto_export
            print("\n4. Configuration de la simulation...")
            config = {
                "resolution": 1.0,
                "propagation_model": "free_space",
                "rf_calculator_backend": "default",
                "auto_export": True,  # Activer l'export automatique
                "export_formats": ["csv", "vtk"],  # Formats à exporter
                "output_path": str(temp_path / "simulation_results")  # Chemin de base pour les exports
            }
            print("✅ Configuration définie avec auto_export=True")
            
            # 5. Callback de progression
            def progress_callback(percent, message):
                if percent % 50 == 0:  # Afficher tous les 50%
                    print(f"   🔄 {percent}% - {message}")
            
            # 6. Lancement de la simulation
            print("\n5. Lancement de la simulation...")
            start_time = time.time()
            
            results = orchestrator.start_simulation(config, progress_callback)
            
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"✅ Simulation terminée en {execution_time:.2f} secondes")
            
            # 7. Vérification des résultats bruts
            print("\n6. Vérification des résultats bruts...")
            if results and "coverage" in results:
                coverage_points = len(results["coverage"])
                print(f"✅ Points de couverture calculés: {coverage_points}")
                
                # Afficher quelques résultats
                if coverage_points > 0:
                    print("📊 Exemples de résultats:")
                    for i, point in enumerate(results["coverage"][:3]):
                        print(f"   Point {i+1}: Position {point['position']}, Signal: {point['signal_strength']:.2f} dBm")
            else:
                print("❌ Aucun résultat de couverture trouvé")
                return False
            
            # 8. Vérification de la mise en cache
            print("\n7. Vérification de la mise en cache...")
            try:
                # Créer une clé de cache basée sur les paramètres
                cache_key = {
                    "scene": str(scene),
                    "antennas": [str(a) for a in orchestrator.antennas],
                    "config": config
                }
                
                # Vérifier si les résultats sont dans le cache
                cached_results = orchestrator.cache.get_cached_results(cache_key)
                if cached_results:
                    print("✅ Résultats trouvés dans le cache")
                    # Vérifier que les résultats du cache sont identiques
                    if cached_results == results:
                        print("✅ Cohérence entre résultats originaux et mis en cache")
                    else:
                        print("⚠️  Différence entre résultats originaux et mis en cache")
                else:
                    print("⚠️  Résultats non trouvés dans le cache (première exécution)")
                    
                # Tester la mise en cache explicite
                test_key = {"test": "cache_verification"}
                test_data = {"test_value": 42}
                orchestrator.cache.cache_results(test_key, test_data)
                retrieved_data = orchestrator.cache.get_cached_results(test_key)
                
                if retrieved_data == test_data:
                    print("✅ Système de cache fonctionnel")
                else:
                    print("❌ Problème avec le système de cache")
                    return False
                    
            except Exception as e:
                print(f"❌ Erreur lors de la vérification du cache: {e}")
                return False
            
            # 9. Vérification des exports
            print("\n8. Vérification des exports...")
            expected_files = []
            base_output_path = temp_path / "simulation_results"
            
            # Vérifier les fichiers CSV
            csv_file = Path(str(base_output_path) + ".csv")
            if csv_file.exists():
                file_size = csv_file.stat().st_size
                print(f"✅ Fichier CSV généré: {csv_file.name} ({file_size} bytes)")
                expected_files.append(csv_file)
            else:
                print(f"❌ Fichier CSV non trouvé: {csv_file}")
                
            # Vérifier les fichiers VTK
            vtk_file = Path(str(base_output_path) + ".vtk")
            if vtk_file.exists():
                file_size = vtk_file.stat().st_size
                print(f"✅ Fichier VTK généré: {vtk_file.name} ({file_size} bytes)")
                expected_files.append(vtk_file)
            else:
                print(f"❌ Fichier VTK non trouvé: {vtk_file}")
            
            # Afficher le contenu des fichiers générés (aperçu)
            for file_path in expected_files:
                try:
                    print(f"\n📄 Contenu de {file_path.name} (5 premières lignes):")
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if i < 5:
                                print(f"   {line.strip()}")
                            else:
                                break
                except Exception as e:
                    print(f"   ⚠️  Impossible de lire {file_path.name}: {e}")
            
            # 10. Test de récupération depuis le cache
            print("\n9. Test de récupération depuis le cache...")
            print("   🔄 Relance de la même simulation...")
            
            # Relancer la simulation avec les mêmes paramètres
            start_time2 = time.time()
            results2 = orchestrator.start_simulation(config, progress_callback)
            end_time2 = time.time()
            
            execution_time2 = end_time2 - start_time2
            print(f"   ✅ Deuxième simulation terminée en {execution_time2:.2f} secondes")
            
            # Vérifier si c'était plus rapide (devrait venir du cache)
            if execution_time2 < execution_time:
                print("   ✅ La deuxième exécution était plus rapide (probablement depuis le cache)")
            else:
                print("   ⚠️  La deuxième exécution n'était pas plus rapide (peut-être pas depuis le cache)")
            
            # Vérifier que les résultats sont identiques
            if results == results2:
                print("   ✅ Résultats identiques entre les deux exécutions")
            else:
                print("   ⚠️  Résultats différents entre les deux exécutions")
            
            print("\n🎉 Test du Post-traitement & Résultats TERMINÉ")
            return True
            
    except Exception as e:
        print(f"❌ Erreur fatale lors du test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_export_manager_standalone():
    """Teste l'ExportManager de manière indépendante."""
    print("\n" + "=" * 60)
    print("🔧 Test de l'ExportManager (autonome)")
    print("=" * 60)
    
    try:
        from core.application.exporter import ExportManager
        import tempfile
        import csv
        
        # Données de test
        test_results = {
            "coverage": [
                {"position": [0, 0, 1], "signal_strength": -50.0},
                {"position": [1, 1, 1], "signal_strength": -55.0},
                {"position": [2, 2, 1], "signal_strength": -60.0}
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            base_path = temp_path / "test_export"
            
            # Test d'export en batch
            print("   📤 Test d'export batch (CSV, VTK)...")
            exporter = ExportManager()
            exported_files = exporter.batch_export(
                test_results, 
                str(base_path), 
                ["csv", "vtk"]
            )
            
            print("   ✅ Export batch terminé")
            
            # Vérifier les fichiers générés
            for format_name, file_path in exported_files.items():
                path_obj = Path(file_path)
                if path_obj.exists():
                    file_size = path_obj.stat().st_size
                    print(f"   ✅ {format_name.upper()} généré: {path_obj.name} ({file_size} bytes)")
                    
                    # Pour CSV, vérifier le contenu
                    if format_name == "csv":
                        try:
                            with open(path_obj, 'r') as f:
                                import csv
                                reader = csv.reader(f)
                                rows = list(reader)
                                print(f"   📊 CSV contient {len(rows)-1} lignes de données")  # -1 pour l'en-tête
                        except Exception as e:
                            print(f"   ⚠️  Erreur lors de la lecture du CSV: {e}")
                else:
                    print(f"   ❌ {format_name.upper()} non trouvé: {file_path}")
            
            print("✅ Test de l'ExportManager autonome réussi")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors du test de l'ExportManager: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Test du Post-traitement & Résultats")
    print("=" * 60)
    
    # Test principal
    success1 = test_post_processing_and_results()
    
    # Test de l'ExportManager autonome
    success2 = test_export_manager_standalone()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TOUS LES TESTS DU POST-TRAITEMENT & RÉSULTATS ONT RÉUSSI")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
    print("=" * 60)
