# Dossier : raw_dev_model
# Fichier : Data_Bretagne.csv
    - Contenu : Données météorologiques journalières observées toutes les 6h 
    - Source de données : Météonet 
    - Lien : https://meteonet.umr-cnrm.fr/
    - Période d'observation disponible : Janvier 2016 - Décembre 2018 (3 années) | 15GB
    - Région disponible : Nord Ouest et Sud Est
    - Région retenue : Bretagne
    

# Dossier : raw_dev_model
# Fichier : Conso_Bretagne.csv
    - Contenu :  données éCO2mix régionales consolidées et définitives de la consommation électrique au pas demi-heure
    - Source de données : Odré 
    - Lien : https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def/information/?disjunctive.libelle_region&disjunctive.nature
    - Période d'observation disponible : Janvier 2013 - Mai 2022
    - Période d'observation retenue : Janvier 2016 - Décembre 2018 (3 années)
    - Région disponible : 12 régions
    - Région retenue : Bretagne


# Dossier : raw_for_prediction
# Fichier : meteo_concept_dt_val_xxxx
    - Contenu : Extraction brute de l'api Météo concept (données météorologiques yc la température)
    - Période d'observation disponible : 14 jours (jour d'extraction inclus) 
    - Source : https://api.meteo-concept.com/documentation_openapi


# Dossier : processed
# Fichier : processed_bretagne_yyyy-mm-dd
    - Contenu : Données pré-traitées provenant du fichier meteo_concept_dt_val_yyyy-mm-dd
    - Date d'observation : xxxx

# Dossier : pred_model
# Fichier : model_bretagne_yyyy-mm-dd
    - Contenu : Données modéliséés (variable cible : conso(MW))
    - Source : processed_bretagne_yyyy-mm-dd
    - Date d'observation : yyyy-mm-dd
# Fichier : model_bretagne_db
    - Contenu : Données modéliséés historisées (variable cible : conso(MW))
    - Source : tous processed_bretagne_yyyy-mm-dd
    - Date d'observation : Historique des données modélisées ET disponibles dans le répertoire "processed"