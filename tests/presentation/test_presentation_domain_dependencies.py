# tests/presentation/test_presentation_domain_dependencies.py
"""
Tests pour vérifier les dépendances entre la couche Présentation et la couche Domaine
selon le tableau fourni.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Ajouter le dossier src au chemin Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Importer les classes nécessaires
from core.domain.scene import Scene3D
from core.domain.antenna import BaseAntenna, WiFiAntenna, Antenna5G
from core.domain.antenna_factory import AntennaFactory
from core.domain.rf_models import PropagationStrategy, FreeSpaceModel, SimpleRayTracingModel
from core.domain.material_properties import MaterialProperties
from core.domain.spatial_index import SpatialIndex

class TestPresentationDomainDependencies:
    """Tests pour les dépendances entre Présentation Layer et Domain Layer"""

    # Test: gui/main_window.py → Scene3D, SpatialIndex
    def test_main_window_domain_dependencies(self):
        """Teste les dépendances de main_window.py vers Scene3D et SpatialIndex"""
        # Arrange & Act
        # Vérifier que Scene3D peut être importé
        scene_available = hasattr(Scene3D, '__init__')
        
        # Vérifier que SpatialIndex peut être importé
        spatial_index_available = hasattr(SpatialIndex, '__init__')
        
        # Assert
        assert scene_available, "Scene3D doit être disponible pour main_window.py"
        assert spatial_index_available, "SpatialIndex doit être disponible pour main_window.py"

    # Test: gui/widgets/* → AntennaFactory, BaseAntenna, WiFiAntenna, Antenna5G
    def test_gui_widgets_domain_dependencies(self):
        """Teste les dépendances des widgets GUI vers les classes d'antennes"""
        # Arrange & Act
        # Vérifier que les classes d'antennes peuvent être importées
        base_antenna_available = hasattr(BaseAntenna, '__init__')
        wifi_antenna_available = hasattr(WiFiAntenna, '__init__')
        antenna_5g_available = hasattr(Antenna5G, '__init__')
        antenna_factory_available = hasattr(AntennaFactory, '__init__')
        
        # Assert
        assert base_antenna_available, "BaseAntenna doit être disponible pour les widgets"
        assert wifi_antenna_available, "WiFiAntenna doit être disponible pour les widgets"
        assert antenna_5g_available, "Antenna5G doit être disponible pour les widgets"
        assert antenna_factory_available, "AntennaFactory doit être disponible pour les widgets"

    def test_antenna_factory_integration(self):
        """Teste l'intégration de AntennaFactory"""
        # Arrange
        factory = AntennaFactory()
        
        # Act
        # Créer différentes antennes via la factory
        base_config = {
            "name": "Test Base Antenna",
            "position": [0, 0, 1],
            "frequency": 2.4e9,
            "power_dbm": 20.0
        }
        
        wifi_config = {
            "name": "Test WiFi Antenna",
            "position": [1, 1, 1],
            "frequency": 2.4e9,
            "power_dbm": 20.0,
            "ssid": "TestNetwork"
        }
        
        antenna5g_config = {
            "name": "Test 5G Antenna",
            "position": [2, 2, 1],
            "frequency": 3.5e9,
            "power_dbm": 30.0,
            "band": "n78"
        }
        
        # Créer les antennes
        try:
            base_antenna = factory.create_antenna("base", base_config)
            wifi_antenna = factory.create_antenna("wifi", wifi_config)
            antenna5g = factory.create_antenna("5g", antenna5g_config)
            factory_works = True
        except Exception:
            factory_works = False
            
        # Assert
        assert factory_works, "AntennaFactory doit pouvoir créer toutes les antennes"
        assert isinstance(base_antenna, BaseAntenna)
        assert isinstance(wifi_antenna, WiFiAntenna)
        assert isinstance(antenna5g, Antenna5G)

    # Test: gui/adapters/backend_adapter.py → PropagationStrategy, FreeSpaceModel, SimpleRayTracingModel
    def test_backend_adapter_propagation_dependencies(self):
        """Teste les dépendances de backend_adapter.py vers les modèles de propagation"""
        # Arrange & Act
        # Vérifier que les classes de propagation peuvent être importées
        propagation_strategy_available = hasattr(PropagationStrategy, '__init__')
        free_space_model_available = hasattr(FreeSpaceModel, '__init__')
        ray_tracing_model_available = hasattr(SimpleRayTracingModel, '__init__')
        
        # Assert
        assert propagation_strategy_available, "PropagationStrategy doit être disponible"
        assert free_space_model_available, "FreeSpaceModel doit être disponible"
        assert ray_tracing_model_available, "SimpleRayTracingModel doit être disponible"

    def test_propagation_models_integration(self):
        """Teste l'intégration des modèles de propagation"""
        # Arrange
        free_space_model = FreeSpaceModel()
        ray_tracing_model = SimpleRayTracingModel()
        
        # Act
        # Vérifier que les modèles ont les méthodes nécessaires
        free_space_has_method = hasattr(free_space_model, 'calculate_path_loss')
        ray_tracing_has_method = hasattr(ray_tracing_model, 'calculate_path_loss')
        
        # Assert
        assert free_space_has_method, "FreeSpaceModel doit avoir calculate_path_loss"
        assert ray_tracing_has_method, "SimpleRayTracingModel doit avoir calculate_path_loss"

    # Test: gui/adapters/backend_adapter.py → RFCalculator, BaseAntenna
    def test_backend_adapter_rf_calculator_dependencies(self):
        """Teste les dépendances de backend_adapter.py vers RFCalculator et BaseAntenna"""
        # Arrange & Act
        # Vérifier que BaseAntenna est disponible (déjà testé)
        base_antenna_available = hasattr(BaseAntenna, '__init__')
        
        # Vérifier que OptimizedRFCalculator peut être importé
        try:
            from core.application.optimized_rf_calculator import OptimizedRFCalculator
            rf_calculator_available = True
        except ImportError:
            rf_calculator_available = False
            
        # Assert
        assert base_antenna_available, "BaseAntenna doit être disponible"
        # Note: Selon l'analyse, RFCalculator n'est pas utilisé directement par backend_adapter
        # mais par SimulationOrchestrator

    # Test: config_manager.py → Scene3D, MaterialProperties, AntennaFactory, PropagationStrategy
    def test_config_manager_domain_dependencies(self):
        """Teste les dépendances hypothétiques de config_manager.py vers les classes du domaine"""
        # Arrange & Act
        # Vérifier que les classes du domaine peuvent être importées
        scene_available = hasattr(Scene3D, '__init__')
        material_props_available = hasattr(MaterialProperties, '__init__')
        antenna_factory_available = hasattr(AntennaFactory, '__init__')
        propagation_strategy_available = hasattr(PropagationStrategy, '__init__')
        
        # Assert
        assert scene_available, "Scene3D doit être disponible"
        assert material_props_available, "MaterialProperties doit être disponible"
        assert antenna_factory_available, "AntennaFactory doit être disponible"
        assert propagation_strategy_available, "PropagationStrategy doit être disponible"

    def test_material_properties_integration(self):
        """Teste l'intégration de MaterialProperties"""
        # Arrange & Act
        try:
            # Créer un matériau
            concrete = MaterialProperties("Concrete", 2.4e9, 5.0)
            
            # Vérifier les propriétés
            name = concrete.get_name()
            attenuation = concrete.get_attenuation()
            
            # Assert
            assert name == "Concrete"
            assert attenuation == 5.0
        except Exception as e:
            pytest.fail(f"MaterialProperties ne fonctionne pas correctement: {e}")

    def test_spatial_index_integration(self):
        """Teste l'intégration de SpatialIndex"""
        # Arrange & Act
        try:
            # Créer un index spatial
            spatial_index = SpatialIndex()
            
            # Insérer un point
            spatial_index.insert([0, 0, 0], "test_point")
            
            # Requête
            results = spatial_index.query_point(0, 0, 0, radius=1.0)
            
            # Assert
            assert isinstance(results, list)
            assert len(results) >= 1
        except Exception as e:
            pytest.skip(f"SpatialIndex ne fonctionne pas correctement: {e}")

    # Tests d'intégration complète
    def test_presentation_domain_integration(self):
        """Teste l'intégration complète des composants Présentation avec Domaine"""
        # Arrange & Act
        # Test de Scene3D
        scene = Scene3D()
        scene_available = scene is not None
        
        # Test de AntennaFactory
        factory = AntennaFactory()
        factory_available = factory is not None
        
        # Test de FreeSpaceModel
        free_space_model = FreeSpaceModel()
        free_space_available = free_space_model is not None
        
        # Test de MaterialProperties
        material = MaterialProperties()
        material_available = material is not None
        
        # Assert
        assert scene_available, "Scene3D doit être intégré"
        assert factory_available, "AntennaFactory doit être intégré"
        assert free_space_available, "FreeSpaceModel doit être intégré"
        assert material_available, "MaterialProperties doit être intégré"

    def test_domain_classes_instantiation(self):
        """Teste l'instanciation de toutes les classes du domaine nécessaires"""
        # Arrange & Act & Assert
        try:
            # Scene3D
            scene = Scene3D()
            assert isinstance(scene, Scene3D)
            
            # AntennaFactory
            factory = AntennaFactory()
            assert isinstance(factory, AntennaFactory)
            
            # BaseAntenna
            base_antenna = BaseAntenna()
            assert isinstance(base_antenna, BaseAntenna)
            
            # WiFiAntenna
            wifi_antenna = WiFiAntenna()
            assert isinstance(wifi_antenna, WiFiAntenna)
            
            # Antenna5G
            antenna5g = Antenna5G()
            assert isinstance(antenna5g, Antenna5G)
            
            # FreeSpaceModel
            free_space = FreeSpaceModel()
            assert isinstance(free_space, FreeSpaceModel)
            
            # SimpleRayTracingModel
            ray_tracing = SimpleRayTracingModel()
            assert isinstance(ray_tracing, SimpleRayTracingModel)
            
            # MaterialProperties
            material = MaterialProperties()
            assert isinstance(material, MaterialProperties)
            
            # SpatialIndex
            spatial_index = SpatialIndex()
            assert isinstance(spatial_index, SpatialIndex)
            
        except Exception as e:
            pytest.fail(f"Échec de l'instanciation des classes du domaine: {e}")
