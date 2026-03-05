-- =============================================================================
--  BoardGame Hub — Structure complète de la base de données MySQL
--  Moteur : MySQL
--  Encodage : utf8mb4 (support des emojis et des caractères spéciaux)
--
--  Intégrations externes :
--    - OpenCage Geocoding API → champs city / region / location_text dans events
--    - Cloudinary            → champs *_url (VARCHAR) dans profiles et events
--
--  Exécution :
--    mysql -u root -p < schema.sql
-- =============================================================================

DROP DATABASE IF EXISTS boardgame_hub;
CREATE DATABASE boardgame_hub
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE boardgame_hub;

-- -----------------------------------------------------------------------------
-- TABLE : users
-- Compte principal de chaque membre de la plateforme.
-- Le champ `role` distingue les utilisateurs ordinaires des administrateurs.
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id            INT AUTO_INCREMENT  PRIMARY KEY,
    email         VARCHAR(150)        NOT NULL UNIQUE,
    password_hash VARCHAR(255)        NOT NULL,
    role          ENUM('user', 'admin') NOT NULL DEFAULT 'user',
    created_at    DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- TABLE : profiles
-- Profil public d'un utilisateur (1-to-1 avec users).
-- profile_image_url : URL fournie par Cloudinary, aucun fichier stocké ici.
-- city / region    : informations saisies manuellement (pas d'appel géo ici).
-- Supprimé automatiquement si l'utilisateur est supprimé (ON DELETE CASCADE).
-- -----------------------------------------------------------------------------
CREATE TABLE profiles (
    id                INT AUTO_INCREMENT  PRIMARY KEY,
    user_id           INT                 NOT NULL UNIQUE,  -- 1 profil par utilisateur
    username          VARCHAR(50)         NOT NULL UNIQUE,
    bio               TEXT,
    city              VARCHAR(100),
    region            VARCHAR(100),
    profile_image_url VARCHAR(255),                         -- URL Cloudinary

    -- Clé étrangère : si l'utilisateur est supprimé, son profil l'est aussi
    CONSTRAINT fk_profiles_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : games
-- Catalogue de jeux de société.
-- image_url     : URL de la pochette du jeu.
-- play_time_min : durée de partie en minutes.
-- -----------------------------------------------------------------------------
CREATE TABLE games (
    id            INT AUTO_INCREMENT  PRIMARY KEY,
    name          VARCHAR(200)        NOT NULL UNIQUE,
    description   TEXT,
    min_players   INT                 NOT NULL,
    max_players   INT                 NOT NULL,
    play_time_min INT                 NOT NULL,          -- durée en minutes
    image_url     VARCHAR(255)                           -- URL image
);

-- -----------------------------------------------------------------------------
-- TABLE : events
-- Soirée jeu organisée par un utilisateur (creator_id).
-- location_text : adresse complète retournée par OpenCage Geocoding API.
-- city / region : composants géographiques extraits de la réponse OpenCage.
-- cover_url     : image de couverture stockée sur Cloudinary (URL uniquement).
-- status        : cycle de vie → open → full → cancelled / completed.
-- Supprimé automatiquement si l'organisateur ou le jeu est supprimé.
-- -----------------------------------------------------------------------------
CREATE TABLE events (
    id            INT AUTO_INCREMENT  PRIMARY KEY,
    creator_id    INT                 NOT NULL,  -- FK vers users
    game_id       INT                 NOT NULL,  -- FK vers games
    title         VARCHAR(200)        NOT NULL,
    description   TEXT,
    date_time     DATETIME            NOT NULL,
    location_text VARCHAR(255)        NOT NULL,  -- texte du lieu (OpenCage)
    city          VARCHAR(100)        NOT NULL,  -- ville (OpenCage)
    region        VARCHAR(100),                  -- région / département (OpenCage)
    max_players   INT                 NOT NULL,
    status        ENUM('open', 'full', 'cancelled', 'completed') NOT NULL DEFAULT 'open',
    cover_url     VARCHAR(255),                  -- URL Cloudinary
    latitude      FLOAT,                         -- latitude (OpenCage Geocoding)
    longitude     FLOAT,                         -- longitude (OpenCage Geocoding)
    created_at    DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Clé étrangère : suppression de l'organisateur → suppression de ses événements
    CONSTRAINT fk_events_creator
        FOREIGN KEY (creator_id) REFERENCES users(id)
        ON DELETE CASCADE,

    -- Clé étrangère : suppression d'un jeu → suppression des événements liés
    CONSTRAINT fk_events_game
        FOREIGN KEY (game_id) REFERENCES games(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : event_participants
-- Table de liaison : qui participe à quel événement.
-- status 'confirmed' : place validée.
-- status 'pending'   : en attente de confirmation de l'organisateur.
-- La contrainte UNIQUE évite qu'un utilisateur s'inscrive deux fois au même événement.
-- -----------------------------------------------------------------------------
CREATE TABLE event_participants (
    id        INT AUTO_INCREMENT  PRIMARY KEY,
    event_id  INT                 NOT NULL,  -- FK vers events
    user_id   INT                 NOT NULL,  -- FK vers users
    status    ENUM('confirmed', 'pending') NOT NULL DEFAULT 'confirmed',
    joined_at DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Un utilisateur ne peut s'inscrire qu'une seule fois par événement
    UNIQUE KEY uq_event_user (event_id, user_id),

    -- Clé étrangère : suppression d'un événement → suppression des inscriptions
    CONSTRAINT fk_ep_event
        FOREIGN KEY (event_id) REFERENCES events(id)
        ON DELETE CASCADE,

    -- Clé étrangère : suppression d'un utilisateur → suppression de ses inscriptions
    CONSTRAINT fk_ep_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : friends
-- Relations sociales entre utilisateurs.
-- Convention : user_id_1 < user_id_2 (à enforcer côté applicatif)
-- pour éviter les doublons (A→B) et (B→A).
-- requester_id : ID réel de l'expéditeur (indépendant du tri).
-- status : pending → accepted. Refus = suppression de la ligne.
-- -----------------------------------------------------------------------------
CREATE TABLE friends (
    id           INT AUTO_INCREMENT  PRIMARY KEY,
    user_id_1    INT                 NOT NULL,  -- premier utilisateur (ID le plus petit)
    user_id_2    INT                 NOT NULL,  -- second utilisateur (ID le plus grand)
    requester_id INT                 NOT NULL,  -- expéditeur réel de la demande
    status       ENUM('pending', 'accepted') NOT NULL DEFAULT 'pending',
    created_at   DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Une seule relation possible entre deux utilisateurs
    UNIQUE KEY uq_friendship (user_id_1, user_id_2),

    -- Clé étrangère : suppression d'un utilisateur → suppression de ses relations
    CONSTRAINT fk_friends_user1
        FOREIGN KEY (user_id_1) REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_friends_user2
        FOREIGN KEY (user_id_2) REFERENCES users(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_friends_requester
        FOREIGN KEY (requester_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : posts
-- Publications du fil d'actualité de la plateforme.
-- post_type : 'text' (texte seul), 'image' (photo + texte optionnel), 'news' (actualité)
-- content et image_url sont optionnels mais au moins l'un doit être fourni (côté appli).
-- image_url : URL Cloudinary si une image est jointe.
-- Supprimé automatiquement si l'auteur est supprimé.
-- -----------------------------------------------------------------------------
CREATE TABLE posts (
    id         INT AUTO_INCREMENT  PRIMARY KEY,
    author_id  INT                 NOT NULL,  -- FK vers users
    post_type  ENUM('text', 'image', 'news') NOT NULL DEFAULT 'text',
    content    TEXT,                          -- texte optionnel
    image_url  VARCHAR(255),                  -- URL Cloudinary (optionnel)
    created_at DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Clé étrangère : suppression d'un utilisateur → suppression de ses posts
    CONSTRAINT fk_posts_author
        FOREIGN KEY (author_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : reviews
-- Avis laissés sur un événement OU sur un autre joueur.
-- reviewer_id      : auteur de l'avis (FK vers users).
-- event_id         : NULL si l'avis porte sur un joueur.
-- reviewed_user_id : NULL si l'avis porte sur un événement.
-- rating           : note de 1 à 5 (enforced par CHECK).
-- Les deux cibles sont mutuellement exclusives côté applicatif.
-- -----------------------------------------------------------------------------
CREATE TABLE reviews (
    id               INT AUTO_INCREMENT  PRIMARY KEY,
    reviewer_id      INT                 NOT NULL,  -- FK vers users (auteur)
    event_id         INT,                           -- FK vers events (NULL si review joueur)
    reviewed_user_id INT,                           -- FK vers users  (NULL si review événement)
    rating           TINYINT             NOT NULL,  -- note de 1 à 5
    comment          TEXT,
    created_at       DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Validation de la plage de la note (MySQL 8.0.16+)
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 5),

    -- Clé étrangère : suppression de l'auteur → suppression de ses avis
    CONSTRAINT fk_reviews_reviewer
        FOREIGN KEY (reviewer_id) REFERENCES users(id)
        ON DELETE CASCADE,

    -- Clé étrangère : suppression d'un événement → suppression des avis associés
    CONSTRAINT fk_reviews_event
        FOREIGN KEY (event_id) REFERENCES events(id)
        ON DELETE CASCADE,

    -- Clé étrangère : suppression d'un utilisateur noté → suppression de ses avis reçus
    CONSTRAINT fk_reviews_reviewed_user
        FOREIGN KEY (reviewed_user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : event_comments
-- Commentaires laissés par les membres sur un événement spécifique.
-- Supprimé automatiquement si l'événement ou l'utilisateur est supprimé.
-- -----------------------------------------------------------------------------
CREATE TABLE event_comments (
    id         INT AUTO_INCREMENT  PRIMARY KEY,
    event_id   INT                 NOT NULL,  -- FK vers events
    user_id    INT                 NOT NULL,  -- FK vers users (auteur)
    content    TEXT                NOT NULL,
    created_at DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Clé étrangère : suppression d'un événement → suppression de ses commentaires
    CONSTRAINT fk_ec_event
        FOREIGN KEY (event_id) REFERENCES events(id)
        ON DELETE CASCADE,

    -- Clé étrangère : suppression d'un utilisateur → suppression de ses commentaires
    CONSTRAINT fk_ec_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : favorite_games
-- Table de liaison entre un utilisateur et ses jeux favoris.
-- Clé primaire composite (user_id, game_id) : un jeu ne peut être favori
-- qu'une seule fois par utilisateur.
-- Supprimé automatiquement si l'utilisateur ou le jeu est supprimé.
-- -----------------------------------------------------------------------------
CREATE TABLE favorite_games (
    user_id  INT      NOT NULL,  -- FK vers users
    game_id  INT      NOT NULL,  -- FK vers games
    added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (user_id, game_id),

    -- Clé étrangère : suppression d'un utilisateur → suppression de ses favoris
    CONSTRAINT fk_fg_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,

    -- Clé étrangère : suppression d'un jeu → suppression des entrées favoris associées
    CONSTRAINT fk_fg_game
        FOREIGN KEY (game_id) REFERENCES games(id)
        ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : post_likes
-- Likes des utilisateurs sur les posts. Clé primaire composite (user_id, post_id).
-- Supprimé automatiquement si l'utilisateur ou le post est supprimé.
-- -----------------------------------------------------------------------------
CREATE TABLE post_likes (
    user_id    INT  NOT NULL,  -- FK vers users
    post_id    INT  NOT NULL,  -- FK vers posts

    PRIMARY KEY (user_id, post_id),

    CONSTRAINT fk_pl_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_pl_post
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

-- -----------------------------------------------------------------------------
-- TABLE : post_comments
-- Commentaires des utilisateurs sur les posts.
-- Supprimé automatiquement si l'utilisateur ou le post est supprimé.
-- -----------------------------------------------------------------------------
CREATE TABLE post_comments (
    id         INT AUTO_INCREMENT  PRIMARY KEY,
    post_id    INT                 NOT NULL,  -- FK vers posts
    user_id    INT                 NOT NULL,  -- FK vers users
    content    TEXT                NOT NULL,
    created_at DATETIME            NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pc_post
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    CONSTRAINT fk_pc_user
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =============================================================================
--  FIN DU SCRIPT — Base de données boardgame_hub créée et prête à l'emploi.
--  Tables : users, profiles, games, events, event_participants, friends,
--           posts, post_likes, post_comments, reviews, event_comments, favorite_games
-- =============================================================================
