# ConsoPredict
Projet DataScienTest MLOps sur la prédiction de la consommation énergétique

1 - Objectif  
Ce projet a pour but de mettre en place le MVP d'une application permettant de prédire la consommation énergétique d'un territoire en fonction de ses prévisions météorologiques

2 - Installation :  
Il n'y a pas de pré-requis, il faut juste cloner le projet et lancer le script start_api.sh :  
```
    git init
    git clone https://github.com/Zenobiatoon/ConsoPredict
    cd ConsoPredict
    ./start_api.sh
```
Les images Docker seront récupérées de Dockerhub et la base de données sera créée et initialisée automatiquement  
Attention : il se peut que le tout premier lancement échoue (l'API peut démarrer avant que la base de données ne soit complètement créée), dans ce cas, arrêter l'application et la relancer

3 - Lancement de l'application si elle est déjà installée  
Il suffit de lancer le script start_api.sh :  
```
    cd ConsoPredict
    ./start_api.sh
```

4 - Architecture  

Services Docker :
- Un service "db" (base de données MySQL)
- Une interface PHPMyAdmin pour administrer la base de données, accessible sur localhost:8080
- Un service "batch" effectuant tous les traitements nécessaires (scripts Python) sur les données et le monitoring de l'application, de façon transparente pour les utilisateurs
- Un service "api" (FastAPI) permettant aux utilisateurs d'obtenir les prédictions de consommation énergétique, accessible sur localhost:8000/docs (swagger de l'API)  

Volumes :
- Data : monté sur le service batch
- Model : monté sur le service batch  

Intégration continue :
- Github action : à chque git push, build et transfert sur Dockerhub des images api et batch 

5 - Arborescence du projet  
.github/workflows : Github actions de CI  
data : données utilisées pour le modèle ML initial et données générées par le service "batch"  
model : contient le modèle ML initial, le monitoring générera de nouvelles versions du modèle si nécessaire  
notebook : notebook ayant permis de créer le modèle ML initial  
src : sources des services db, batch et api  
test : contient un scipt de tests unitaires (à lancer lorsque l'application tourne)  
