# BoardGame Hub 

Plateforme sociale pour les passionnés de jeux de société : créez des soirées jeux, gérez vos amis, partagez vos jeux favoris et discutez avec votre communauté.

---

## Table des matières

1. [Présentation du projet](#présentation-du-projet)
2. [Stack technique](#stack-technique)
3. [Architecture du projet](#architecture-du-projet)
4. [Prérequis](#prérequis)
5. [Installation et configuration](#installation-et-configuration)
6. [Lancement du projet](#lancement-du-projet)
7. [Base de données](#base-de-données)
8. [API REST — Endpoints](#api-rest--endpoints)
9. [Variables d'environnement](#variables-denvironnement)
10. [Services externes](#services-externes)
11. [Tests](#tests)
12. [Structure des fichiers](#structure-des-fichiers)

---

## Présentation du projet

**BoardGame Hub** est un réseau social permettant à des persones de :

- S'inscrire et gérer leur profil (photo de profil, ville, bio)
- Consulter un catalogue de jeux de société
- Créer et rejoindre des soirées jeux
- Gérer une liste d'amis (demande / acceptation / refus / suppression)
- Publier des posts sur un fil d'actualité
- Rechercher des utilisateurs, jeux et événements
- Marquer des jeux en favoris

---

## Stack technique

### Backend

| Outil | Version | Rôle |
|---|---|---|
| Python | 3.10+ | Langage principal |
| Flask | 3.0.0 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM pour MySQL |
| Flask-JWT-Extended | 4.6.0 | Authentification JWT |
| Flask-CORS | 4.0.0 | Gestion CORS |
| Flask-Limiter | 3.5.1 | Rate limiting |
| Flasgger | 0.9.7.1 | Documentation Swagger |
| Cloudinary | 1.40.0 | Stockage des images |
| mysql-connector-python | 8.2.0 | Driver MySQL |
| python-dotenv | 1.0.0 | Chargement des variables .env |
| requests | 2.31.0 | Appels HTTP (OpenCage) |

### Frontend

| Outil | Version | Rôle |
|---|---|---|
| React | 18+ | Interface utilisateur |
| Vite | 7.x | Bundler et serveur de développement |
| React Router | 6+ | Navigation côté client |
| react-icons | - | Icônes |

### Base de données

- **MySQL** — Schéma relationnel avec 8 tables

### Services externes

- **OpenCage Geocoding API** — Géocodage des adresses lors de la création d'événements
- **Cloudinary** — Stockage et CDN des images (photos de profil, couvertures d'événements)

---

## Architecture du projet

```
Portfolio-Project/
├── run.py                  # Point d'entrée Flask
├── config.py               # Configuration centralisée (env vars)
├── requirements.txt        # Dépendances Python
├── .env                    # Variables d'environnement (non versionné)
├── app/
│   ├── __init__.py         # Factory Flask (create_app), extensions
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py # Blueprint api_v1
│   │       ├── auth.py     # Inscription / Connexion
│   │       ├── users.py    # Profil utilisateur, favoris
│   │       ├── games.py    # Catalogue de jeux
│   │       ├── events.py   # Soirées jeux (CRUD + participation)
│   │       ├── friends.py  # Gestion des amis
│   │       ├── posts.py    # Fil d'actualité
│   │       └── search.py   # Recherche globale
│   ├── models/
│   │   ├── user.py         # Modèle User
│   │   ├── profile.py      # Modèle Profile (1-to-1 avec User)
│   │   ├── game.py         # Modèle Game
│   │   ├── event.py        # Modèle Event
│   │   ├── event_participant.py
│   │   ├── event_comment.py
│   │   ├── favorite_game.py
│   │   ├── friend.py       # Modèle Friend (demandes + liens)
│   │   └── post.py         # Modèle Post
│   ├── persistence/
│   │   └── repository.py   # Couche d'accès aux données (Repository pattern)
│   └── services/
│       └── facade.py       # Logique métier (Facade pattern)
├── database/
│   ├── schema.sql          # Script SQL de création de la BDD
│   └── seed.py             # Script de données initiales (admins + jeux)
├── frontend/
│   ├── src/
│   │   ├── api/            # Appels HTTP vers le backend
│   │   ├── components/     # Composants React réutilisables
│   │   ├── context/        # AuthContext (token JWT)
│   │   ├── pages/          # Pages principales
│   │   ├── routes/         # ProtectedRoute
│   │   └── styles/         # CSS par page
│   └── public/
│       └── images/games/   # Images des jeux de société
└── tests/                  # Tests unitaires et d'intégration pytest
```

### Patterns utilisés

- **Factory Pattern** : `create_app()` dans `app/__init__.py`
- **Facade Pattern** : `app/services/facade.py` — couche unique d'accès à toute la logique métier
- **Repository Pattern** : `app/persistence/repository.py` — abstraction de l'accès à la base de données
- **Blueprint** : l'API est organisée en Blueprint Flask (`api_v1`)

---

## Prérequis

- Python 3.10+
- Node.js 18+
- MySQL 8.0+
- Un compte Cloudinary
- Une clé OpenCage Geocoding API

---

## Installation et configuration

### 1. Cloner le repo

```bash
git clone <https://github.com/WassefRPZ/Portfolio-Project.git>
cd Portfolio-Project
```

### 2. Backend — Environnement virtuel et dépendances

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Créer le fichier `.env`

À la racine du projet, créer un fichier `.env` :

```env
SECRET_KEY=une_cle_secrete_tres_longue
JWT_SECRET_KEY=une_autre_cle_jwt_secrete

DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=ton_mot_de_passe_mysql
DB_NAME=boardgame_hub

CORS_ORIGINS=http://localhost:5173

OPENCAGE_API_KEY=ta_cle_opencage
CLOUDINARY_CLOUD_NAME=ton_cloud_name
CLOUDINARY_API_KEY=ta_cle_cloudinary
CLOUDINARY_API_SECRET=ton_secret_cloudinary

SEED_ADMIN_PASSWORD=MotDePasse_Admin1!
FLASK_DEBUG=false
FLASK_PORT=5000
FLASK_HOST=127.0.0.1
```

### 4. Créer la base de données MySQL

```bash
mysql -u root -p < database/schema.sql
```

### 5. Insérer les données initiales

```bash
cd database
python3 seed.py
cd ..
```

### 6. Frontend — Dépendances

```bash
cd frontend
npm install
cd ..
```

---

## Lancement du projet

**Terminal 1 — Backend Flask :**

```bash
source .venv/bin/activate
python3 run.py
```

Le backend sera disponible sur : http://127.0.0.1:5000  
Documentation Swagger : http://127.0.0.1:5000/apidocs/

**Terminal 2 — Frontend React :**

```bash
cd frontend
npm run dev
```

Le frontend sera disponible sur : http://localhost:5173

---

## Base de données

### Schéma relationnel

```
users (id, email, password_hash, role, created_at)
  │
  ├── profiles (id, user_id, username, bio, city, region, profile_image_url)
  │
  ├── events (id, creator_id, game_id, title, description, city, region,
  │           location_text, date_time, max_players, status, cover_url,
  │           latitude, longitude, created_at)
  │     ├── event_participants (id, event_id, user_id, status, joined_at)
  │     └── event_comments (id, event_id, user_id, content, created_at)
  │
  ├── favorite_games (user_id, game_id, added_at)
  │
  ├── friends (id, user_id_1, user_id_2, requester_id, status, created_at)
  │
  └── posts (id, author_id, post_type, content, image_url, created_at)

games (id, name, description, min_players, max_players, play_time_min, image_url)
```

### Tables

| Table | Description |
|---|---|
| `users` | Comptes utilisateurs (email, mot de passe hashé, rôle) |
| `profiles` | Profil public (1-to-1 avec users) |
| `games` | Catalogue de jeux de société |
| `events` | Soirées jeux créées par les utilisateurs |
| `event_participants` | Inscriptions aux soirées (confirmed / pending) |
| `event_comments` | Commentaires sur les soirées |
| `favorite_games` | Jeux favoris par utilisateur |
| `friends` | Demandes d'amis et liens d'amitié (pending / accepted) |
| `posts` | Posts du fil d'actualité (text / image / news) |

---

## API REST — Endpoints

**Base URL :** `http://127.0.0.1:5000/api/v1`  
**Authentification :** Bearer Token JWT dans le header `Authorization`

### Auth

| Méthode | Route | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Inscription | Non |
| POST | `/auth/login` | Connexion | Non |

### Users

| Méthode | Route | Description | Auth |
|---|---|---|---|
| GET | `/users/me` | Mon profil complet | Oui |
| PUT | `/users/me` | Modifier mon profil / photo | Oui |
| GET | `/users/<id>` | Profil public d'un utilisateur | Oui |
| GET | `/users/search?q=&city=` | Rechercher des utilisateurs | Oui |
| GET | `/users/me/favorite-games` | Mes jeux favoris | Oui |
| POST | `/users/me/favorite-games` | Ajouter un jeu favori | Oui |
| DELETE | `/users/me/favorite-games/<game_id>` | Retirer un jeu favori | Oui |

### Games

| Méthode | Route | Description | Auth |
|---|---|---|---|
| GET | `/games?limit=50&offset=0` | Liste de tous les jeux | Oui |
| GET | `/games/search?q=` | Rechercher un jeu par nom | Oui |

### Events

| Méthode | Route | Description | Auth |
|---|---|---|---|
| GET | `/events` | Liste des événements ouverts | Oui |
| POST | `/events` | Créer un événement | Oui |
| GET | `/events/<id>` | Détail d'un événement | Oui |
| PUT | `/events/<id>` | Modifier un événement (créateur) | Oui |
| DELETE | `/events/<id>` | Annuler un événement (créateur) | Oui |
| POST | `/events/<id>/join` | Rejoindre un événement | Oui |
| POST | `/events/<id>/leave` | Quitter un événement | Oui |
| GET | `/events/<id>/comments` | Commentaires d'un événement | Oui |
| POST | `/events/<id>/comments` | Poster un commentaire | Oui |

**Filtres disponibles pour GET /events :**
- `city` — filtrer par ville
- `date` — filtrer par date (format ISO 8601 : `2024-12-25`)
- `lat`, `lng`, `radius` — filtrer par géolocalisation (rayon en km, max 200)
- `limit`, `offset` — pagination

### Friends

| Méthode | Route | Description | Auth |
|---|---|---|---|
| GET | `/friends` | Ma liste d'amis | Oui |
| GET | `/friends/pending` | Demandes reçues en attente | Oui |
| GET | `/friends/sent` | Demandes envoyées | Oui |
| POST | `/friends/request/<receiver_id>` | Envoyer une demande d'ami | Oui |
| POST | `/friends/accept/<requester_id>` | Accepter une demande | Oui |
| POST | `/friends/reject/<requester_id>` | Refuser une demande | Oui |
| DELETE | `/friends/<user_id>` | Supprimer un ami | Oui |

### Posts

| Méthode | Route | Description | Auth |
|---|---|---|---|
| GET | `/posts` | Fil d'actualité | Oui |
| POST | `/posts` | Créer un post | Oui |
| GET | `/posts/<id>` | Détail d'un post | Oui |
| PUT | `/posts/<id>` | Modifier son post | Oui |
| DELETE | `/posts/<id>` | Supprimer son post | Oui |
| GET | `/posts/user/<user_id>` | Posts d'un utilisateur | Oui |

### Search

| Méthode | Route | Description | Auth |
|---|---|---|---|
| GET | `/search?q=` | Recherche globale (users + events + games) | Oui |

---

## Variables d'environnement

| Variable | Obligatoire | Description |
|---|---|---|
| `SECRET_KEY` | Oui | Clé secrète Flask |
| `JWT_SECRET_KEY` | Oui | Clé JWT |
| `DB_HOST` | Non (127.0.0.1) | Hôte MySQL |
| `DB_USER` | Oui | Utilisateur MySQL |
| `DB_PASSWORD` | Non | Mot de passe MySQL |
| `DB_NAME` | Oui | Nom de la base de données |
| `CORS_ORIGINS` | Non (*) | Origines autorisées CORS |
| `OPENCAGE_API_KEY` | Oui* | Clé API OpenCage |
| `CLOUDINARY_CLOUD_NAME` | Non | Cloud Cloudinary |
| `CLOUDINARY_API_KEY` | Non | Clé Cloudinary |
| `CLOUDINARY_API_SECRET` | Non | Secret Cloudinary |
| `SEED_ADMIN_PASSWORD` | Oui (seed) | Mot de passe admins pour le seed |
| `FLASK_DEBUG` | Non (false) | Mode debug Flask |
| `FLASK_PORT` | Non (5000) | Port Flask |
| `FLASK_HOST` | Non (127.0.0.1) | Hôte Flask |

---

## Services externes

### OpenCage Geocoding API

Utilisé lors de la **création d'un événement** pour transformer une adresse textuelle (`location_text`) en coordonnées GPS (`latitude`, `longitude`) et extraire la ville (`city`) et la région (`region`).

- **Endpoint :** `https://api.opencagedata.com/geocode/v1/json`
- **Documentation :** https://opencagedata.com/api

### Cloudinary

Utilisé pour le **stockage des images** uploadées par les utilisateurs :

Les URL retournées sont stockées dans la base de données (`profile_image_url`, `cover_url`).

- **Documentation :** https://cloudinary.com/documentation

---

## Tests

```bash
source .venv/bin/activate
pytest tests/ -v
```

### Fichiers de tests

| Fichier | Couverture |
|---|---|
| `test_auth.py` | Inscription, connexion, validation |
| `test_users.py` | Profil, mise à jour, favoris |
| `test_games.py` | Liste, recherche de jeux |
| `test_events.py` | CRUD événements, participation, commentaires |
| `test_friends.py` | Demandes, acceptation, refus, suppression |
| `test_posts.py` | CRUD posts |
| `test_search.py` | Recherche globale |

## Fonctionnalités

- **Authentification** : Inscription, Connexion (JWT).
- **Événements** : Création, recherche (par ville/date), participation, annulation.
- **Utilisateurs** : Profils, gestion d'amis, jeux favoris.
- **Jeux** : Catalogue de jeux, recherche.
- **Social** : Commentaires sur les événements.

##  Stack Technique

- **Langage** : Python 3.x
- **Framework** : Flask
- **Base de données** : MySQL
- **ORM** : SQLAlchemy
- **Documentation API** : Flasgger (Swagger UI)

## Installation

### 1. Prérequis
- Python 3.8 ou supérieur
- MySQL Server installé et lancé

### 2. Cloner le projet
```bash
git clone [https://github.com/WassefRPZ/Portfolio-Project.git]
cd portfolio-project

Installer les dépendances
Bash
pip install -r Portfolio-Project-app/requirements.txt

# .env
FLASK_APP=run.py
FLASK_ENV=development

# Base de données
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=""
DB_NAME=boardgame_meetup

# Sécurité
SECRET_KEY=une_clé_très_secrete_et_aléatoire
JWT_SECRET_KEY=une_autre_clé_secrete_jwt

 Démarrage
Le script de lancement initialise automatiquement les tables et injecte des données de test (Admin, Jeux) si elles n'existent pas.

Bash
cd Portfolio-Project-app
python3 run.py
L'API sera accessible sur : http://127.0.0.1:5000/api/v1/

La documentation Swagger est disponible sur : http://127.0.0.1:5000/apidocs/

 Tests et Documentation
Les endpoints sont documentés via Swagger. Une fois le serveur lancé, visitez /apidocs pour tester les routes directement depuis le navigateur.
 
Auteurs
Projet Portfolio - Wassef / Nina / Warren