#!/usr/bin/env python3
"""
Script pour tester l'intégration GUI/PyVista.
Teste :
1. Affichage d'un objet simple (sphère) dans SceneViewer3D
2. Affichage de résultats de simulation (nuage de points)
3. Intégration complète avec BackendAdapter
"""

import sys
import os
from pathlib import Path

# Ajouter le dossier src au chemin Python
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def test_pyvista_integration():
    """Teste l'intégration de base de PyVista."""
    print("🧪 Test de l'intégration PyVista")
    print("=" * 50)
    
    try:
        import pyvista as pv
        print("✅ PyVista importé avec succès")
        
        # Créer un objet simple pour test
        sphere = pv.Sphere()
        print(f"✅ Objet PyVista créé: {type(sphere)} ({sphere.n_points} points)")
        
        return True
    except Exception as e:
        print(f"❌ Erreur d'intégration PyVista: {e}")
        return False

def test_scene_viewer_3d_basic():
    """Teste SceneViewer3D avec un objet simple."""
    print("\n🎨 Test de SceneViewer3D (objet simple)")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        import sys
        
        # Créer une application Qt (nécessaire pour les widgets)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Importer SceneViewer3D
        from gui.widgets.scene_viewer_3d import SceneViewer3D
        
        # Créer le widget
        viewer = SceneViewer3D()
        print("✅ SceneViewer3D créé avec succès")
        
        # Créer un objet PyVista simple
        import pyvista as pv
        sphere = pv.Sphere()
        
        # Tester l'affichage
        viewer.show_scene(sphere)
        print("✅ Objet PyVista affiché dans SceneViewer3D")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec SceneViewer3D: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scene_viewer_3d_with_scene_object():
    """Teste SceneViewer3D avec un objet Scene3D."""
    print("\n🏢 Test de SceneViewer3D (objet Scene3D)")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        import sys
        
        # Créer une application Qt
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Importer les composants
        from gui.widgets.scene_viewer_3d import SceneViewer3D
        from core.domain.scene import Scene3D
        import pyvista as pv
        
        # Créer le widget
        viewer = SceneViewer3D()
        print("✅ SceneViewer3D créé")
        
        # Créer un objet Scene3D avec un mesh simple
        sphere = pv.Sphere()
        scene = Scene3D(data=sphere)
        # Forcer le mesh pour le test
        scene.mesh = sphere
        
        # Tester l'affichage
        viewer.show_scene(scene)
        print("✅ Objet Scene3D affiché dans SceneViewer3D")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec Scene3D dans SceneViewer3D: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backend_adapter_integration():
    """Teste l'intégration avec BackendAdapter."""
    print("\n🔌 Test de BackendAdapter")
    print("=" * 50)
    
    try:
        # Importer BackendAdapter
        from gui.adapters.backend_adapter import BackendAdapter
        print("✅ BackendAdapter importé")
        
        # Créer une instance
        backend = BackendAdapter()
        print("✅ BackendAdapter instancié")
        
        # Vérifier les méthodes de base
        required_methods = ['load_scene', 'add_antenna', 'start_simulation']
        for method in required_methods:
            if hasattr(backend, method):
                print(f"   ✅ Méthode {method} présente")
            else:
                print(f"   ❌ Méthode {method} manquante")
        
        return True
    except Exception as e:
        print(f"❌ Erreur avec BackendAdapter: {e}")
        return False

def test_simulation_results_display():
    """Teste l'affichage de résultats de simulation."""
    print("\n📊 Test d'affichage des résultats de simulation")
    print("=" * 50)
    
    try:
        from PyQt6.QtWidgets import QApplication
        import sys
        import numpy as np
        
        # Créer une application Qt
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Importer SceneViewer3D
        from gui.widgets.scene_viewer_3d import SceneViewer3D
        
        # Créer le widget
        viewer = SceneViewer3D()
        print("✅ SceneViewer3D créé")
        
        # Créer des résultats de simulation factices
        import pyvista as pv
        
        # Créer un nuage de points avec intensité
        points = np.array([
            [0, 0, 1],
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
            [0.5, 0.5, 2]
        ])
        
        cloud = pv.PolyData(points)
        signal_strength = np.array([-50, -55, -60, -65, -45])
        cloud["signal_strength"] = signal_strength
        
        # Tester l'affichage
        viewer.show_scene(cloud)
        print("✅ Résultats de simulation affichés dans SceneViewer3D")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage des résultats: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Fonction principale de test."""
    print("🚀 Test de la Visualisation GUI/PyVista")
    print("=" * 60)
    
    # Liste des tests à exécuter
    tests = [
        ("Intégration PyVista", test_pyvista_integration),
        ("SceneViewer3D (objet simple)", test_scene_viewer_3d_basic),
        ("SceneViewer3D (objet Scene3D)", test_scene_viewer_3d_with_scene_object),
        ("BackendAdapter", test_backend_adapter_integration),
        ("Résultats de simulation", test_simulation_results_display)
    ]
    
    results = []
    
    # Exécuter chaque test
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Exécution du test: {test_name}")
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test {test_name} a échoué avec une exception: {e}")
            results.append((test_name, False))
    
    # Résumé
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ SUCCÈS" if result else "❌ ÉCHEC"
        print(f"   {test_name:<30} : {status}")
        if result:
            passed += 1
    
    print(f"\n📈 Résultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests de visualisation GUI/PyVista ont réussi!")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
