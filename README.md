# Module Base de Données - BoardGame Meetup

Ce module contient les scripts d'initialisation et l'architecture de la base de données MySQL pour le MVP **BoardGame Meetup**.

## Architecture des Données

La base de données relationnelle est conçue pour gérer les interactions entre joueurs, événements et jeux.

### Schéma
* **Users** : Profils joueurs, rôles (admin/user), géolocalisation.
* **Games** : Bibliothèque de jeux de société.
* **Events** : Sessions de jeu organisées.
* **Participations** : Gestion des inscriptions et liste d'attente.
* **Social** : Système d'amis (`friendships`) avec contraintes d'unicité et commentaires.

---

## Installation et Configuration

### Prérequis
* Python 3.8+
* MySQL Server 8.0+
* Pip (Gestionnaire de paquets Python)

### 1. Configuration de l'environnement
Installez les dépendances nécessaires :
```bash
pip install mysql-connector-python

### 2. initialiser et tester la base de donnée

 # Lancer mysql

sudomysql

# Exécutez ces commandes dans votre terminal MySQL

CREATE USER IF NOT EXISTS 'dev_user'@'localhost' IDENTIFIED BY '';

GRANT ALL PRIVILEGES ON *.* TO 'dev_user'@'localhost';

FLUSH PRIVILEGES;

EXIT;
# Lancez le script d'automatisation pour créer les tables et insérer les données de test (seed) 

python3 database/init_database.py

### vérification des données

# Lister les utilisateurs créés

mysql -u dev_user -D boardgame_meetup -e "SELECT user_id, username, email FROM users;"