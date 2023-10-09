# Librairies
import json
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from pandas import json_normalize
from scipy.spatial import distance
from os.path import dirname, abspath
from datetime import timedelta
from sklearn.metrics import mean_absolute_error as MAE

print('Démarrage script 7')

# Répertoire
data_dir_pred = dirname(dirname(abspath(__file__))) + "/data/pred_model/"
data_dir_4_dev = dirname(dirname(abspath(__file__))) + "/data/raw_4_dev_model/"

# Base données en temps réel
df_obs = pd.read_json(data_dir_pred + 'obs_tps_reel_bretagne_db.json')
df_obs['date_model']= pd.to_datetime(df_obs['date_model']).dt.date

# Paramètres
region='Bretagne'
now = datetime.now()
jour_proc = now.strftime("%Y-%m-%d")
jour_deb = (now - timedelta(days=40)).strftime("%Y-%m-%d")

# Base de modélisation
df_mod = pd.read_csv(data_dir_4_dev + 'Conso_Bretagne.csv', sep = ';', index_col= 0)
df_mod = df_mod.rename(columns = {"consommation": "conso_dev_mod(MW)"})
df_mod.index = pd.to_datetime(df_mod.index)
df_mod['jour'] = df_mod.index.day
df_mod['jour_sem'] = df_mod.index.weekday
df_mod['mois'] = df_mod.index.month
df_mod['annee'] = df_mod.index.year
df_mod = df_mod[['jour_sem','mois', 'annee', 'conso_dev_mod(MW)']]
moy_co2_mod = df_mod.groupby(['mois','jour_sem'])['conso_dev_mod(MW)'].agg('mean').round()
print(moy_co2_mod)

# Base des oservations consolidées
df_obs = df_obs.loc[df_obs['date_model'] == jour_deb]
df_obs['jour'] = df_obs['date'].dt.day
df_obs['jour_sem'] = df_obs['date'].dt.weekday
df_obs['mois'] = df_obs['date'].dt.month
df_obs['annee'] = df_obs['date'].dt.year
df_obs['statut_donnees'] = 'consolidées'
print(df_obs)

# Union des deux bases
df = df_obs.merge(moy_co2_mod, on = ['jour_sem','mois'], how = 'left')
ecart_type_tps_reel= np.std(df['conso_tps_reel(MW)'])
ecart_type_per_mod = np.std(df['conso_dev_mod(MW)'])
moyenne_tps_reel= np.mean(df['conso_tps_reel(MW)'])
moyenne_per_mod = np.mean(df['conso_dev_mod(MW)'])

# Calcul des metrics
norm=np.linalg.norm(df['conso_tps_reel(MW)'].to_numpy())
conso_tps_reel = tuple(df['conso_tps_reel(MW)'])
conso_dev_mod = tuple(df['conso_dev_mod(MW)'])
distance_euclidean= distance.euclidean(conso_tps_reel, conso_dev_mod)
df_metrics = df[['libelle_region','code_insee_region', 'date_model', 'statut_donnees']].head(1)
df_metrics['date_model'] = df_metrics['date_model'].astype(str)
df_metrics['date_perf_calcul'] = jour_proc
df_metrics['pct_dist_euclid']=100*(distance_euclidean/norm)
df_metrics['ecart-type_tps_reel'] = ecart_type_tps_reel
df_metrics['ecart-type_per_mod'] = ecart_type_per_mod
df_metrics['moyenne_tps_reel'] = moyenne_tps_reel
df_metrics['moyenne_per_mod'] = moyenne_per_mod
resultat_metrics=df_metrics.to_dict('records')
print(df_metrics)


def metrics_json(new_data, file_name= data_dir_pred +'model_drift_bretagne_db.json'):
    with open(file_name, 'r') as infile:
        file_data = json.load(infile)

    merged_contents = []
    dico_date_model = []
    dico_date_perf_cal = []
    
    merged_contents.append(new_data[0])    
    for i,j in enumerate(file_data):
        dico_date_model.append(file_data[i]['date_model'])

    if (new_data[0]['date_model'] not in dico_date_model) :
        merged_contents.extend(file_data)
        with open(file_name, 'w') as infile:
            json.dump(merged_contents, infile, indent=2)
    else:
            print('La perf du modèle au %s a déjà été calculée' %jour_proc)
    with pd.option_context('display.max_columns', 10):
        print(pd.read_json(file_name))

metrics_json(new_data=resultat_metrics)

print('Fin script 7 : mise à jour de ', data_dir_pred +'model_drift_bretagne_db.json')