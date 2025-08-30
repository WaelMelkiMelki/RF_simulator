# src/main.py
"""
Point d'entrée principal de l'application RF Simulator 3D.
Configure l'environnement et lance l'interface utilisateur.
"""

import sys
import os
import logging

import pyvista as pv
print("Version PyVista:", pv.__version__)

# Vérification des méthodes Scene3D
from core.domain.scene import Scene3D
scene = Scene3D()
print("Méthodes disponibles:", [m for m in dir(scene) if not m.startswith('_')])
print("propagate_materials_to_cells existe:", hasattr(scene, 'propagate_materials_to_cells'))

# Configuration globale des threads Qt et WebEngine
try:
    from PyQt6.QtCore import QThread
    # QThread.globalSetTerminationEnabled(True)  # Cette ligne n'existe pas dans PyQt6
except Exception as e:
    print(f"[WARNING] Impossible de configurer QThread: {e}")
os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"  # Prévention crashes Qt

# Configuration des variables d'environnement AVANT tout import
os.environ["QT_OPENGL"] = "desktop"  # Force l'utilisation du pilote OpenGL desktop
os.environ["PYVISTA_PLOTTER"] = "qt"  # Force l'utilisation du plotter Qt
os.environ["QT_API"] = "PyQt6"  # Force PyQt6

# Configuration PyVista pour debug
os.environ["PYVISTA_VERBOSE"] = "1"
os.environ["PYVISTA_DEBUG"] = "1"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rf_simulator.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

print("=== DÉMARRAGE RF SIMULATOR 3D ===")
print(f"Python: {sys.version}")
print(f"Plateforme: {sys.platform}")

def check_dependencies():
    """Vérifie que toutes les dépendances sont présentes."""
    dependencies = {
        "VTK": lambda: __import__('vtk'),
        "PyVista": lambda: __import__('pyvista'),
        "PyQt6": lambda: __import__('PyQt6'),
        "qtpy": lambda: __import__('qtpy'),
        "numpy": lambda: __import__('numpy'),
        "matplotlib": lambda: __import__('matplotlib'),
        "fpdf": lambda: __import__('fpdf'),
        "pyvistaqt": lambda: __import__('pyvistaqt')
    }
    
    missing = []
    for name, import_func in dependencies.items():
        try:
            import_func()
            print(f"✅ {name} importé avec succès")
        except ImportError as e:
            print(f"❌ ERREUR {name}: {e}")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Dépendances manquantes: {', '.join(missing)}")
        print("Installez-les avec: pip install " + " ".join(missing).lower())
        return False
    
    return True

def configure_pyvista():
    """Configure PyVista avec les paramètres appropriés."""
    try:
        import pyvista as pv
        
        # Configuration globale PyVista
        pv.global_theme.font.size = 12
        pv.global_theme.show_scalar_bar = True
        pv.global_theme.color = 'white'
        pv.global_theme.background = 'black'
        pv.global_theme.axes.show = True
        pv.global_theme.interactive = True
        
        print("✅ PyVista configuré")
        return True
    except Exception as e:
        print(f"❌ ERREUR configuration PyVista: {e}")
        return False

def test_pyvista_basic():
    """Test basique de PyVista pour vérifier que tout fonctionne."""
    try:
        import pyvista as pv
        import numpy as np
    
        print("🧪 Test PyVista basique...")
    
        # Créer des points de test
        points = np.random.rand(100, 3) * 10
        values = np.random.rand(100)
    
        # Créer un nuage de points
        point_cloud = pv.PolyData(points)
        point_cloud.point_data['test_values'] = values
    
        print(f"✅ Point cloud test créé: {point_cloud.n_points} points")
        return True
    
    except Exception as e:
        print(f"❌ Échec test PyVista: {e}")
        return False

def setup_qt_environment():
    """Configure l'environnement Qt."""
    try:
        # Forcer le backend Matplotlib à utiliser Qt
        import matplotlib
        matplotlib.use('QtAgg')
        print("✅ Backend Matplotlib configuré sur QtAgg")
    except ImportError as e:
        print(f"[DEBUG] Erreur configuration Matplotlib: {e}")
    
    # Vérifier qtpy
    try:
        import qtpy
        print(f"qtpy Version: {qtpy.__version__}")
        print(f"QT_API utilisé: {qtpy.API_NAME}")
        if qtpy.API_NAME != "PyQt6":
            print(f"⚠️ AVERTISSEMENT: qtpy utilise {qtpy.API_NAME} au lieu de PyQt6")
    except ImportError as e:
        print(f"❌ ERREUR qtpy: {e}")
        print("Assurez-vous que qtpy est installé: pip install qtpy")
        return False
    
    return True

def main():
    """Point d'entrée de l'application."""
    try:
        print("🚀 Lancement de l'application...")
        
        # Vérification des dépendances
        if not check_dependencies():
            input("Appuyez sur Entrée pour fermer...")
            sys.exit(1)
        
        # Configuration de PyVista
        if not configure_pyvista():
            input("Appuyez sur Entrée pour fermer...")
            sys.exit(1)
        
        # Test basique de PyVista
        if not test_pyvista_basic():
            input("Appuyez sur Entrée pour fermer...")
            sys.exit(1)
        
        # Configuration de l'environnement Qt
        if not setup_qt_environment():
            input("Appuyez sur Entrée pour fermer...")
            sys.exit(1)
        
        # Créer QApplication avant tout import de widgets
        from PyQt6.QtWidgets import QApplication
        
        # Créer l'application Qt en premier
        app = QApplication(sys.argv)
        app.setApplicationName("RF Simulator 3D")
        app.setApplicationVersion("1.0.0")
        print("✅ QApplication créée")
        
        # Importer MainWindow après QApplication
        from gui.main_window import MainWindow
        print("✅ MainWindow importée")
        
        window = MainWindow()
        print("✅ MainWindow créée")
        
        window.show()
        print("✅ Fenêtre affichée")
        print("=== APPLICATION PRÊTE ===")
        
        # Lancer la boucle d'événements
        sys.exit(app.exec())
    
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Vérifiez que tous les modules sont installés:")
        print("pip install PyQt6 pyvista pyvistaqt qtpy numpy matplotlib fpdf")
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erreur fatale: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour fermer...")
        sys.exit(1)

if __name__ == '__main__':
    main()