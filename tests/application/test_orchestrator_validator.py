# tests/application/test_orchestrator_validator.py
"""
Tests pour vérifier la dépendance entre SimulationOrchestrator et DataValidator
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from pyvista import PolyData

# Importer les classes nécessaires
from core.application.simulation_orchestrator import SimulationOrchestrator
from core.application.data_validator import DataValidator, DataValidationError
from core.domain.antenna import BaseAntenna
from core.domain.scene import Scene3D

class TestOrchestratorValidatorDependencies:
    """Tests pour les dépendances entre SimulationOrchestrator et DataValidator"""

    @pytest.fixture
    def valid_scene(self):
        """Crée une scène valide pour les tests"""
        scene = Scene3D()
        # Créer un maillage simple
        points = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
            [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]
        ])
        faces = np.array([4, 0, 1, 2, 3, 4, 4, 5, 6, 7, 4, 0, 1, 5, 4])
        mesh = PolyData(points, faces)
        scene.mesh = mesh
        return scene

    @pytest.fixture
    def valid_antenna(self):
        """Crée une antenne valide pour les tests"""
        return BaseAntenna(
            name="Test Antenna",
            position=[0, 0, 1],
            frequency=2.4e9,
            power_dbm=20.0
        )

    def test_orchestrator_calls_validator_on_valid_data(self, valid_scene, valid_antenna):
        """Teste que SimulationOrchestrator appelle DataValidator avec des données valides"""
        # Arrange
        orchestrator = SimulationOrchestrator()
        orchestrator.scene = valid_scene
        orchestrator.add_antenna("base", {
            "name": "Test Antenna",
            "position": [0, 0, 1],
            "frequency": 2.4e9,
            "power_dbm": 20.0
        })

        # Act & Assert
        # Vérifier que la validation réussit sans exception
        result = orchestrator.validate_data()
        assert result is True

    def test_orchestrator_handles_validator_scene_error(self):
        """Teste que SimulationOrchestrator gère correctement les erreurs de validation de scène"""
        # Arrange
        orchestrator = SimulationOrchestrator()
        orchestrator.scene = None  # Scène invalide
        orchestrator.add_antenna("base", {
            "name": "Test Antenna",
            "position": [0, 0, 1],
            "frequency": 2.4e9,
            "power_dbm": 20.0
        })

        # Act & Assert
        with pytest.raises(DataValidationError):
            orchestrator.validate_data()

    def test_orchestrator_handles_validator_antenna_error(self, valid_scene):
        """Teste que SimulationOrchestrator gère correctement les erreurs de validation d'antenne"""
        # Arrange
        orchestrator = SimulationOrchestrator()
        orchestrator.scene = valid_scene
        # Ajouter une antenne invalide (sans attributs requis)
        invalid_antenna = Mock()
        invalid_antenna.name = None  # Attribut manquant
        orchestrator.antennas = [invalid_antenna]

        # Act & Assert
        with pytest.raises(DataValidationError):
            orchestrator.validate_data()

    def test_orchestrator_validator_integration_with_real_validator(self, valid_scene, valid_antenna):
        """Teste l'intégration réelle avec DataValidator"""
        # Arrange
        orchestrator = SimulationOrchestrator()
        orchestrator.scene = valid_scene
        orchestrator.add_antenna("base", {
            "name": "Test Antenna",
            "position": [0, 0, 1],
            "frequency": 2.4e9,
            "power_dbm": 20.0
        })

        # Act
        validator = DataValidator()
        
        # Assert
        # Vérifier que les méthodes de validation sont appelables
        assert hasattr(validator, 'validate_scene')
        assert hasattr(validator, 'validate_antennas')
        
        # Vérifier que la validation fonctionne
        try:
            validator.validate_scene(orchestrator.scene)
            validator.validate_antennas(orchestrator.antennas)
            validation_passed = True
        except DataValidationError:
            validation_passed = False
            
        assert validation_passed is True

    def test_validator_accesses_antenna_attributes(self):
        """Teste que DataValidator accède correctement aux attributs d'antenne"""
        # Arrange
        validator = DataValidator()
        
        # Créer une antenne valide
        valid_antenna = BaseAntenna(
            name="Test Antenna",
            position=[0, 0, 1],
            frequency=2.4e9,
            power_dbm=20.0
        )
        
        # Act & Assert
        # Vérifier que l'antenne a les attributs attendus
        assert hasattr(valid_antenna, 'name')
        assert hasattr(valid_antenna, 'position')
        assert hasattr(valid_antenna, 'frequency')
        assert hasattr(valid_antenna, 'power_dbm')
        
        # Vérifier que DataValidator peut accéder à ces attributs
        try:
            validator.validate_antennas([valid_antenna])
            validation_passed = True
        except DataValidationError:
            validation_passed = False
            
        assert validation_passed is True

    @patch('core.application.data_validator.DataValidator.validate_scene')
    @patch('core.application.data_validator.DataValidator.validate_antennas')
    def test_orchestrator_calls_validator_methods(self, mock_validate_antennas, mock_validate_scene, valid_scene):
        """Teste que SimulationOrchestrator appelle les bonnes méthodes de DataValidator"""
        # Arrange
        orchestrator = SimulationOrchestrator()
        orchestrator.scene = valid_scene
        orchestrator.add_antenna("base", {
            "name": "Test Antenna",
            "position": [0, 0, 1],
            "frequency": 2.4e9,
            "power_dbm": 20.0
        })
        
        mock_validate_scene.return_value = None
        mock_validate_antennas.return_value = None

        # Act
        orchestrator.validate_data()

        # Assert
        mock_validate_scene.assert_called_once_with(valid_scene)
        mock_validate_antennas.assert_called_once_with(orchestrator.antennas)

    def test_orchestrator_validator_with_multiple_antenna_types(self, valid_scene):
        """Teste la validation avec différents types d'antennes"""
        # Arrange
        orchestrator = SimulationOrchestrator()
        orchestrator.scene = valid_scene
        
        # Ajouter différents types d'antennes via la factory
        orchestrator.add_antenna("base", {
            "name": "Base Antenna",
            "position": [0, 0, 1],
            "frequency": 2.4e9,
            "power_dbm": 20.0
        })
        
        orchestrator.add_antenna("wifi", {
            "name": "WiFi Antenna",
            "position": [1, 1, 1],
            "frequency": 2.4e9,
            "power_dbm": 20.0,
            "ssid": "TestNetwork"
        })

        # Act & Assert
        result = orchestrator.validate_data()
        assert result is True
