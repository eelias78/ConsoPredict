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
;

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