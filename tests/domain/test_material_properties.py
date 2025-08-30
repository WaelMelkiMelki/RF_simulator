# tests/domain/test_material_properties.py
"""
Tests pour les propriétés matérielles (MaterialProperties).
Vérifie l'intégration avec CacheManager et DatabaseAccess.
"""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path

# Importer les classes nécessaires
from core.domain.material_properties import MaterialProperties, get_material_by_name, MATERIAL_DATABASE
from core.infrastructure.cache_manager import SimulationCache

class TestMaterialProperties:
    """Tests pour MaterialProperties et ses intégrations."""

    def test_material_properties_creation(self):
        """Teste la création d'une instance de MaterialProperties."""
        try:
            # Créer une instance de MaterialProperties
            material = MaterialProperties(
                name="Test Material",
                frequency=2.4e9,
                attenuation=3.5
            )
            
            assert material is not None
            assert material.get_name() == "Test Material"
            assert material.get_frequency() == 2.4e9
            assert material.get_attenuation() == 3.5
            
            print("✅ MaterialProperties créée avec succès")
        except Exception as e:
            pytest.fail(f"Erreur lors de la création de MaterialProperties: {e}")

    def test_material_properties_attenuation_calculation(self):
        """Teste le calcul de l'atténuation selon la fréquence."""
        try:
            # Créer une instance de MaterialProperties
            material = MaterialProperties(
                name="Frequency Dependent Material",
                frequency=2.4e9,
                attenuation=5.0
            )
            
            # Calculer l'atténuation à différentes fréquences
            attenuation_2_4ghz = material.get_attenuation(2.4e9)
            attenuation_5ghz = material.get_attenuation(5.0e9)
            attenuation_1ghz = material.get_attenuation(1.0e9)
            
            # Vérifier que l'atténuation est calculée
            assert attenuation_2_4ghz == 5.0  # Fréquence de base
            assert attenuation_5ghz > attenuation_2_4ghz  # Fréquence plus élevée
            assert attenuation_1ghz < attenuation_2_4ghz  # Fréquence plus basse
            
            print("✅ Calcul de l'atténuation selon la fréquence réussi")
        except Exception as e:
            pytest.fail(f"Erreur lors du calcul de l'atténuation: {e}")

    def test_material_properties_database_lookup(self):
        """Teste la recherche de matériaux dans la base de données."""
        try:
            # Obtenir des matériaux connus
            concrete = get_material_by_name("Concrete")
            wood = get_material_by_name("Wood")
            glass = get_material_by_name("Glass")
            steel = get_material_by_name("Steel")
            
            # Vérifier que les matériaux sont trouvés
            assert concrete is not None
            assert wood is not None
            assert glass is not None
            assert steel is not None
            
            # Vérifier les propriétés
            assert concrete.get_name() == "Concrete"
            assert concrete.get_attenuation() == 5.0
            
            assert wood.get_name() == "Wood"
            assert wood.get_attenuation() == 0.5
            
            assert glass.get_name() == "Glass"
            assert glass.get_attenuation() == 0.2
            
            assert steel.get_name() == "Steel"
            assert steel.get_attenuation() == 20.0
            
            print("✅ Recherche de matériaux dans la base de données réussie")
        except Exception as e:
            pytest.fail(f"Erreur lors de la recherche de matériaux: {e}")

    def test_material_properties_unknown_material_handling(self):
        """Teste la gestion des matériaux inconnus."""
        try:
            # Obtenir un matériau inconnu
            unknown_material = get_material_by_name("UnknownMaterial")
            
            # Vérifier que l'objet est créé
            assert unknown_material is not None
            assert isinstance(unknown_material, MaterialProperties)
            
            # Vérifier que le nom est correct
            assert unknown_material.get_name() == "UnknownMaterial"
            
            # Vérifier que l'atténuation par défaut est utilisée
            default_attenuation = unknown_material.get_attenuation()
            assert default_attenuation == 1.0  # Valeur par défaut
            
            print("✅ Gestion des matériaux inconnus réussie")
        except Exception as e:
            pytest.fail(f"Erreur lors de la gestion des matériaux inconnus: {e}")

    def test_material_properties_cache_manager_integration(self):
        """Teste l'intégration de MaterialProperties avec CacheManager."""
        try:
            # Créer un cache temporaire
            with tempfile.TemporaryDirectory() as temp_dir:
                cache = SimulationCache(cache_dir=temp_dir)
                # Créer une clé de cache pour un matériau
                cache_key = ("Concrete", 2.4e9)
                material_data = {"name": "Concrete", "attenuation": 5.0, "frequency": 2.4e9}
                # Mettre en cache les données
                cache.cache_results(cache_key, material_data)
                # Récupérer les données du cache
                cached_data = cache.get_cached_results(cache_key)
                # Vérifier que les données sont correctes
                assert cached_data is not None
                assert cached_data["name"] == "Concrete"
                assert cached_data["attenuation"] == 5.0
                assert cached_data["frequency"] == 2.4e9
                print("✅ Intégration MaterialProperties avec CacheManager réussie")
                # Nettoyage explicite pour éviter le verrouillage du fichier sous Windows
                cache.close()
                del cache
                import gc
                import time
                gc.collect()
                time.sleep(0.1)
        except Exception as e:
            pytest.fail(f"Erreur lors de l'intégration avec CacheManager: {e}")

    def test_material_properties_database_access_integration(self):
        """Teste l'intégration de MaterialProperties avec DatabaseAccess."""
        try:
            # Vérifier que la base de données est accessible
            assert MATERIAL_DATABASE is not None
            assert isinstance(MATERIAL_DATABASE, dict)
            
            # Vérifier que les matériaux standards sont présents
            assert "Concrete" in MATERIAL_DATABASE
            assert "Wood" in MATERIAL_DATABASE
            assert "Glass" in MATERIAL_DATABASE
            assert "Steel" in MATERIAL_DATABASE
            
            # Vérifier les propriétés des matériaux
            concrete_props = MATERIAL_DATABASE["Concrete"]
            assert concrete_props.get_name() == "Concrete"
            assert concrete_props.get_attenuation() == 5.0
            
            wood_props = MATERIAL_DATABASE["Wood"]
            assert wood_props.get_name() == "Wood"
            assert wood_props.get_attenuation() == 0.5
            
            print("✅ Intégration MaterialProperties avec DatabaseAccess réussie")
        except Exception as e:
            pytest.fail(f"Erreur lors de l'intégration avec DatabaseAccess: {e}")

    def test_material_properties_frequency_scaling(self):
        """Teste l'échelle d'atténuation selon la fréquence."""
        try:
            # Créer un matériau avec une fréquence de base
            material = MaterialProperties(
                name="Scaling Material",
                frequency=2.4e9,  # 2.4 GHz
                attenuation=5.0
            )
            
            # Calculer l'atténuation à différentes fréquences
            frequencies = [1.0e9, 2.4e9, 5.0e9, 10.0e9]  # 1GHz, 2.4GHz, 5GHz, 10GHz
            attenuations = [material.get_attenuation(freq) for freq in frequencies]
            
            # Vérifier que l'atténuation augmente avec la fréquence
            # (sauf pour la fréquence de base)
            assert attenuations[1] == 5.0  # Fréquence de base
            assert attenuations[2] > attenuations[1]  # 5GHz > 2.4GHz
            assert attenuations[3] > attenuations[2]  # 10GHz > 5GHz
            # Note: 1GHz < 2.4GHz, donc l'atténuation pourrait être inférieure ou supérieure
            # selon l'algorithme de scaling
            
            print("✅ Échelle d'atténuation selon la fréquence vérifiée")
        except Exception as e:
            pytest.fail(f"Erreur lors du test de l'échelle d'atténuation: {e}")

    def test_material_properties_repr_and_str(self):
        """Teste les représentations string de MaterialProperties."""
        try:
            # Créer une instance de MaterialProperties
            material = MaterialProperties(
                name="Test Material",
                frequency=2.4e9,
                attenuation=3.5
            )
            
            # Obtenir les représentations
            repr_str = repr(material)
            str_str = str(material)
            
            # Vérifier que les représentations contiennent les informations attendues
            assert "Test Material" in repr_str
            assert "2.4GHz" in repr_str
            assert "3.5" in repr_str
            
            assert "Test Material" in str_str
            assert "2.4GHz" in str_str
            assert "3.5" in str_str
            
            print("✅ Représentations string de MaterialProperties vérifiées")
        except Exception as e:
            pytest.fail(f"Erreur lors du test des représentations string: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
