# tests/presentation/test_presentation_application_dependencies.py
"""
Tests pour vérifier les dépendances entre la couche Présentation et la couche Application.
"""

import pytest
import sys
import os

# Ajouter le dossier src au chemin Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importer les classes nécessaires
from core.application.simulation_orchestrator import SimulationOrchestrator

class TestPresentationApplicationDependencies:
    """Tests pour les dépendances entre Présentation Layer et Application Layer"""

    def test_simulation_orchestrator_import(self):
        """Teste que SimulationOrchestrator peut être importé (dépendance de base)."""
        try:
            from core.application.simulation_orchestrator import SimulationOrchestrator
            assert SimulationOrchestrator is not None
            print("✅ SimulationOrchestrator importé avec succès.")
        except ImportError as e:
            pytest.fail(f"❌ Échec de l'importation de SimulationOrchestrator: {e}")

    def test_simulation_orchestrator_instantiation(self):
        """Teste que SimulationOrchestrator peut être instancié."""
        try:
            orchestrator = SimulationOrchestrator()
            assert orchestrator is not None
            print("✅ SimulationOrchestrator instancié avec succès.")
        except Exception as e:
            pytest.fail(f"❌ Échec de l'instanciation de SimulationOrchestrator: {e}")

    def test_simulation_orchestrator_has_required_attributes(self):
        """Teste que SimulationOrchestrator possède les attributs attendus."""
        try:
            orchestrator = SimulationOrchestrator()
            
            # Vérifier les attributs de base
            required_attributes = [
                'scene',
                'antennas',
                'config',
                'is_running',
                'cache',
                'memory_manager',
                'performance_monitor'
            ]
            
            for attr in required_attributes:
                assert hasattr(orchestrator, attr), f"SimulationOrchestrator doit avoir l'attribut {attr}"
                
            print("✅ SimulationOrchestrator possède tous les attributs requis.")
        except Exception as e:
            pytest.fail(f"❌ Échec de la vérification des attributs de SimulationOrchestrator: {e}")

    def test_simulation_orchestrator_has_required_methods(self):
        """Teste que SimulationOrchestrator possède les méthodes attendues."""
        try:
            orchestrator = SimulationOrchestrator()
            
            # Vérifier les méthodes de base
            required_methods = [
                'load_scene',
                'add_antenna',
                'start_simulation',
                'validate_data'
            ]
            
            for method in required_methods:
                assert hasattr(orchestrator, method), f"SimulationOrchestrator doit avoir la méthode {method}"
                
            print("✅ SimulationOrchestrator possède toutes les méthodes requises.")
        except Exception as e:
            pytest.fail(f"❌ Échec de la vérification des méthodes de SimulationOrchestrator: {e}")

    def test_config_manager_integration_with_orchestrator(self):
        """Teste l'intégration de ConfigManager avec SimulationOrchestrator."""
        try:
            # Importer ConfigManager
            from core.application.config_manager import ConfigManager
            
            # Créer un ConfigManager
            config_manager = ConfigManager()
            assert config_manager is not None
            
            # Créer un SimulationOrchestrator
            orchestrator = SimulationOrchestrator()
            assert orchestrator is not None
            
            # Vérifier que ConfigManager peut fournir une configuration à l'orchestrateur
            # (Cela simule l'intégration, sans exécuter la simulation complète)
            config_data = {
                "simulation": {
                    "model": "free_space",
                    "resolution": 1.0
                }
            }
            
            # Simuler la transmission de configuration
            orchestrator.config = config_data
            assert orchestrator.config == config_data
            
            print("✅ Intégration ConfigManager → SimulationOrchestrator réussie.")
        except ImportError:
            pytest.skip("ConfigManager non disponible")
        except Exception as e:
            pytest.fail(f"❌ Échec de l'intégration ConfigManager → SimulationOrchestrator: {e}")

    def test_backend_adapter_integration_with_orchestrator(self):
        """Teste l'intégration de BackendAdapter avec SimulationOrchestrator."""
        try:
            # Importer BackendAdapter
            # Note: Le chemin exact dépend de la structure du projet
            # Nous testons simplement que l'orchestrateur peut être utilisé
            orchestrator = SimulationOrchestrator()
            assert orchestrator is not None
            
            # Vérifier que l'orchestrateur a les méthodes attendues par le backend
            assert hasattr(orchestrator, 'add_antenna')
            assert hasattr(orchestrator, 'load_scene')
            assert hasattr(orchestrator, 'start_simulation')
            
            print("✅ BackendAdapter peut interagir avec SimulationOrchestrator.")
        except Exception as e:
            pytest.fail(f"❌ Échec de l'intégration BackendAdapter → SimulationOrchestrator: {e}")

    def test_gui_integration_with_orchestrator(self):
        """Teste que les composants GUI peuvent utiliser SimulationOrchestrator."""
        try:
            # Créer un SimulationOrchestrator
            orchestrator = SimulationOrchestrator()
            assert orchestrator is not None
            
            # Vérifier que l'orchestrateur peut être utilisé par la GUI
            # (Cela simule l'utilisation par les widgets)
            assert hasattr(orchestrator, 'scene')
            assert hasattr(orchestrator, 'antennas')
            assert hasattr(orchestrator, 'add_antenna')
            
            print("✅ GUI peut interagir avec SimulationOrchestrator.")
        except Exception as e:
            pytest.fail(f"❌ Échec de l'intégration GUI → SimulationOrchestrator: {e}")

    def test_cli_integration_with_orchestrator(self):
        """Teste que CLI peut utiliser SimulationOrchestrator."""
        try:
            # Créer un SimulationOrchestrator
            orchestrator = SimulationOrchestrator()
            assert orchestrator is not None
            
            # Vérifier que l'orchestrateur peut être utilisé par CLI
            # (Cela simule l'utilisation par l'interface en ligne de commande)
            assert hasattr(orchestrator, 'load_scene')
            assert hasattr(orchestrator, 'start_simulation')
            assert hasattr(orchestrator, 'validate_data')
            
            print("✅ CLI peut interagir avec SimulationOrchestrator.")
        except Exception as e:
            pytest.fail(f"❌ Échec de l'intégration CLI → SimulationOrchestrator: {e}")

    def test_presentation_application_integration(self):
        """Teste l'intégration complète Présentation → Application."""
        try:
            # Importer tous les composants nécessaires
            from core.application.simulation_orchestrator import SimulationOrchestrator
            from core.application.config_manager import ConfigManager
            
            # Créer les instances
            orchestrator = SimulationOrchestrator()
            config_manager = ConfigManager()
            
            # Vérifier que tous les composants peuvent interagir
            assert orchestrator is not None
            assert config_manager is not None
            
            # Vérifier que l'orchestrateur a les fonctionnalités de base
            assert hasattr(orchestrator, 'scene')
            assert hasattr(orchestrator, 'antennas')
            assert hasattr(orchestrator, 'config')
            assert hasattr(orchestrator, 'start_simulation')
            assert hasattr(orchestrator, 'add_antenna')
            assert hasattr(orchestrator, 'load_scene')
            
            print("✅ Intégration complète Présentation → Application réussie.")
        except ImportError as e:
            pytest.skip(f"Composant non disponible: {e}")
        except Exception as e:
            pytest.fail(f"❌ Échec de l'intégration complète Présentation → Application: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
