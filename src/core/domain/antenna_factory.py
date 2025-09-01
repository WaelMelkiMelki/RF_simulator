
# src/core/domain/antenna_factory.py
"""
Factory pour la création d'antennes de différents types.
"""
from core.domain.antenna import BaseAntenna, WiFiAntenna, Antenna5G, YagiAntenna
from core.domain.units_converter import UnitsConverter
import logging

logger = logging.getLogger(__name__)

class AntennaFactory:
    """
    Factory pour instancier des objets antennes en fonction du type et de la configuration.
    """
    def create_antenna(self, antenna_type: str, config: dict):
        """
        Crée une instance d'antenne en fonction du type et du dictionnaire de configuration.

        Args:
            antenna_type (str): Le type d'antenne ("wifi", "5g", "yagi", etc.).
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
        
        # CORRECTION: Utiliser le convertisseur d'unités pour tous les paramètres
        try:
            # Paramètres communs avec conversion d'unités
            common_params = {
                "name": config.get("name", "Antenne Inconnue"),
                "position": config.get("position", (0.0, 0.0, 0.0)),
                "frequency": config.get("frequency", "2.4GHz"),  # Sera converti par la classe
                "power_dbm": config.get("power_dbm", "20dBm"),   # Sera converti par la classe
                "coverage_radius": config.get("coverage_radius", "15m")  # Sera converti par la classe
            }
            
            logger.debug(f"AntennaFactory: Création antenne '{antenna_type}' avec config: {config}")
            
            # Créer l'antenne selon le type
            if antenna_type_lc == "wifi":
                wifi_params = common_params.copy()
                wifi_params["ssid"] = config.get("ssid", "MonReseauWiFi")
                return WiFiAntenna(**wifi_params)
                
            elif antenna_type_lc == "5g":
                antenna_5g_params = common_params.copy()
                antenna_5g_params["band"] = config.get("band", "n78")
                return Antenna5G(**antenna_5g_params)
                
            elif antenna_type_lc == "yagi":
                yagi_params = common_params.copy()
                yagi_params["gain_dbi"] = config.get("gain_dbi", 10.0)
                yagi_params["direction"] = config.get("direction", (0.0, 0.0))
                return YagiAntenna(**yagi_params)
                
            elif antenna_type_lc == "base":
                return BaseAntenna(**common_params)
                
            else:
                raise ValueError(f"AntennaFactory: Type d'antenne non supporté : {antenna_type}")
                
        except Exception as e:
            logger.error(f"AntennaFactory: Erreur lors de la conversion des paramètres: {e}")
            raise ValueError(f"Paramètres invalides pour l'antenne {antenna_type}: {e}")
