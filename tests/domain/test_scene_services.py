# tests/domain/test_scene_services.py
import pytest
import numpy as np
from pyvista import PolyData
from core.domain.scene import Scene3D
from core.domain.material_properties import MaterialProperties, CONCRETE, WOOD
from core.domain.spatial_index import SpatialIndex

def test_scene_uses_material_properties(test_scene):
    """Vérifie que Scene3D utilise MaterialProperties"""
    # Ajoute des propriétés matérielles à la scène
    test_scene.material_properties = {
        "walls": {"material": CONCRETE, "attenuation": 5.0},
        "floor": {"material": WOOD, "attenuation": 0.5}
    }
    
    assert test_scene.material_properties is not None
    assert "walls" in test_scene.material_properties
    assert "floor" in test_scene.material_properties
    assert test_scene.material_properties["walls"]["attenuation"] == 5.0
    assert test_scene.material_properties["floor"]["attenuation"] == 0.5
    
    # Vérifie que la méthode get_material_properties existe
    assert hasattr(test_scene, "get_material_properties")
    material = test_scene.get_material_properties("walls")
    assert material["attenuation"] == 5.0

def test_scene_uses_spatial_index(test_scene, simple_mesh):
    """Vérifie que Scene3D utilise SpatialIndex"""
    assert test_scene.spatial_index is not None
    assert hasattr(test_scene.spatial_index, "insert")
    assert hasattr(test_scene.spatial_index, "query_point")
    
    # Test d'insertion et de requête
    test_point = [0.5, 0.5, 0.5]
    test_scene.spatial_index.insert(test_point, "test_data")
    
    results = test_scene.spatial_index.query_point(0.5, 0.5, 0.5, radius=0.1)
    assert len(results) > 0
    assert results[0][0] == pytest.approx(test_point, 0.01)
    assert results[0][1] == "test_data"

def test_scene_uses_file_loader(test_scene, simple_mesh):
    """Vérifie que Scene3D peut charger un maillage via FileLoader"""
    # Nous testons déjà que load_mesh fonctionne via test_scene
    assert test_scene.mesh is not None
    assert len(test_scene.mesh.points) > 0
    assert len(test_scene.mesh.faces) > 0
    
    # Vérifie que la méthode process_glb_data existe
    assert hasattr(test_scene, "process_glb_data")
    
    # Test avec un objet MultiBlock pour simuler un fichier GLB
    from pyvista import MultiBlock
    block = MultiBlock()
    points = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]])
    faces = np.array([4, 0, 1, 2, 3])
    block["mesh_0"] = PolyData(points, faces)
    
    test_scene.process_glb_data(block)
    assert test_scene.mesh is not None
    assert len(test_scene.mesh.points) == 4
    assert len(test_scene.mesh.faces) == 5  # 4 (nombre de points) + les indices

def test_material_properties_basic_functionality():
    """Vérifie les fonctionnalités de base de MaterialProperties"""
    # Test avec des valeurs par défaut
    material = MaterialProperties()
    assert material.get_name() == "Generic"
    assert material.get_frequency() == 2.4e9
    assert material.get_attenuation() == 1.0
    
    # Test avec des valeurs personnalisées
    concrete = MaterialProperties("Concrete", 3.5e9, 6.0)
    assert concrete.get_name() == "Concrete"
    assert concrete.get_frequency() == 3.5e9
    assert concrete.get_attenuation() == 6.0
    
    # Test avec une fréquence différente
    assert concrete.get_attenuation(7e9) > concrete.get_attenuation()

def test_material_database():
    """Vérifie la base de données de matériaux"""
    from core.domain.material_properties import CONCRETE, WOOD, GLASS, STEEL, get_material_by_name
    
    assert get_material_by_name("Concrete").get_name() == "Concrete"
    assert get_material_by_name("Wood").get_name() == "Wood"
    assert get_material_by_name("Glass").get_name() == "Glass"
    assert get_material_by_name("Steel").get_name() == "Steel"
    assert get_material_by_name("Unknown").get_name() == "Unknown"
    
    # Vérifie les valeurs par défaut
    assert get_material_by_name("Concrete").get_attenuation() == 5.0
    assert get_material_by_name("Wood").get_attenuation() == 0.5

def test_spatial_index_functionality():
    """Vérifie les fonctionnalités de base de SpatialIndex"""
    spatial_index = SpatialIndex()
    
    # Insère quelques points
    spatial_index.insert([0.5, 0.5, 0.5], "point1")
    spatial_index.insert([1.5, 1.5, 1.5], "point2")
    spatial_index.insert([2.5, 2.5, 2.5], "point3")
    
    # Test de requête ponctuelle
    results = spatial_index.query_point(0.5, 0.5, 0.5, radius=0.1)
    assert len(results) == 1
    assert results[0][1] == "point1"
    
    # Test de requête avec un rayon plus grand
    results = spatial_index.query_point(0.5, 0.5, 0.5, radius=1.5)
    assert len(results) >= 1  # Au moins point1 devrait être trouvé
    
    # Test de statistiques
    stats = spatial_index.get_statistics()
    assert isinstance(stats, dict)