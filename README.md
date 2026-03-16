# Portfolio Backend API

Backend API Python pour gérer un portfolio professionnel avec gestion des utilisateurs, projets, compétences et expériences.

## Structure du Projet

### Dossiers

- **app/** - Cœur de l'application
  - **api/v1/** - Endpoints API version 1 (users, projects, skills, experiences)
  - **models/** - Modèles de données (User, Project, Skill, Experience)
  - **services/** - Logique métier et façade pour les services
  - **persistence/** - Gestion de la persistance des données et repository

- **middleware/** - Middlewares (authentification, validation, etc.)
- **config/** - Configuration de l'application
- **utils/** - Utilitaires et fonctions helper
- **database/** - Gestion de la base de données
- **tests/** - Tests unitaires et d'intégration

### Fichiers racine

- **run.py** - Point d'entrée principal de l'application
- **config.py** - Configuration globale (variables d'environnement, paramètres)
- **requirements.txt** - Dépendances Python
- **README.md** - Documentation du projet

## Installation

```bash
pip install -r requirements.txt
```

## Démarrage

```bash
python run.py
```
