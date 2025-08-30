# src/core/domain/material_properties.py
"""
Représente les propriétés électromagnétiques d'un matériau pour la simulation RF.
Fournit des méthodes pour obtenir l'atténuation en fonction de la fréquence.
"""

class MaterialProperties:
    """
    Encapsule les propriétés RF d'un matériau.
    """

    def __init__(self, name: str = "Generic", frequency: float = 2.4e9, attenuation: float = 1.0):
        """
        Initialise les propriétés d'un matériau.

        Args:
            name (str): Nom du matériau (ex: 'Concrete', 'Glass').
            frequency (float): Fréquence de référence pour l'atténuation (Hz).
            attenuation (float): Atténuation spécifique à cette fréquence (dB/m).
        """
        self.name = name
        self.base_frequency = frequency
        self.base_attenuation = attenuation
        # Pour une implémentation plus avancée, on pourrait avoir une liste
        # de tuples (frequency, attenuation) ou une fonction d'interpolation.

    def get_name(self) -> str:
        """
        Renvoie le nom du matériau.

        Returns:
            str: Le nom du matériau.
        """
        return self.name

    def get_frequency(self) -> float:
        """
        Renvoie la fréquence de référence.

        Returns:
            float: La fréquence de référence (Hz).
        """
        return self.base_frequency

    def get_attenuation(self, frequency: float = None) -> float:
        """
        Renvoie l'atténuation du matériau à une fréquence donnée.
        Pour l'instant, renvoie une valeur constante ou interpolée de manière basique.

        Args:
            frequency (float, optional): La fréquence à laquelle obtenir l'atténuation (Hz).
                                         Si None, utilise la fréquence de référence.

        Returns:
            float: L'atténuation en dB/m.
        """
        if frequency is None or frequency == self.base_frequency:
            return self.base_attenuation
        else:
            # Simplification : atténuation proportionnelle à la racine carrée de la fréquence
            # Cela devrait être remplacé par une base de données ou un modèle physique réel.
            # Attenuation = k * sqrt(frequency) => k = base_att / sqrt(base_freq)
            # Nouvelle att = k * sqrt(new_freq) = base_att * sqrt(new_freq / base_freq)
            import math
            try:
                ratio = frequency / self.base_frequency
                if ratio > 0:
                    return self.base_attenuation * math.sqrt(ratio)
                else:
                    return self.base_attenuation
            except (ZeroDivisionError, ValueError):
                # En cas d'erreur mathématique, retourner la valeur de base
                return self.base_attenuation

    def __repr__(self):
        freq_ghz = self.base_frequency / 1e9
        return (f"MaterialProperties(name='{self.name}', "
                f"frequency={freq_ghz:.1f}GHz, "
                f"attenuation={self.base_attenuation}dB/m)")

    def __str__(self):
        freq_ghz = self.base_frequency / 1e9
        return f"MaterialProperties: {self.name}, {freq_ghz:.1f}GHz, {self.base_attenuation}dB/m"

# --- Exemples de matériaux prédéfinis ---
# Ces instances pourraient être gérées par une factory ou une base de données.

CONCRETE = MaterialProperties("Concrete", 2.4e9, 5.0)
WOOD = MaterialProperties("Wood", 2.4e9, 0.5)
GLASS = MaterialProperties("Glass", 2.4e9, 0.2)
STEEL = MaterialProperties("Steel", 2.4e9, 20.0) # Très haute atténuation

MATERIAL_DATABASE = {
    "Concrete": CONCRETE,
    "Wood": WOOD,
    "Glass": GLASS,
    "Steel": STEEL
}

def get_material_by_name(name: str) -> MaterialProperties:
    """
    Récupère un matériau prédéfini par son nom.

    Args:
        name (str): Nom du matériau.

    Returns:
        MaterialProperties: L'objet MaterialProperties correspondant, ou un matériau générique.
    """
    return MATERIAL_DATABASE.get(name, MaterialProperties(name))
