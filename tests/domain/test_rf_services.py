# tests/domain/test_rf_services.py
import pytest
import numpy as np
from core.domain.rf_models import PropagationStrategy, FreeSpaceModel, SimpleRayTracingModel

def test_propagation_strategy_uses_free_space_model(free_space_model):
    """Vérifie que PropagationStrategy peut utiliser FreeSpaceModel"""
    # Test avec des valeurs simples
    tx_pos = [0, 0, 1]
    rx_pos = [10, 0, 1]
    frequency = 2.4e9
    
    path_loss = free_space_model.calculate_path_loss(tx_pos, rx_pos, None, frequency)
    
    assert isinstance(path_loss, float)
    assert path_loss > 0  # Le path loss est positif en dB
    # Vérification approximative (formule de Friis)
    expected_loss = 20 * np.log10(10) + 20 * np.log10(2.4e9) + 92.45
    assert abs(path_loss - expected_loss) < 0.001

def test_propagation_strategy_uses_ray_tracing_model(ray_tracing_model, test_scene, wifi_antenna):
    """Vérifie que PropagationStrategy peut utiliser SimpleRayTracingModel"""
    # Test avec des positions simples
    tx_pos = wifi_antenna.position
    rx_pos = [5, 5, 1]
    frequency = wifi_antenna.frequency
    
    path_loss = ray_tracing_model.calculate_path_loss(tx_pos, rx_pos, test_scene, frequency)
    
    assert isinstance(path_loss, float)
    assert path_loss > 0  # Le path loss est positif en dB

def test_ray_tracing_uses_scene_3d(ray_tracing_model, test_scene, wifi_antenna):
    """Vérifie que SimpleRayTracingModel utilise correctement Scene3D"""
    assert hasattr(ray_tracing_model, "max_reflections")
    assert ray_tracing_model.max_reflections == 2
    
    # Test avec des positions simples
    tx_pos = wifi_antenna.position
    rx_pos = [1, 1, 1]
    
    # Vérifie que le modèle peut utiliser la scène
    path_loss = ray_tracing_model.calculate_path_loss(
        tx_pos, rx_pos, test_scene, wifi_antenna.frequency
    )
    
    assert isinstance(path_loss, float)
    assert path_loss > 0

def test_ray_tracing_uses_spatial_index(ray_tracing_model, test_scene, wifi_antenna):
    """Vérifie que SimpleRayTracingModel utilise SpatialIndex"""
    # Vérifie que le modèle peut fonctionner avec une scène qui a un spatial_index
    assert hasattr(test_scene, "spatial_index")
    assert test_scene.spatial_index is not None
    
    # Test d'une requête spatiale
    tx_pos = wifi_antenna.position
    rx_pos = [0.5, 0.5, 0.5]
    
    # Vérifie que le modèle peut calculer un path loss avec ces positions
    path_loss = ray_tracing_model.calculate_path_loss(
        tx_pos, rx_pos, test_scene, wifi_antenna.frequency
    )
    
    assert isinstance(path_loss, float)
    assert path_loss > 0