# RF Simulator 3D

Simulateur RF 3D développé avec une architecture modulaire en 4 couches, utilisant Python, PyVista pour la visualisation 3D et PyQt6 pour l'interface utilisateur.

## Architecture

Le projet suit une architecture **Clean Architecture** en 4 couches :

- **Présentation** : Interface CLI et GUI (PyQt6)
- **Application** : Orchestration et logique métier (SimulationOrchestrator)
- **Domaine** : Modèles RF et entités métier
- **Infrastructure** : Accès aux données et services externes

## Fonctionnalités principales

### Modèles de Propagation RF
- **FreeSpaceModel** : Propagation en espace libre
- **MaterialAwareModel** : Propagation avec prise en compte des matériaux
- **SimpleRayTracingModel** : Ray tracing basique avec géométrie

### Interface Utilisateur
- **MainWindow** : Fenêtre principale avec PyQt6
- **SceneViewer3D** : Visualisation 3D interactive avec PyVista
- **AntennaLibrary** : Bibliothèque d'antennes
- **ProjectExplorer** : Gestion de projets

### Pipeline de Simulation
1. **Validation** des entrées (DataValidator)
2. **Préprocessing** de la scène 
3. **Computation RF** avec parallélisation (ParallelEngine)
4. **Post-processing** des résultats et visualisation

## Technologies utilisées

- **Python** : Langage principal
- **PyQt6** : Interface utilisateur desktop
- **PyVista** : Visualisation 3D et rendu
- **NumPy/SciPy** : Calculs scientifiques
- **Mermaid** : Diagrammes d'architecture

## Structure du projet
- `src/` : Code source principal
- `urban_scene_modeling/` : Scènes et modèles 3D
- `requirements.txt` : Dépendances Python
- `setup.py` : Script d'installation
- `docs/` : Documentation
- `tests/` : Tests unitaires

## Installation
1. Cloner le dépôt :
   ```
   git clone https://github.com/ton-utilisateur/nom-du-repo.git
   ```
2. Installer les dépendances :
   ```
   pip install -r requirements.txt
   ```
3. Lancer l'application :
   ```
   python src/main.py
   ```

## Dépendances principales
- PyVista
- PyQt6
- numpy
- matplotlib

## Utilisation
- Charger une scène 3D via l'interface graphique
- Assigner des matériaux aux objets
- Lancer la simulation RF

## Auteur
Wael

## Licence
Ce projet est sous licence MIT.
