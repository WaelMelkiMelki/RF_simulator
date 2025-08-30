# tests/domain/test_antenna_services.py
import pytest
from core.domain.antenna_factory import AntennaFactory
from core.domain.antenna import BaseAntenna, WiFiAntenna, Antenna5G

def test_antenna_factory_creates_base_antenna():
    """Vérifie que AntennaFactory peut créer une BaseAntenna"""
    factory = AntennaFactory()
    antenna = factory.create_antenna("base", {
        "position": [0, 0, 1],
        "power_dbm": 20.0,
        "name": "Test Base Antenna"
    })
    assert isinstance(antenna, BaseAntenna)
    assert antenna.position == [0, 0, 1]
    assert antenna.power_dbm == 20.0
    assert antenna.name == "Test Base Antenna"
    assert hasattr(antenna, 'frequency')

def test_antenna_factory_creates_wifi_antenna():
    """Vérifie que AntennaFactory peut créer une WiFiAntenna"""
    factory = AntennaFactory()
    antenna = factory.create_antenna("wifi", {
        "position": [0, 0, 1],
        "frequency": 2.4e9,
        "power_dbm": 20.0,
        "ssid": "TestNetwork"
    })
    assert isinstance(antenna, WiFiAntenna)
    assert antenna.position == [0, 0, 1]
    assert antenna.frequency == 2.4e9
    assert antenna.power_dbm == 20.0
    assert antenna.ssid == "TestNetwork"
    assert hasattr(antenna, "calculate_radiation_pattern")

def test_antenna_factory_creates_5g_antenna():
    """Vérifie que AntennaFactory peut créer une Antenna5G"""
    factory = AntennaFactory()
    antenna = factory.create_antenna("5g", {
        "position": [5, 5, 1.5],
        "frequency": 3.5e9,
        "power_dbm": 30.0,
        "band": "n78"
    })
    assert isinstance(antenna, Antenna5G)
    assert antenna.position == [5, 5, 1.5]
    assert antenna.frequency == 3.5e9
    assert antenna.power_dbm == 30.0
    assert antenna.band == "n78"
    assert hasattr(antenna, "calculate_radiation_pattern")

def test_base_antenna_is_parent_of_wifi_antenna(wifi_antenna):
    """Vérifie que WiFiAntenna hérite de BaseAntenna"""
    assert isinstance(wifi_antenna, BaseAntenna)
    assert hasattr(wifi_antenna, "position")
    assert hasattr(wifi_antenna, "calculate_radiation_pattern")
    assert hasattr(wifi_antenna, "power_dbm")

def test_base_antenna_is_parent_of_5g_antenna(antenna_5g):
    """Vérifie que Antenna5G hérite de BaseAntenna"""
    assert isinstance(antenna_5g, BaseAntenna)
    assert hasattr(antenna_5g, "position")
    assert hasattr(antenna_5g, "calculate_radiation_pattern")
    assert hasattr(antenna_5g, "power_dbm")