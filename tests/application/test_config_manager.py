# tests/application/test_config_manager.py
"""
Tests pour le composant ConfigManager de la couche Application.
"""

import pytest
import tempfile
import os
import json
import yaml
from core.application.config_manager import ConfigManager, ConfigValidationError

class TestConfigManager:
    """Tests pour ConfigManager"""

    def test_config_manager_import(self):
        """Teste l'importation de ConfigManager."""
        try:
            from core.application.config_manager import ConfigManager
            assert ConfigManager is not None
            print("✅ ConfigManager importé avec succès.")
        except ImportError as e:
            pytest.fail(f"❌ Échec de l'importation de ConfigManager: {e}")

    def test_config_manager_instantiation(self):
        """Teste l'instanciation de ConfigManager sans fichier."""
        try:
            config_manager = ConfigManager()
            assert config_manager is not None
            assert config_manager.config_data == {}
            print("✅ ConfigManager instancié avec succès (sans fichier).")
        except Exception as e:
            pytest.fail(f"❌ Échec de l'instanciation de ConfigManager: {e}")

    def test_load_valid_json_config(self):
        """Teste le chargement d'un fichier JSON valide."""
        # Créer un fichier de configuration JSON temporaire
        valid_config = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_config, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            assert config_manager.config_data == valid_config
            print("✅ Chargement d'un fichier JSON valide réussi.")
        except Exception as e:
            pytest.fail(f"❌ Échec du chargement d'un fichier JSON valide: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_load_valid_yaml_config(self):
        """Teste le chargement d'un fichier YAML valide."""
        # Créer un fichier de configuration YAML temporaire
        valid_config = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "ray_tracing",
                "resolution": 0.5
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_config, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            assert config_manager.config_data == valid_config
            print("✅ Chargement d'un fichier YAML valide réussi.")
        except Exception as e:
            pytest.fail(f"❌ Échec du chargement d'un fichier YAML valide: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_load_invalid_file_format(self):
        """Teste le chargement d'un fichier avec un format non supporté."""
        # Créer un fichier de configuration avec un format non supporté
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("invalid format")
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            pytest.fail("❌ Le chargement aurait dû échouer pour un format non supporté.")
        except ConfigValidationError as e:
            assert "non supporté" in str(e)
            print("✅ Gestion correcte d'un format de fichier non supporté.")
        except Exception as e:
            pytest.fail(f"❌ Erreur inattendue lors du chargement d'un format non supporté: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_load_nonexistent_file(self):
        """Teste le chargement d'un fichier qui n'existe pas."""
        nonexistent_path = "/path/to/nonexistent/config.json"
        
        try:
            config_manager = ConfigManager(nonexistent_path)
            pytest.fail("❌ Le chargement aurait dû échouer pour un fichier inexistant.")
        except FileNotFoundError as e:
            assert "non trouvé" in str(e)
            print("✅ Gestion correcte d'un fichier de configuration inexistant.")
        except Exception as e:
            pytest.fail(f"❌ Erreur inattendue lors du chargement d'un fichier inexistant: {e}")

    def test_config_validation_success(self):
        """Teste la validation d'une configuration valide."""
        valid_config = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(valid_config, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            # La validation est faite automatiquement lors du chargement
            assert config_manager.config_data == valid_config
            print("✅ Validation d'une configuration valide réussie.")
        except Exception as e:
            pytest.fail(f"❌ Échec de la validation d'une configuration valide: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_config_validation_missing_required_fields(self):
        """Teste la validation d'une configuration avec des champs requis manquants."""
        invalid_config = {
            "project": {
                "name": "Test Project"
                # "author" manquant
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_config, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            pytest.fail("❌ La validation aurait dû échouer pour une configuration invalide.")
        except ConfigValidationError as e:
            assert "requis" in str(e)
            print("✅ Gestion correcte d'une configuration avec des champs requis manquants.")
        except Exception as e:
            pytest.fail(f"❌ Erreur inattendue lors de la validation d'une configuration invalide: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_config_validation_invalid_model(self):
        """Teste la validation d'une configuration avec un modèle invalide."""
        invalid_config = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "invalid_model",  # Modèle non supporté
                "resolution": 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_config, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            pytest.fail("❌ La validation aurait dû échouer pour un modèle invalide.")
        except ConfigValidationError as e:
            assert "non supporté" in str(e)
            print("✅ Gestion correcte d'une configuration avec un modèle invalide.")
        except Exception as e:
            pytest.fail(f"❌ Erreur inattendue lors de la validation d'un modèle invalide: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_config_validation_invalid_resolution(self):
        """Teste la validation d'une configuration avec une résolution invalide."""
        invalid_config = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": -1.0  # Résolution négative
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_config, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            pytest.fail("❌ La validation aurait dû échouer pour une résolution invalide.")
        except ConfigValidationError as e:
            assert "positif" in str(e)
            print("✅ Gestion correcte d'une configuration avec une résolution invalide.")
        except Exception as e:
            pytest.fail(f"❌ Erreur inattendue lors de la validation d'une résolution invalide: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_get_simulation_config(self):
        """Teste la récupération de la configuration de simulation."""
        config_data = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "ray_tracing",
                "resolution": 0.5
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            simulation_config = config_manager.get_simulation_config()
            assert simulation_config == config_data["simulation"]
            print("✅ Récupération de la configuration de simulation réussie.")
        except Exception as e:
            pytest.fail(f"❌ Échec de la récupération de la configuration de simulation: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_get_project_info(self):
        """Teste la récupération des informations du projet."""
        config_data = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            project_info = config_manager.get_project_info()
            assert project_info == config_data["project"]
            print("✅ Récupération des informations du projet réussie.")
        except Exception as e:
            pytest.fail(f"❌ Échec de la récupération des informations du projet: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_get_antennas_config(self):
        """Teste la récupération de la configuration des antennes."""
        config_data = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            },
            "antennas": [
                {
                    "type": "wifi",
                    "name": "WiFi Antenna 1",
                    "position": {"x": 0, "y": 0, "z": 1},
                    "frequency": 2.4e9,
                    "power_dbm": 20.0,
                    "ssid": "MyNetwork"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            antennas_config = config_manager.get_antennas_config()
            assert antennas_config == config_data["antennas"]
            print("✅ Récupération de la configuration des antennes réussie.")
        except Exception as e:
            pytest.fail(f"❌ Échec de la récupération de la configuration des antennes: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_get_export_config(self):
        """Teste la récupération de la configuration d'export."""
        config_data = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            },
            "export": {
                "auto_export": True,
                "output_dir": "./results",
                "formats": ["csv", "vtk", "png"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            export_config = config_manager.get_export_config()
            assert export_config == config_data["export"]
            print("✅ Récupération de la configuration d'export réussie.")
        except Exception as e:
            pytest.fail(f"❌ Échec de la récupération de la configuration d'export: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_get_full_config(self):
        """Teste la récupération de la configuration complète."""
        config_data = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            full_config = config_manager.get_full_config()
            assert full_config == config_data
            print("✅ Récupération de la configuration complète réussie.")
        except Exception as e:
            pytest.fail(f"❌ Échec de la récupération de la configuration complète: {e}")
        finally:
            os.unlink(temp_file_path)

    def test_save_config_json(self):
        """Teste la sauvegarde de la configuration en JSON."""
        config_data = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            
            # Modifier la configuration
            config_manager.config_data["project"]["name"] = "Modified Project"
            
            # Sauvegarder dans un nouveau fichier
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                new_file_path = f.name
            
            config_manager.save_config(new_file_path)
            
            # Vérifier que le fichier a été créé et contient les bonnes données
            with open(new_file_path, 'r') as f:
                saved_config = json.load(f)
                
            assert saved_config["project"]["name"] == "Modified Project"
            print("✅ Sauvegarde de la configuration en JSON réussie.")
            
        except Exception as e:
            pytest.fail(f"❌ Échec de la sauvegarde de la configuration en JSON: {e}")
        finally:
            os.unlink(temp_file_path)
            if 'new_file_path' in locals():
                os.unlink(new_file_path)

    def test_save_config_yaml(self):
        """Teste la sauvegarde de la configuration en YAML."""
        config_data = {
            "project": {
                "name": "Test Project",
                "author": "Test Author"
            },
            "simulation": {
                "model": "free_space",
                "resolution": 1.0
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_file_path = f.name

        try:
            config_manager = ConfigManager(temp_file_path)
            
            # Modifier la configuration
            config_manager.config_data["project"]["name"] = "Modified Project"
            
            # Sauvegarder dans un nouveau fichier YAML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                new_file_path = f.name
            
            config_manager.save_config(new_file_path)
            
            # Vérifier que le fichier a été créé et contient les bonnes données
            with open(new_file_path, 'r') as f:
                saved_config = yaml.safe_load(f)
                
            assert saved_config["project"]["name"] == "Modified Project"
            print("✅ Sauvegarde de la configuration en YAML réussie.")
            
        except Exception as e:
            pytest.fail(f"❌ Échec de la sauvegarde de la configuration en YAML: {e}")
        finally:
            os.unlink(temp_file_path)
            if 'new_file_path' in locals():
                os.unlink(new_file_path)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
