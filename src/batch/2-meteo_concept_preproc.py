# Librairies
import os
import json
import pandas as pd
from datetime import datetime
from os.path import dirname, abspath

print('Démarrage script 2')

# Création de la date du process
now = datetime.now()
dt_fic = now.strftime("%Y-%m-%d")

# Répertoire de l'extraction
in_data_dir = dirname(dirname(abspath(__file__)))  # chemin

# Chargement de la BDD météo et filtre sur la région Bretagne
json = pd.read_json(in_data_dir +"/data/raw_4_prediction/meteo_concept_dt_val_"+ dt_fic+".json")
json['date model']= pd.to_datetime(json['date_val'])
bretagne = json.loc[json['region']=='Bretagne'].reset_index(drop=True)


# Calcul de la 1ère variable explicative : "moyenne des températures" en K 
bretagne['feat_tmean'] = bretagne.apply(lambda x: ((x['tmax']+x['tmin'])/2 + 273.15), axis=1)

# Variables nécesssaires
bretagne=bretagne[['region','localite','code_insee','datetime','day','date model','feat_tmean']]

# TRansfo en date et calcul de la 2ème variable explicative :
bretagne['datetime'] = pd.to_datetime(bretagne['datetime'].str[:10])
bretagne['feat_month']= bretagne.datetime.dt.month

# Calcul de la 3ème variable explicative :
bretagne['feat_day_of_week']= bretagne.datetime.dt.day_of_week

# Mise en forme de la date de prédiction
bretagne['date prediction'] = bretagne['datetime'].dt.strftime("%Y-%m-%d")
bretagne.to_json(in_data_dir +"/data/processed/processed_bretagne_"+ dt_fic+".json", orient="records")
print('Fin script 2 : génération de ',in_data_dir +"/data/processed/processed_bretagne_"+ dt_fic+".json")
