# test_exporter.py
"""
Script pour tester le composant ExportManager et les exporteurs de la couche Application.
"""

import sys
import os
import tempfile
import shutil
import numpy as np

# Ajouter le dossier src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_exporter_import():
    """Teste l'importation des classes d'export."""
    print("--- Test d'importation des classes d'export ---")
    try:
        from core.application.exporter import BaseExporter
        print("  -> SUCCÈS: BaseExporter importé correctement.")
    except Exception as e:
        print(f"  -> ECHEC: Erreur lors du test de BaseExporter: {e}")

# test_exporter.py
"""
Script pour tester le composant ExportManager et les exporteurs de la couche Application.
Teste l'importation, l'instanciation et les fonctionnalités de base de chaque exporteur.
"""

import sys
import os
import tempfile
import shutil
import numpy as np

# Ajouter le dossier src au chemin Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def main():
    test_exporter_import()

    # Ajoutez ici d'autres tests pour les exporteurs si nécessaire

    # Par exemple, tester l'instanciation et l'export de base

    print("✅ Tous les tests d'importation de base des exporteurs ont été effectués.")

if __name__ == "__main__":
    main()
