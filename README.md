# RF Simulator 3D

Ce projet est une application de simulation RF (Radio Fréquence) en 3D, permettant de modéliser des scènes urbaines, d'attribuer des matériaux aux objets et de réaliser des analyses de propagation.

## Fonctionnalités principales
- Chargement de scènes 3D (GLTF, OBJ, etc.)
- Gestion des matériaux et propriétés RF
- Visualisation et interaction 3D avec PyVista et PyQt
- Attribution et propagation des matériaux sur les cellules du mesh
- Ray tracing et calculs d'intersection

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
