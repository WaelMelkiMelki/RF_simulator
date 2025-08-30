# src/core/domain/antenna.py
# --- Classes d'antennes ---

class BaseAntenna:
    """
    Classe de base abstraite pour tous les types d'antennes.
    Définit l'interface commune et les attributs de base.
    """
    def __init__(self, name: str = "Antenne Inconnue", position: tuple = (0.0, 0.0, 0.0), frequency: float = 2.4e9, power_dbm: float = 20.0, coverage_radius: float = 15.0):
        self.name = name
        self.position = position # Tuple (x, y, z)
        self.frequency = frequency # Fréquence en Hz
        self.power_dbm = power_dbm # Puissance en dBm
        self.coverage_radius = coverage_radius # Rayon de couverture en mètres

    def __repr__(self):
        return f"<BaseAntenna(name='{self.name}', position={self.position}, frequency={self.frequency}, power_dbm={self.power_dbm}, coverage_radius={self.coverage_radius})>"

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
    def __init__(self, name="Antenne WiFi", position=(0.0, 0.0, 0.0), frequency=2.4e9, power_dbm=20.0, ssid="MonReseauWiFi", coverage_radius=15.0):
        super().__init__(name, position, frequency, power_dbm, coverage_radius)
        self.ssid = ssid
        self.coverage_radius = coverage_radius
        self.type = "wifi"

    def calculate_radiation_pattern(self, theta=0, phi=0):
        # Pattern omnidirectionnel approximé (dipôle)
        import numpy as np
        return np.sin(theta)**2  # Gain relatif (0 à 1)

    def __repr__(self):
        return f"<WiFiAntenna(name='{self.name}', ssid='{self.ssid}', position={self.position}, frequency={self.frequency/1e9}GHz, power={self.power_dbm}dBm, coverage_radius={self.coverage_radius})>"

class Antenna5G(BaseAntenna):
    """
    Représente une antenne 5G.
    """
    def __init__(self, name="Antenne 5G", position=(0.0, 0.0, 0.0), frequency=3.5e9, power_dbm=40.0, band="n78", coverage_radius=15.0):
        super().__init__(name, position, frequency, power_dbm, coverage_radius)
        self.band = band # Ex: n78, n79
        self.coverage_radius = coverage_radius
        self.type = "5g"

    def calculate_radiation_pattern(self, theta=0, phi=0):
        # Pattern directionnel simple (ex: beamforming basique)
        import numpy as np
        return np.cos(theta)**4  # Plus directif

    def __repr__(self):
        return f"<Antenna5G(name='{self.name}', band='{self.band}', position={self.position}, frequency={self.frequency/1e9}GHz, power={self.power_dbm}dBm, coverage_radius={self.coverage_radius})>"

class YagiAntenna(BaseAntenna):
    """
    Représente une antenne Yagi-Uda.
    """
    def __init__(self, name="Antenne Yagi", position=(0.0, 0.0, 0.0), frequency=2.4e9, power_dbm=25.0, gain_dbi=10.0, direction=(0.0, 0.0), coverage_radius=15.0):
        super().__init__(name, position, frequency, power_dbm, coverage_radius)
        self.gain_dbi = gain_dbi # Gain en dBi
        self.direction = direction # Direction principale (azimuth, elevation) en degrés
        self.coverage_radius = coverage_radius
        self.type = "yagi"

    def __repr__(self):
        return f"<YagiAntenna(name='{self.name}', gain={self.gain_dbi}dBi, direction={self.direction}, coverage_radius={self.coverage_radius})>"