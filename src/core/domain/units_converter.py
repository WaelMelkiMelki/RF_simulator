# src/core/domain/units_converter.py
"""
Convertisseur d'unités physiques pour le simulateur RF.
Assure la cohérence des unités dans tous les calculs.
"""

import re
import logging

logger = logging.getLogger(__name__)

class UnitsConverter:
    """Convertisseur d'unités physiques pour RF."""
    
    @staticmethod
    def parse_frequency(freq_str):
        """
        Convertit une chaîne de fréquence en Hz.
        
        Args:
            freq_str (str): Fréquence sous forme de chaîne (ex: "2.4GHz", "900MHz")
            
        Returns:
            float: Fréquence en Hz
            
        Raises:
            ValueError: Si le format n'est pas reconnu
        """
        if isinstance(freq_str, (int, float)):
            # Déjà un nombre, supposer qu'il est en Hz
            return float(freq_str)
            
        if not isinstance(freq_str, str):
            raise ValueError(f"Format de fréquence invalide: {freq_str}")
            
        # Nettoyer la chaîne
        freq_str = freq_str.strip().replace(',', '.')
        
        # Pattern pour capturer nombre + unité
        pattern = r'^(\d+(?:\.\d+)?)\s*(Hz|KHz|MHz|GHz|THz)?$'
        match = re.match(pattern, freq_str, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Format de fréquence invalide: {freq_str}")
            
        value = float(match.group(1))
        unit = (match.group(2) or 'Hz').upper()
        
        # Conversion vers Hz
        multipliers = {
            'HZ': 1,
            'KHZ': 1e3,
            'MHZ': 1e6,
            'GHZ': 1e9,
            'THZ': 1e12
        }
        
        if unit not in multipliers:
            raise ValueError(f"Unité de fréquence inconnue: {unit}")
            
        result = value * multipliers[unit]
        logger.debug(f"Conversion fréquence: '{freq_str}' -> {result} Hz")
        return result
    
    @staticmethod
    def format_frequency(freq_hz):
        """
        Formate une fréquence en Hz vers une chaîne lisible.
        
        Args:
            freq_hz (float): Fréquence en Hz
            
        Returns:
            str: Fréquence formatée (ex: "2.4 GHz")
        """
        if freq_hz >= 1e12:
            return f"{freq_hz/1e12:.1f} THz"
        elif freq_hz >= 1e9:
            return f"{freq_hz/1e9:.1f} GHz"
        elif freq_hz >= 1e6:
            return f"{freq_hz/1e6:.1f} MHz"
        elif freq_hz >= 1e3:
            return f"{freq_hz/1e3:.1f} kHz"
        else:
            return f"{freq_hz:.1f} Hz"
    
    @staticmethod
    def parse_power(power_str):
        """
        Convertit une chaîne de puissance en dBm.
        
        Args:
            power_str (str): Puissance (ex: "20dBm", "1W", "30 dBm")
            
        Returns:
            float: Puissance en dBm
        """
        import numpy as np  # Import local pour éviter les erreurs
        
        if isinstance(power_str, (int, float)):
            # Déjà un nombre, supposer qu'il est en dBm
            return float(power_str)
            
        if not isinstance(power_str, str):
            raise ValueError(f"Format de puissance invalide: {power_str}")
            
        # Nettoyer la chaîne
        power_str = power_str.strip().replace(',', '.')
        
        # Pattern pour capturer nombre + unité
        pattern = r'^(\d+(?:\.\d+)?)\s*(dBm|W|mW|uW)?$'
        match = re.match(pattern, power_str, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Format de puissance invalide: {power_str}")
            
        value = float(match.group(1))
        unit = (match.group(2) or 'dBm').upper()
        
        # Conversion vers dBm
        if unit == 'DBM':
            return value
        elif unit == 'W':
            # P(dBm) = 10*log10(P(W)*1000)
            return 10 * np.log10(value * 1000)
        elif unit == 'MW':
            # P(dBm) = 10*log10(P(mW))
            return 10 * np.log10(value)
        elif unit == 'UW':
            # P(dBm) = 10*log10(P(uW)/1000)
            return 10 * np.log10(value / 1000)
        else:
            raise ValueError(f"Unité de puissance inconnue: {unit}")
    
    @staticmethod
    def parse_distance(dist_str):
        """
        Convertit une chaîne de distance en mètres.
        
        Args:
            dist_str (str): Distance (ex: "10m", "1km", "50cm")
            
        Returns:
            float: Distance en mètres
        """
        if isinstance(dist_str, (int, float)):
            # Déjà un nombre, supposer qu'il est en mètres
            return float(dist_str)
            
        if not isinstance(dist_str, str):
            raise ValueError(f"Format de distance invalide: {dist_str}")
            
        # Nettoyer la chaîne
        dist_str = dist_str.strip().replace(',', '.')
        
        # Pattern pour capturer nombre + unité
        pattern = r'^(\d+(?:\.\d+)?)\s*(mm|cm|m|km)?$'
        match = re.match(pattern, dist_str, re.IGNORECASE)
        
        if not match:
            raise ValueError(f"Format de distance invalide: {dist_str}")
            
        value = float(match.group(1))
        unit = (match.group(2) or 'm').lower()
        
        # Conversion vers mètres
        multipliers = {
            'mm': 1e-3,
            'cm': 1e-2,
            'm': 1,
            'km': 1e3
        }
        
        if unit not in multipliers:
            raise ValueError(f"Unité de distance inconnue: {unit}")
            
        return value * multipliers[unit]
    
    @staticmethod
    def validate_physical_ranges(frequency_hz, power_dbm, distance_m):
        """
        Valide que les valeurs physiques sont dans des plages réalistes.
        
        Args:
            frequency_hz (float): Fréquence en Hz
            power_dbm (float): Puissance en dBm
            distance_m (float): Distance en mètres
            
        Returns:
            tuple: (is_valid, warnings_list)
        """
        warnings = []
        is_valid = True
        
        # Validation fréquence (30 kHz à 300 GHz pour RF)
        if frequency_hz < 30e3:
            warnings.append(f"Fréquence très basse: {UnitsConverter.format_frequency(frequency_hz)}")
        elif frequency_hz > 300e9:
            warnings.append(f"Fréquence très haute: {UnitsConverter.format_frequency(frequency_hz)}")
            
        # Validation puissance (-100 dBm à +100 dBm)
        if power_dbm < -100:
            warnings.append(f"Puissance très faible: {power_dbm} dBm")
        elif power_dbm > 100:
            warnings.append(f"Puissance très élevée: {power_dbm} dBm")
            is_valid = False  # Dangereux
            
        # Validation distance (0.1 mm à 10 km)
        if distance_m < 1e-4:
            warnings.append(f"Distance très courte: {distance_m*1000:.1f} mm")
        elif distance_m > 10e3:
            warnings.append(f"Distance très longue: {distance_m/1000:.1f} km")
            
        return is_valid, warnings

# Tests unitaires
if __name__ == "__main__":
    import numpy as np
    
    print("=== Tests du convertisseur d'unités ===")
    
    # Tests fréquence
    test_frequencies = ["2.4GHz", "900MHz", "5GHz", "28GHz", "2400000000"]
    for freq in test_frequencies:
        try:
            hz = UnitsConverter.parse_frequency(freq)
            formatted = UnitsConverter.format_frequency(hz)
            print(f"'{freq}' -> {hz} Hz -> '{formatted}'")
        except Exception as e:
            print(f"Erreur avec '{freq}': {e}")
    
    # Tests puissance
    test_powers = ["20dBm", "30", "1W", "100mW"]
    for power in test_powers:
        try:
            dbm = UnitsConverter.parse_power(power)
            print(f"'{power}' -> {dbm} dBm")
        except Exception as e:
            print(f"Erreur avec '{power}': {e}")
    
    # Tests validation
    valid, warnings = UnitsConverter.validate_physical_ranges(2.4e9, 20, 10)
    print(f"Validation (2.4GHz, 20dBm, 10m): Valid={valid}, Warnings={warnings}")
