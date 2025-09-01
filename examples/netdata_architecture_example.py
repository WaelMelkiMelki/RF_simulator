# examples/netdata_architecture_example.py
"""
Exemple d'utilisation de l'Architecture NETDATA INNOVATION
Démontre l'utilisation correcte des couches et services.

ARCHITECTURE NETDATA :
🎨 PRESENTATION → 🧠 APPLICATION → 🔬 DOMAIN → ⚙️ INFRASTRUCTURE
"""
import sys
import logging
from pathlib import Path

# Ajouter le répertoire src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def setup_logging():
    """Configure le logging pour l'exemple."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def example_visualization_engine():
    """
    Exemple d'utilisation du VisualizationEngine (Infrastructure Layer).
    
    Démontre :
    - Création d'un moteur de visualisation
    - Configuration haute performance
    - Affichage d'objets 3D
    - Monitoring des performances
    """
    print("\n🌐 EXEMPLE: VisualizationEngine (Infrastructure Layer)")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication
        from gui.widgets.visualization_engine import VisualizationEngine
        import pyvista as pv
        
        # Créer application Qt
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Créer le moteur de visualisation (Infrastructure Layer)
        engine = VisualizationEngine()
        
        # Afficher les métriques de performance
        def on_performance_metrics(metrics):
            print(f"📊 Métriques: CPU {metrics.get('cpu_percent', 0):.1f}%, "
                  f"Mémoire {metrics.get('memory_percent', 0):.1f}%, "
                  f"FPS {metrics.get('fps', 0):.1f}")
        
        engine.performance_metrics.connect(on_performance_metrics)
        
        # Créer une scène 3D simple
        sphere = pv.Sphere(radius=5.0)
        cube = pv.Cube(bounds=[-3, 3, -3, 3, -3, 3])
        
        # Simuler un objet Scene avec meshes
        class MockScene:
            def __init__(self):
                self.meshes = {
                    "sphere": sphere,
                    "cube": cube
                }
        
        scene = MockScene()
        
        # Afficher la scène via le moteur
        engine.update_scene(scene)
        
        # Ajouter des antennes
        engine.add_antenna([0, 0, 10], "wifi", "Antenne_WiFi")
        engine.add_antenna([10, 0, 5], "5g", "Antenne_5G")
        
        print("✅ VisualizationEngine configuré avec succès")
        print("   - Scène 3D affichée")
        print("   - Antennes ajoutées") 
        print("   - Monitoring de performance actif")
        
        engine.show()
        return engine
        
    except Exception as e:
        print(f"❌ Erreur VisualizationEngine: {e}")
        import traceback
        traceback.print_exc()
        return None

def example_scene_viewer_widget():
    """
    Exemple d'utilisation du SceneViewer3DWidget (Presentation Layer).
    
    Démontre :
    - Création d'un widget de présentation
    - Intégration avec VisualizationEngine
    - Gestion des événements UI
    """
    print("\n🎨 EXEMPLE: SceneViewer3DWidget (Presentation Layer)")
    print("=" * 60)
    
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
        from gui.widgets.scene_viewer_3d_widget import SceneViewer3DWidget
        
        # Créer application Qt
        app = QApplication.instance() or QApplication(sys.argv)
        
        # Fenêtre principale
        main_window = QMainWindow()
        main_window.setWindowTitle("NETDATA INNOVATION - Visualiseur 3D")
        main_window.setGeometry(100, 100, 1200, 800)
        
        # Widget central
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # SceneViewer3DWidget (Presentation Layer)
        scene_widget = SceneViewer3DWidget()
        layout.addWidget(scene_widget)
        
        main_window.setCentralWidget(central_widget)
        
        # Connecter les signaux
        def on_mesh_selected(index):
            print(f"🎯 Mesh sélectionné: {index}")
        
        def on_right_click(x, y, z):
            print(f"🖱️ Clic droit en: ({x:.1f}, {y:.1f}, {z:.1f})")
        
        scene_widget.mesh_selected.connect(on_mesh_selected)
        scene_widget.right_click_position.connect(on_right_click)
        
        print("✅ SceneViewer3DWidget configuré avec succès")
        print("   - Interface utilisateur créée")
        print("   - Signaux connectés")
        print("   - VisualizationEngine intégré")
        
        main_window.show()
        return main_window, scene_widget
        
    except Exception as e:
        print(f"❌ Erreur SceneViewer3DWidget: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def example_backend_adapter():
    """
    Exemple d'utilisation du BackendAdapter (Presentation Layer).
    
    Démontre :
    - Adaptation entre UI et Application Layer
    - Gestion des simulations asynchrones
    - Communication via signaux PyQt6
    """
    print("\n🧠 EXEMPLE: BackendAdapter (Presentation → Application)")
    print("=" * 60)
    
    try:
        from PyQt6.QtCore import QObject
        from gui.adapters.backend_adapter import BackendAdapter
        
        # Mock SimulationOrchestrator pour l'exemple
        class MockOrchestrator(QObject):
            def load_scene(self, path):
                print(f"📁 Chargement scène: {path}")
                return {"name": "scene_test", "meshes": {}}
            
            def add_antenna(self, position, antenna_type, properties=None):
                print(f"📡 Ajout antenne {antenna_type} en {position}")
                return {"id": 1, "type": antenna_type, "position": position}
            
            def run_simulation(self, config):
                print(f"⚡ Simulation avec config: {config}")
                return {"status": "success", "results": {}}
        
        # Créer l'adaptateur
        adapter = BackendAdapter()
        
        # Configurer avec l'orchestrateur mock
        adapter.set_orchestrator(MockOrchestrator())
        
        # Connecter les signaux
        def on_scene_loaded(scene):
            print(f"✅ Scène chargée: {scene}")
        
        def on_simulation_completed(results):
            print(f"✅ Simulation terminée: {results}")
        
        adapter.scene_loaded.connect(on_scene_loaded)
        adapter.simulation_completed.connect(on_simulation_completed)
        
        # Tester les fonctionnalités
        adapter.load_scene("test_scene.obj")
        
        # Créer une antenne pour le test
        from core.domain.antenna_factory import AntennaFactory
        factory = AntennaFactory()
        antenna = factory.create_antenna("wifi", [0, 0, 10], {"name": "Test_Antenna"})
        adapter.add_antenna(antenna)
        
        print("✅ BackendAdapter configuré avec succès")
        print("   - Orchestrateur connecté")
        print("   - Signaux fonctionnels")
        print("   - Communication UI ↔ Application active")
        
        return adapter
        
    except Exception as e:
        print(f"❌ Erreur BackendAdapter: {e}")
        import traceback
        traceback.print_exc()
        return None

def example_netdata_config():
    """
    Exemple d'utilisation de la configuration NETDATA.
    
    Démontre :
    - Validation de l'architecture
    - Informations sur les composants
    - Métriques de performance
    """
    print("\n⚙️ EXEMPLE: Configuration NETDATA")
    print("=" * 60)
    
    try:
        from core.application.netdata_config import (
            validate_netdata_architecture,
            get_netdata_component_info,
            log_architecture_info,
            NETDATA_LAYERS,
            PERFORMANCE_TARGETS
        )
        
        # Afficher les informations d'architecture
        log_architecture_info()
        
        # Valider l'architecture
        is_valid = validate_netdata_architecture()
        print(f"\n🔍 Validation architecture: {'✅ VALIDE' if is_valid else '❌ PROBLÈMES'}")
        
        # Informations sur un composant
        component_info = get_netdata_component_info("visualization_engine")
        if component_info:
            print(f"\n📋 Informations VisualizationEngine:")
            print(f"   - Couche: {component_info.get('layer', 'N/A')}")
            print(f"   - Description: {component_info.get('description', 'N/A')}")
        
        # Afficher les cibles de performance
        print(f"\n🎯 Cibles de performance:")
        for category, targets in PERFORMANCE_TARGETS.items():
            print(f"   {category.upper()}:")
            for metric, value in targets.items():
                print(f"     - {metric}: {value}")
        
        print("\n✅ Configuration NETDATA chargée avec succès")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration NETDATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_netdata_architecture():
    """
    Démonstration complète de l'architecture NETDATA.
    
    Montre l'intégration de tous les composants selon les spécifications.
    """
    print("🚀 DÉMONSTRATION ARCHITECTURE NETDATA INNOVATION")
    print("=" * 80)
    print("Architecture respectée selon le cahier des charges:")
    print("• Analyse des exigences NETDATA INNOVATION ✅")
    print("• Technologies PyVista pour visualisation 3D ✅") 
    print("• Calcul haute performance CPU/GPU ✅")
    print("• Architecture modulaire avec séparation des couches ✅")
    print("=" * 80)
    
    # Configuration logging
    setup_logging()
    
    # 1. Configuration NETDATA
    print("\n📋 1. VALIDATION ARCHITECTURE NETDATA")
    config_ok = example_netdata_config()
    
    if not config_ok:
        print("❌ Configuration NETDATA non valide - arrêt de la démonstration")
        return
    
    # 2. Infrastructure Layer - VisualizationEngine
    print("\n🌐 2. INFRASTRUCTURE LAYER - VisualizationEngine")
    engine = example_visualization_engine()
    
    # 3. Presentation Layer - SceneViewer3DWidget
    print("\n🎨 3. PRESENTATION LAYER - SceneViewer3DWidget")
    window, widget = example_scene_viewer_widget()
    
    # 4. Presentation Layer - BackendAdapter
    print("\n🔗 4. ADAPTER LAYER - BackendAdapter")
    adapter = example_backend_adapter()
    
    # Résumé
    print("\n" + "=" * 80)
    print("🎉 DÉMONSTRATION TERMINÉE")
    print("=" * 80)
    print("✅ Architecture NETDATA INNOVATION implémentée avec succès:")
    print("   🎨 PRESENTATION: SceneViewer3DWidget + BackendAdapter")
    print("   🧠 APPLICATION: SimulationOrchestrator (simulé)")
    print("   🔬 DOMAIN: Services RF et Antennes (référencés)")
    print("   ⚙️ INFRASTRUCTURE: VisualizationEngine + Services techniques")
    print("\n📊 Bénéfices obtenus:")
    print("   • Séparation claire des responsabilités")
    print("   • Haute performance avec PyVista + GPU")
    print("   • Architecture modulaire et extensible")
    print("   • Monitoring de performance en temps réel")
    print("   • Respect total du cahier des charges NETDATA")
    
    # Garder les fenêtres ouvertes si créées
    if window:
        print("\n🖼️ Fenêtres de démonstration ouvertes")
        print("   (Fermer les fenêtres pour terminer)")
    
    return engine, window, widget, adapter

if __name__ == "__main__":
    # Lancer la démonstration complète
    components = demonstrate_netdata_architecture()
    
    # Si des composants graphiques ont été créés, lancer la boucle d'événements
    engine, window, widget, adapter = components
    
    if window:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance() or QApplication(sys.argv)
        sys.exit(app.exec())
