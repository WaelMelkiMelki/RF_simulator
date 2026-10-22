"""Shared, deterministic domain fixtures (no application startup at collection)."""
import pytest
import pyvista as pv
from core.domain.scene import Scene3D
from core.domain.antenna_factory import AntennaFactory
from core.domain.rf_models import FreeSpaceModel, SimpleRayTracingModel

@pytest.fixture
def simple_mesh():
    return pv.Box(bounds=(0., 1., 0., 1., 0., 1.))

@pytest.fixture
def test_scene(simple_mesh):
    return Scene3D(data=simple_mesh)

@pytest.fixture
def wifi_antenna():
    return AntennaFactory().create_antenna('wifi', {'name': 'WiFi', 'position': [0, 0, 1], 'frequency': '2.4GHz'})

@pytest.fixture
def antenna_5g():
    return AntennaFactory().create_antenna('5g', {'name': '5G', 'position': [0, 0, 1], 'frequency': '3.5GHz'})

@pytest.fixture
def free_space_model():
    return FreeSpaceModel()

@pytest.fixture
def ray_tracing_model():
    return SimpleRayTracingModel(max_reflections=2)
