import importlib
import sys
from PyQt6.QtWidgets import QMessageBox

class DependencyChecker:
    REQUIRED_PACKAGES = [
        ('pyvista', 'pyvista'),
        ('fpdf', 'fpdf'),
        ('PIL', 'Pillow'),
        ('matplotlib', 'matplotlib')
    ]

    @classmethod
    def check_dependencies(cls, parent=None):
        missing = []
        for import_name, package_name in cls.REQUIRED_PACKAGES:
            try:
                importlib.import_module(import_name)
            except ImportError:
                missing.append(package_name)
        if missing:
            msg = "Les packages suivants sont requis pour l'export:\n"
            msg += "\n".join(f"- {pkg}" for pkg in missing)
            msg += "\n\nSouhaitez-vous les installer maintenant?"
            reply = QMessageBox.question(
                parent,
                "Dépendances manquantes",
                msg,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                cls.install_dependencies(missing)
                return True
            return False
        return True

    @classmethod
    def install_dependencies(cls, packages):
        import subprocess
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
            QMessageBox.information(None, "Installation réussie", "Les dépendances ont été installées avec succès!")
            return True
        except Exception as e:
            QMessageBox.critical(None, "Erreur d'installation", f"Échec de l'installation:\n{str(e)}")
            return False
