# Le README.md

# BoardGame

Backend de l'application BoardGame Hub, une plateforme sociale pour organiser des soirées jeux de société. Ce projet expose une API RESTful développée avec Flask.

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
git clone [https://github.com/ton-repo/portfolio-project.git](https://github.com/ton-repo/portfolio-project.git)
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

Workflow Git
main : Code de production stable.

dev : Intégration des nouvelles fonctionnalités.
 
Auteurs
Projet Portfolio - Wassef / Nina / Warren