# src/core/domain/antenna.py
# --- Classes d'antennes ---

from .units_converter import UnitsConverter
import logging

logger = logging.getLogger(__name__)

class BaseAntenna:
    """
    Classe de base abstraite pour tous les types d'antennes.
    Définit l'interface commune et les attributs de base.
    """
    def __init__(self, name: str = "Antenne Inconnue", position: tuple = (0.0, 0.0, 0.0), frequency = 2.4e9, power_dbm = 20.0, coverage_radius: float = 15.0):
        self.name = name
        self.position = position # Tuple (x, y, z) en mètres
        
        # CORRECTION: Conversion automatique des unités
        try:
            self.frequency = UnitsConverter.parse_frequency(frequency)  # Toujours en Hz
            self.power_dbm = UnitsConverter.parse_power(power_dbm)      # Toujours en dBm
            self.coverage_radius = UnitsConverter.parse_distance(coverage_radius)  # Toujours en mètres
            
            # Validation des plages physiques
            is_valid, warnings = UnitsConverter.validate_physical_ranges(
                self.frequency, self.power_dbm, self.coverage_radius
            )
            
            if warnings:
                for warning in warnings:
                    logger.warning(f"Antenne '{name}': {warning}")
                    
            if not is_valid:
                raise ValueError(f"Paramètres physiques invalides pour l'antenne '{name}'")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de l'antenne '{name}': {e}")
            # Valeurs par défaut sécurisées
            self.frequency = 2.4e9      # 2.4 GHz
            self.power_dbm = 20.0       # 20 dBm
            self.coverage_radius = 15.0 # 15 mètres

    def __repr__(self):
        freq_display = UnitsConverter.format_frequency(self.frequency)
        return f"<BaseAntenne(nom='{self.name}', position={self.position}, fréquence={freq_display}, puissance={self.power_dbm}dBm, rayon={self.coverage_radius}m)>"

    def get_frequency_display(self):
        """Retourne la fréquence sous forme lisible."""
        return UnitsConverter.format_frequency(self.frequency)

    def calculate_radiation_pattern(self, theta=0, phi=0):
        """
        Calcule le diagramme de rayonnement de l'antenne pour une direction donnée.
        Args:
            theta: Angle d'élévation en radians
            phi: Angle d'azimut en radians
        Returns:
            float: Gain relatif dans la direction spécifiée
        """
        # Isotrope par défaut
        return 1.0

# Exemple de sous-classe (à développer plus tard)


# --- Classes d'antennes spécifiques ---

class WiFiAntenna(BaseAntenna):
    """
    Représente une antenne WiFi typique.
    """
    def __init__(self, name="Antenne WiFi", position=(0.0, 0.0, 0.0), frequency="2.4GHz", power_dbm="20dBm", ssid="MonReseauWiFi", coverage_radius="15m"):
        super().__init__(name, position, frequency, power_dbm, coverage_radius)
        self.ssid = ssid
        self.type = "wifi"

    def calculate_radiation_pattern(self, theta=0, phi=0):
        # Pattern omnidirectionnel approximé (dipôle)
        import numpy as np
        return np.sin(theta)**2  # Gain relatif (0 à 1)

    def __repr__(self):
        freq_display = self.get_frequency_display()
        return f"<WiFiAntenne(nom='{self.name}', ssid='{self.ssid}', position={self.position}, fréquence={freq_display}, puissance={self.power_dbm}dBm, rayon={self.coverage_radius}m)>"

class Antenna5G(BaseAntenna):
    """
    Représente une antenne 5G.
    """
    def __init__(self, name="Antenne 5G", position=(0.0, 0.0, 0.0), frequency="3.5GHz", power_dbm="40dBm", band="n78", coverage_radius="15m"):
        super().__init__(name, position, frequency, power_dbm, coverage_radius)
        self.band = band # Ex: n78, n79
        self.type = "5g"

    def calculate_radiation_pattern(self, theta=0, phi=0):
        # Pattern directionnel simple (ex: beamforming basique)
        import numpy as np
        return np.cos(theta)**4  # Plus directif

    def __repr__(self):
        freq_display = self.get_frequency_display()
        return f"<Antenne5G(nom='{self.name}', bande='{self.band}', position={self.position}, fréquence={freq_display}, puissance={self.power_dbm}dBm, rayon={self.coverage_radius}m)>"

class YagiAntenna(BaseAntenna):
    """
    Représente une antenne Yagi-Uda.
    """
    def __init__(self, name="Antenne Yagi", position=(0.0, 0.0, 0.0), frequency="2.4GHz", power_dbm="25dBm", gain_dbi=10.0, direction=(0.0, 0.0), coverage_radius="15m"):
        super().__init__(name, position, frequency, power_dbm, coverage_radius)
        self.gain_dbi = gain_dbi # Gain en dBi
        self.direction = direction # Direction principale (azimuth, elevation) en degrés
        self.type = "yagi"

    def __repr__(self):
        freq_display = self.get_frequency_display()
        return f"<AntenneYagi(nom='{self.name}', gain={self.gain_dbi}dBi, direction={self.direction}, fréquence={freq_display}, rayon={self.coverage_radius}m)>"