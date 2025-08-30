
# src/core/domain/antenna_factory.py
"""
Factory pour la création d'antennes de différents types.
"""
from core.domain.antenna import BaseAntenna, WiFiAntenna, Antenna5G

class AntennaFactory:
    """
    Factory pour instancier des objets antennes en fonction du type et de la configuration.
    """
    def create_antenna(self, antenna_type: str, config: dict):
        """
        Crée une instance d'antenne en fonction du type et du dictionnaire de configuration.

        Args:
            antenna_type (str): Le type d'antenne ("WiFi", "5G", etc.).
            config (dict): Dictionnaire contenant les paramètres de l'antenne
                           (position, frequency, power_dbm, etc.).

        Returns:
            BaseAntenna: Une instance de la classe d'antenne appropriée.

        Raises:
            ValueError: Si le type d'antenne n'est pas supporté.
        """
        if not isinstance(antenna_type, str):
            raise TypeError(f"AntennaFactory: antenna_type doit être une chaîne, reçu: {type(antenna_type)}")
        antenna_type_lc = antenna_type.lower()
        common_params = {
            "name": config.get("name", "Antenne Inconnue"),
            "position": config["position"],
            "power_dbm": config["power_dbm"],
            "coverage_radius": config.get("coverage_radius", 15.0)
        }
        if antenna_type_lc != "base":
            freq_input = config["frequency"]
            if isinstance(freq_input, str):
                if "GHz" in freq_input:
                    frequency_hz = float(freq_input.replace("GHz", "")) * 1e9
                elif "MHz" in freq_input:
                    frequency_hz = float(freq_input.replace("MHz", "")) * 1e6
                else:
                    frequency_hz = float(freq_input)
            else:
                frequency_hz = float(freq_input)
            common_params["frequency"] = frequency_hz

        if antenna_type_lc == "wifi":
            wifi_params = common_params.copy()
            wifi_params["ssid"] = config.get("ssid", "MonReseauWiFi")
            return WiFiAntenna(**wifi_params)
        elif antenna_type_lc == "5g":
            return Antenna5G(**common_params)
        elif antenna_type_lc == "base":
            return BaseAntenna(**common_params)
        else:
            raise ValueError(f"AntennaFactory: Type d'antenne non supporte : {antenna_type}")
