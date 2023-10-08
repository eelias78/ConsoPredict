# ConsoPredict
Projet DataScienTest MLOps sur la prédiction de la consommation énergétique

Ce projet a pour but de mettre en place le MVP d'une application permettant de prédire la consommation énergétique d'un territoire en fonction de ses prévisions météorologiques

Installation : il suffit de copier ce projet et de lancer start_api.sh, aucun pré-requis nécessaire
Les images Docker seront récupérées de Dockerhub
La base de données sera créée et initialisée automatiquement
Attention : il se peut que le tout premier lancement échoue si l'API démarre avant que la base de données soit complètement créée, dans ce cas, arrêter l'application et la relancer

Cette application est composée de 4 services Docker :
- Un service "db" (base de données MySQL)
- Une interface PHPMyAdmin pour administrer la base de données, accessible sur localhost:8080
- Un service "batch" effectuant tous les traitements nécessaires (scripts Python) sur les données et le monitoring de l'application, de façon transparente pour les utilisateurs
- Un service "api" (FastAPI) permettant aux utilisateurs d'obtenir les prédictions de consommation énergétique, accessible sur localhost:8000/docs (swagger de l'API)

Aperçu du contenu du projet :
.github/workflows : Guthub actions de CI
data : données utilisées pour le modèle ML initial et données générées par le service "batch"
model : contient le modèle ML initial, le monitoring générera de nouvelles versions du modèle si nécessaire
notebook : notebook ayant permis de créer le modèle ML initial
src : sources des services db, batch et api

