# 🎲 Base de Données - Board Game Meetup

Guide rapide pour initialiser la base de données MySQL avec Python.

---

## 📦 Installation

### 1. Installer MySQL
```bash
# Ubuntu/Debian
sudo apt install mysql-server

# macOS
brew install mysql
brew services start mysql
```

### 2. Installer les packages Python
```bash
pip install mysql-connector-python python-dotenv
```

---

## ⚙️ Configuration

### Créer le fichier `.env` à la racine du projet
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=votre_mot_de_passe_mysql
```

⚠️ **Important** : Ajoutez `.env` dans votre `.gitignore` !

---

## 🚀 Lancer le script
```bash
python database/init_database.py
```

**Ce que fait le script :**
1. Supprime la base `boardgame_meetup` si elle existe
2. Crée une nouvelle base de données
3. Crée 7 tables (users, events, comments, friendships, posts, etc.)
4. Insère des données de test (3 users, 2 events, etc.)

---

## 📊 Explication du code

### Structure du script
```python
# 1. Connexion à MySQL
create_connection()
# Lit les credentials depuis .env et se connecte à MySQL

# 2. Exécution SQL
execute_sql_script()
# Crée la base et toutes les tables

# 3. Tables créées
users                   # Profils utilisateurs
favorite_games          # Jeux favoris
events                  # Événements de jeu
event_participants      # Qui participe à quoi
event_comments          # Commentaires sur événements
friendships             # Relations d'amitié (pending/accepted)
posts                   # Publications des utilisateurs

# 4. Données de test insérées
3 utilisateurs          # Nina, Wassef, Warren
3 jeux favoris          # Catan, 7 Wonders, Pandemic
2 événements            # Soirées de jeu à Paris
```

### Fonctionnement détaillé

**Connexion :**
```python
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),      # localhost
    'user': os.getenv('DB_USER'),      # root
    'password': os.getenv('DB_PASSWORD') # votre mot de passe
}
```

**Création de la base :**
```python
cursor.execute("DROP DATABASE IF EXISTS boardgame_meetup")
cursor.execute("CREATE DATABASE boardgame_meetup")
cursor.execute("USE boardgame_meetup")
```

**Création des tables :**
- Chaque `cursor.execute(CREATE TABLE...)` crée une table
- Les `FOREIGN KEY` lient les tables entre elles
- Les `INDEX` accélèrent les recherches par ville/date

**Insertion des données :**
```python
cursor.execute("INSERT INTO users VALUES (...)")
connection.commit()  # Sauvegarde les changements
```

---

## ✅ Vérification

Si tout fonctionne, vous verrez :
```
Initialisation de la base de données...
Table 'users' créée
Table 'favorite_games' créée
...
Base de données initialisée avec succès!
Opération réussie!
```

Vérifier dans MySQL :
```bash
mysql -u root -p
USE boardgame_meetup;
SHOW TABLES;
SELECT * FROM users;
```

---

## 🧪 Données de test

| Username | Email | Mot de passe | Ville |
|----------|-------|--------------|-------|
| Nina_Gamer | nina@example.com | password123 | Paris |
| Wassef_Player | wassef@example.com | password123 | Paris |
| Warren_Dice | warren@example.com | password123 | Lyon |

---

## 🛠️ Dépannage

**Erreur : "No module named 'mysql'"**
```bash
pip install mysql-connector-python python-dotenv
```

**Erreur : "Access denied"**
- Vérifiez le mot de passe dans `.env`

**Erreur : "Can't connect to MySQL"**
```bash
sudo service mysql start
```

---

## 📁 Structure du projet
```
Portfolio-Project/
├── .env                      # Configuration (à créer)
├── .gitignore               # Ajouter .env ici
├── database/
│   └── init_database.py     # Script d'initialisation
└── ...
```

---
