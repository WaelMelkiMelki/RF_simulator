# 📡 RF Simulator 3D - Simulateur de Propagation Radio Fréquence

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![PyVista](https://img.shields.io/badge/PyVista-0.40+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

*Un simulateur RF 3D avancé avec architecture modulaire NETDATA*

[🚀 Installation](#installation) • [📖 Utilisation](#utilisation) • [🏗️ Architecture](#architecture) • [🔧 Fonctionnalités](#fonctionnalités)

</div>

---

## 🎯 Présentation

RF Simulator 3D est une application de simulation de propagation radio fréquence développée avec une architecture **NETDATA** (4 couches) robuste. Elle permet de modéliser et analyser la propagation d'ondes RF dans des environnements 3D complexes avec une interface utilisateur intuitive et des visualisations en temps réel.

## ✨ Fonctionnalités principales

### 🌐 Simulation RF Avancée
- **Modèles de propagation multiples** : Espace libre, modèle conscient des matériaux, ray tracing
- **Support multi-antennes** : WiFi (2.4GHz), 5G (3.5GHz) avec paramètres configurables
- **Calcul de couverture** : Zones de puissance, cartes de signal, analyse de performance
- **Gestion des matériaux** : Brick, concrete, glass, wood, metal, drywall, plaster

### 🎨 Interface Utilisateur 3D
- **Visualisation interactive** : Navigation 3D fluide avec PyVista/VTK
- **Contrôles en temps réel** : Opacité des objets, densité des points, transparence de scène
- **Explorateur d'objets** : Navigation hiérarchique et assignation de matériaux
- **Affichage des résultats** : Cartes de chaleur, points de mesure colorés, zones d'intérêt

### 🔧 Gestion de Scène
- **Chargement de fichiers** : Support GLTF, OBJ et autres formats 3D
- **Modélisation urbaine** : Bâtiments, rues, environnements complexes
- **Assignation de matériaux** : Interface intuitive pour définir les propriétés RF
- **Sauvegarde/Restauration** : Projets complets avec configurations

## 🏗️ Architecture NETDATA

Le projet suit une architecture en **4 couches distinctes** :

```
📁 RF Simulator 3D
├── 🎨 Presentation Layer          # Interface utilisateur
│   ├── GUI (PyQt6)               # Fenêtres, widgets, dialogs
│   ├── 3D Viewer (PyVista)       # Visualisation 3D interactive
│   └── CLI Interface             # Interface ligne de commande
├── 🚀 Application Layer          # Logique applicative
│   ├── Simulation Orchestrator   # Coordination des simulations
│   ├── Scene Manager            # Gestion des scènes 3D
│   └── Result Processor         # Traitement des résultats
├── 🧠 Domain Layer              # Modèles métier
│   ├── RF Models                # Modèles de propagation
│   ├── Antenna Models           # Types d'antennes
│   └── Material Properties      # Propriétés des matériaux
└── 🔧 Infrastructure Layer      # Services techniques
    ├── File Loaders             # Chargement de fichiers 3D
    ├── Database Access          # Persistance des données
    └── Logging Services         # Journalisation
```

## 🛠️ Technologies utilisées

| Catégorie | Technologies |
|-----------|-------------|
| **Language** | Python 3.8+ |
| **GUI Framework** | PyQt6 |
| **3D Visualization** | PyVista, VTK |
| **Scientific Computing** | NumPy, SciPy |
| **3D Processing** | trimesh, open3d |
| **Configuration** | YAML, JSON |
| **Testing** | pytest |

## 📁 Structure du projet

```
📦 RF Simulator 3D
├── 📁 src/                        # Code source principal
│   ├── 📁 gui/                    # Interface utilisateur (Presentation)
│   │   ├── 📁 widgets/           # Widgets PyQt6 personnalisés
│   │   ├── 📁 dialogs/           # Boîtes de dialogue
│   │   └── 📁 adapters/          # Adaptateurs backend
│   ├── 📁 core/                   # Logique métier (Application + Domain)
│   │   ├── 📁 application/       # Services applicatifs
│   │   ├── 📁 domain/            # Modèles et entités
│   │   └── 📁 infrastructure/    # Services techniques
│   ├── 📁 rf_models/             # Modèles de propagation RF
│   ├── 📁 simulation/            # Moteur de simulation
│   └── 📄 main.py               # Point d'entrée
├── 📁 urban_scene_modeling/       # Scènes et modèles 3D
├── 📁 tests/                     # Tests unitaires
├── 📁 docs/                      # Documentation
├── 📁 config/                    # Fichiers de configuration
├── 📄 requirements.txt           # Dépendances Python
├── 📄 setup.py                  # Script d'installation
└── 📄 README.md                 # Ce fichier
```

## 🚀 Installation

### Prérequis
- Python 3.8 ou supérieur
- Git
- Environnement virtuel recommandé

### Étapes d'installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/WaelMelkiMelki/netdaata.git
   cd netdaata
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Lancer l'application**
   ```bash
   python src/main.py
   ```

## 📖 Utilisation

### Démarrage rapide

1. **Charger une scène 3D**
   - Cliquez sur "Charger Scène" dans la barre d'outils
   - Sélectionnez un fichier `.gltf` ou `.obj`
   - La scène s'affiche automatiquement dans le visualiseur 3D

2. **Ajouter des antennes**
   - Utilisez le panneau "Antennes" pour ajouter des émetteurs
   - Configurez le type (WiFi/5G), position, puissance et fréquence
   - Les antennes apparaissent comme des sphères colorées dans la scène

3. **Assigner des matériaux**
   - Cliquez sur "🔍 Explorer objets" dans la barre d'outils
   - Naviguez dans la hiérarchie des objets 3D
   - Assignez des matériaux (brick, concrete, glass, etc.) à chaque objet

4. **Lancer la simulation**
   - Cliquez sur "Démarrer Simulation"
   - Observez la progression dans la barre de statut
   - Les résultats s'affichent sous forme de points colorés (heatmap)

### Contrôles avancés

- **Opacité des points** : Ajustez la transparence des résultats de simulation
- **Densité des points** : Modifiez la résolution de la grille de calcul
- **Opacité de la scène** : Contrôlez la transparence des objets 3D
- **Réinitialisation** : Effacez complètement la scène et recommencez

## 🎮 Interface utilisateur

### Barre d'outils principale
- 📁 **Charger Scène** : Importer des modèles 3D
- ▶️ **Démarrer Simulation** : Lancer les calculs RF
- 🔄 **Réinitialiser** : Effacer la scène actuelle
- 🔍 **Explorer objets** : Naviguer dans la hiérarchie 3D

### Contrôles de visualisation
- 🎚️ **Opacité des points** : Transparence des résultats (10-100%)
- 📏 **Densité des points** : Résolution de simulation (1-20 points)
- 🌫️ **Opacité scène** : Transparence des objets 3D (10-100%)

### Panneau d'antennes
- Liste des antennes actives
- Sélection multiple supportée
- Paramètres configurables par antenne

## 🔬 Exemples d'utilisation

### Simulation WiFi dans un bâtiment
```python
# Exemple de configuration programmatique
antenna = {
    "type": "wifi",
    "name": "Router_Bureau",
    "position": [10.0, 15.0, 2.5],
    "frequency": "2.4GHz",
    "power_dbm": 20.0,
    "coverage_radius": 50.0,
    "ssid": "Bureau_WiFi"
}
```

### Analyse de couverture 5G
```python
# Configuration antenne 5G
antenna_5g = {
    "type": "5g",
    "name": "Station_5G",
    "position": [0.0, 0.0, 25.0],
    "frequency": "3.5GHz",
    "power_dbm": 30.0,
    "coverage_radius": 100.0
}
```

## 🧪 Tests

Exécuter les tests unitaires :
```bash
python -m pytest tests/ -v
```

## 📚 Documentation

- [Guide d'architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Guide de développement](docs/development.md)
- [Exemples avancés](docs/examples.md)

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👨‍💻 Auteur

**Wael Melki**
- GitHub: [@WaelMelkiMelki](https://github.com/WaelMelkiMelki)

## 🙏 Remerciements

- PyVista community pour l'excellent framework de visualisation 3D
- PyQt6 pour l'interface utilisateur robuste
- La communauté Python scientifique

---

<div align="center">
  <sub>Développé avec ❤️ pour la simulation RF 3D</sub>
</div>
