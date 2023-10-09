-- Création de la base de données si elle n'existe pas déjà
CREATE DATABASE IF NOT EXISTS dbconsopredict;

-- Utilisation de la base de données
USE dbconsopredict;

-- Création de la table "USERS"
CREATE TABLE IF NOT EXISTS USERS (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    alias VARCHAR(255) NOT NULL,
    motdepasse VARCHAR(255) NOT NULL,
    hashed_mdp VARCHAR(255) NOT NULL
);

-- Création de la table "PREDICTIONS"
CREATE TABLE IF NOT EXISTS PREDICTIONS (
    predict_id INT AUTO_INCREMENT PRIMARY KEY,
    localite VARCHAR(255) NOT NULL,
    date_prediction DATE NOT NULL,
    jour_predit INT NOT NULL,
    id_jour INT NOT NULL,
    conso FLOAT NOT NULL,
    date_model DATE NOT NULL
);

-- Création de la tale "LOGS"
CREATE TABLE IF NOT EXISTS LOGS (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    date_log DATE NOT NULL,
    alias VARCHAR(255) NOT NULL,
    localite VARCHAR(255) NOT NULL,
    date_model DATE NOT NULL,
    start_day INT NOT NULL,
    end_day INT NOT NULL
);

-- Création de la table "ALIAS_TOKEN"
CREATE TABLE IF NOT EXISTS ALIAS_TOKEN (
    alias VARCHAR(255) NOT NULL,
    token VARCHAR(1000) NOT NULL
);

-- Création de la table OBSERVATIONS
CREATE TABLE IF NOT EXISTS OBSERVATIONS (
    obs_id INT AUTO_INCREMENT PRIMARY KEY,
    code_insee_region VARCHAR(255) NOT NULL,
    libelle_region VARCHAR(255) NOT NULL,
    heure VARCHAR(255) NOT NULL,
    date_heure VARCHAR(255) NOT NULL,
    consommation VARCHAR(255) NOT NULL
);

