# Portfolio Backend API

Backend API Python pour gérer un portfolio professionnel avec gestion des utilisateurs, projets, compétences et expériences.

## Structure du Projet

### Dossiers

- **app/** - Cœur de l'application
  - **api/v1/** - Endpoints API version 1 
  - **models/** - Modèles de données
  - **services/** - Logique métier et façade pour les services
  - **persistence/** - Gestion de la persistance des données et repository

- **config/** - Configuration de l'application
- **utils/** - Utilitaires et fonctions helper
- **database/** - Gestion de la base de données
- **tests/** - Tests unitaires et d'intégration

### Fichiers racine

- **run.py** - Point d'entrée principal de l'application
- **config.py** - Configuration globale (variables d'environnement, paramètres)
- **requirements.txt** - Dépendances Python
- **# Board Game Meetup - Application

Application pour mettre en relation les amateurs de jeux de société et organiser des rencontres.

## 📁 Structure du Projet

```
Portfolio-Project/
├── app/                          # Application principale (Python/Flask)
│   ├── __init__.py
│   ├── api/                      # Routes et endpoints API
│   │   ├── __init__.py
│   │   └── v1/                   # Version 1 de l'API
│   ├── models/                   # Modèles de données
│   ├── services/                 # Logique métier
│   │   └── facade.py             # Façade pour les services
│   └── persistence/              # Accès aux données
│       └── repository.py         # Repository pattern
├── backend/                      # Backend Node.js
│   └── src/
│       └── routes/               # Routes API Node.js
│           ├── auth.js           # Authentification
│           ├── users.js          # Profils utilisateurs
│           ├── games.js          # Recherche de jeux
│           ├── events.js         # Gestion des événements
│           ├── friends.js        # Gestion des amis
│           ├── posts.js          # Publications/Actions
│           └── search.js         # Recherche globale
├── config/                       # Configuration de l'application
│   └── __init__.py
├── database/                     # Gestion de la base de données
│   └── __init__.py
├── tests/                        # Tests unitaires
│   └── __init__.py
├── utils/                        # Utilitaires et helpers
│   └── __init__.py
├── config.py                     # Configuration principale
├── run.py                        # Point d'entrée de l'application
└── requirements.txt              # Dépendances Python
```
