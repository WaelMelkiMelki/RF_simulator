# tests/test_units_validation.py
"""
Tests de validation des unités physiques du simulateur RF.
Vérifie que toutes les conversions d'unités sont correctes.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.domain.units_converter import UnitsConverter
from core.domain.antenna_factory import AntennaFactory
from core.domain.rf_models import FreeSpaceModel
import numpy as np

def test_frequency_conversion():
    """Test de conversion des fréquences."""
    print("=== Test conversion des fréquences ===")
    
    test_cases = [
        ("2.4GHz", 2.4e9),
        ("900MHz", 900e6),
        ("5GHz", 5e9),
        ("28GHz", 28e9),
        ("1800MHz", 1800e6),
        (2400000000, 2400000000),  # Déjà en Hz
        ("2400000000", 2400000000)  # String de Hz
    ]
    
    for input_freq, expected_hz in test_cases:
        try:
            result = UnitsConverter.parse_frequency(input_freq)
            status = "✅" if abs(result - expected_hz) < 1e6 else "❌"
            print(f"{status} '{input_freq}' -> {result} Hz (attendu: {expected_hz})")
        except Exception as e:
            print(f"❌ Erreur avec '{input_freq}': {e}")

def test_power_conversion():
    """Test de conversion des puissances."""
    print("\n=== Test conversion des puissances ===")
    
    test_cases = [
        ("20dBm", 20.0),
        ("30", 30.0),
        ("1W", 30.0),  # 1W = 30dBm
        ("100mW", 20.0),  # 100mW = 20dBm
        (25, 25.0)  # Déjà en dBm
    ]
    
    for input_power, expected_dbm in test_cases:
        try:
            result = UnitsConverter.parse_power(input_power)
            status = "✅" if abs(result - expected_dbm) < 0.1 else "❌"
            print(f"{status} '{input_power}' -> {result:.1f} dBm (attendu: {expected_dbm})")
        except Exception as e:
            print(f"❌ Erreur avec '{input_power}': {e}")

def test_antenna_creation():
    """Test de création d'antennes avec conversion d'unités."""
    print("\n=== Test création d'antennes ===")
    
    factory = AntennaFactory()
    
    # Test WiFi avec unités mixtes
    wifi_config = {
        "name": "Test WiFi",
        "position": (0, 0, 2),
        "frequency": "2.4GHz",
        "power_dbm": "20dBm",
        "coverage_radius": "15m",
        "ssid": "TestNetwork"
    }
    
    try:
        wifi_antenna = factory.create_antenna("wifi", wifi_config)
        print(f"✅ WiFi: {wifi_antenna.get_frequency_display()}, {wifi_antenna.power_dbm}dBm, {wifi_antenna.coverage_radius}m")
        
        # Vérifier que la fréquence est en Hz
        assert wifi_antenna.frequency == 2.4e9, f"Fréquence incorrecte: {wifi_antenna.frequency}"
        
    except Exception as e:
        print(f"❌ Erreur création WiFi: {e}")
    
    # Test 5G avec unités mixtes
    antenna_5g_config = {
        "name": "Test 5G",
        "position": (10, 10, 5),
        "frequency": "3.5GHz",
        "power_dbm": "40dBm",
        "coverage_radius": "20m",
        "band": "n78"
    }
    
    try:
        antenna_5g = factory.create_antenna("5g", antenna_5g_config)
        print(f"✅ 5G: {antenna_5g.get_frequency_display()}, {antenna_5g.power_dbm}dBm, {antenna_5g.coverage_radius}m")
        
        # Vérifier que la fréquence est en Hz
        assert antenna_5g.frequency == 3.5e9, f"Fréquence incorrecte: {antenna_5g.frequency}"
        
    except Exception as e:
        print(f"❌ Erreur création 5G: {e}")

def test_propagation_model():
    """Test des modèles de propagation avec unités correctes."""
    print("\n=== Test modèle de propagation ===")
    
    try:
        factory = AntennaFactory()
        
        # Créer une antenne de test
        config = {
            "name": "Test Propagation",
            "position": (0, 0, 2),
            "frequency": "2.4GHz",
            "power_dbm": "30dBm",
            "coverage_radius": "50m"
        }
        
        antenna = factory.create_antenna("wifi", config)
        model = FreeSpaceModel()
        
        # Test à différentes distances
        test_distances = [1, 10, 100]  # mètres
        
        for distance in test_distances:
            rx_pos = (distance, 0, 2)
            loss = model.calculate_path_loss(
                antenna.position, rx_pos, None, antenna.frequency, antenna
            )
            
            # Vérifier que la perte est positive et réaliste
            if loss > 0 and loss < 200:
                print(f"✅ Distance {distance}m: Perte = {loss:.1f}dB")
                
                # Calculer RSSI
                rssi = antenna.power_dbm - loss
                print(f"   RSSI = {antenna.power_dbm}dBm - {loss:.1f}dB = {rssi:.1f}dBm")
            else:
                print(f"❌ Distance {distance}m: Perte anormale = {loss:.1f}dB")
                
    except Exception as e:
        print(f"❌ Erreur test propagation: {e}")

def test_fspl_formula():
    """Test spécifique de la formule FSPL."""
    print("\n=== Test formule FSPL ===")
    
    # Paramètres de test
    frequency = 2.4e9  # 2.4 GHz en Hz
    distance = 10      # 10 mètres
    c = 3e8           # Vitesse de la lumière
    
    # Calcul FSPL théorique
    fspl_theory = 20 * np.log10(distance) + 20 * np.log10(frequency) + 20 * np.log10(4*np.pi/c)
    
    # Calcul avec le modèle
    model = FreeSpaceModel()
    tx_pos = (0, 0, 0)
    rx_pos = (distance, 0, 0)
    fspl_model = model.calculate_path_loss(tx_pos, rx_pos, None, frequency)
    
    # Comparaison
    diff = abs(fspl_theory - fspl_model)
    status = "✅" if diff < 0.1 else "❌"
    
    print(f"{status} FSPL Théorique: {fspl_theory:.2f}dB")
    print(f"   FSPL Modèle:     {fspl_model:.2f}dB")
    print(f"   Différence:      {diff:.3f}dB")
    
    # Test avec longueur d'onde
    wavelength = c / frequency
    print(f"   Fréquence: {frequency/1e9:.1f} GHz")
    print(f"   Longueur d'onde: {wavelength*100:.1f} cm")

def test_units_validation():
    """Test de validation des plages physiques."""
    print("\n=== Test validation des plages ===")
    
    test_cases = [
        (2.4e9, 20, 10, True, "Valeurs normales"),
        (1e15, 20, 10, False, "Fréquence trop haute"),
        (2.4e9, 200, 10, False, "Puissance dangereuse"),
        (2.4e9, -200, 10, True, "Puissance très faible"),
        (2.4e9, 20, 50000, True, "Distance très longue")
    ]
    
    for freq, power, dist, expected_valid, description in test_cases:
        is_valid, warnings = UnitsConverter.validate_physical_ranges(freq, power, dist)
        status = "✅" if is_valid == expected_valid else "❌"
        print(f"{status} {description}: Valid={is_valid}, Warnings={len(warnings)}")
        if warnings:
            for warning in warnings:
                print(f"   ⚠️ {warning}")

if __name__ == "__main__":
    print("🧪 Tests de validation des unités physiques")
    print("=" * 50)
    
    test_frequency_conversion()
    test_power_conversion()
    test_antenna_creation()
    test_propagation_model()
    test_fspl_formula()
    test_units_validation()
    
    print("\n✅ Tests terminés. Vérifiez les résultats ci-dessus.")
