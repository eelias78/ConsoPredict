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

print('Démarrage script 5')

# Répertoire
data_in_dir = dirname(dirname(abspath(__file__))) + "/data/pred_model/"
data_out_dir = dirname(dirname(abspath(__file__))) + "/data/raw_4_obs_tps_reel/"

# Création de la date du process
now = datetime.now()
jour_proc = now.strftime("%Y-%m-%d")

# Paramètres de connexion à l'API Odré
region='Bretagne'
jour_fin = now 
jour_deb = (jour_fin - timedelta(days=14)).strftime("%Y-%m-%d")

# Requête
url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/exports/json?where=libelle_region%3D%27{first}%27and%20%27{second}%27%3C%3Ddate_heure%20and%20date_heure%3C%3D%27{third}%27&limit=-1&timezone=Europe%2FParis&use_labels=false&epsg=4326"
r = requests.get(url.format(first=region, second=jour_deb, third=jour_fin)).json()

data = json_normalize(r)
df = data[['code_insee_region','libelle_region', 'heure', 'date_heure','consommation']]
reel = df.copy()
reel = reel[reel['heure'].str.contains(':15|:45') == False]
reel['date'] = pd.to_datetime(df.date_heure).dt.date
reel['conso_tps_reel(MW)']= reel.groupby(['date'])['consommation'].transform(sum)
reel= reel.groupby('date').first().reset_index()
reel['statut_donnees'] = 'temps réel'
reel['date_model'] = jour_deb
reel.drop(['heure','date_heure','consommation'], axis=1, inplace=True)
reel.drop(index=reel.index[-1],axis=0,inplace=True)
reel.to_json(data_out_dir + 'obs_tps_reel_bretagne_'+ jour_proc + '.json', orient="records")

# Récupération des prédictions et calcul de la conso moyenne sur la région
predit=pd.read_json(data_in_dir + 'model_bretagne_db.json')
predit['conso_moy_pred(MW)']= predit.groupby(['date prediction'])['conso(MW)'].transform('mean')
predit= predit.groupby('date prediction').first().reset_index()
predit['date prediction'] = pd.to_datetime(predit['date prediction']).dt.date
predit.drop(['localite','jour predit','id jour','conso(MW)'],axis=1,inplace=True)

# Réunion des prédictions et des observations
comp=reel.merge(predit.loc[:, predit.columns != 'date model'], left_on ='date', right_on = 'date prediction', how = 'left')
comp = comp.rename(columns = {"date prediction": "date_prediction"}) 

# Calcul de l'indicateur MAE
MAE=MAE(y_true=comp['conso_tps_reel(MW)'], y_pred=comp['conso_moy_pred(MW)'])
moyenne_pred= np.mean(comp['conso_moy_pred(MW)'])
ecart_type_pred= np.std(comp['conso_moy_pred(MW)'])
variance_pred= np.var(comp['conso_moy_pred(MW)'])

moyenne_reel= np.mean(comp['conso_tps_reel(MW)'])
ecart_type_reel= np.std(comp['conso_tps_reel(MW)'])
variance_reel= np.var(comp['conso_tps_reel(MW)'])


df_metrics = comp[['libelle_region','code_insee_region', 'date_model', 'statut_donnees']].head(1)
df_metrics['date_perf_calcul'] = jour_proc
df_metrics['moyenne_pred'] = moyenne_pred
df_metrics['moyenne_reel'] = moyenne_reel
df_metrics['ecart-type_pred'] = ecart_type_pred
df_metrics['ecart-type_reel'] = ecart_type_reel
df_metrics['MAE']= MAE

# Calcul de l'indicateur distance euclidienne
norm=np.linalg.norm(comp['conso_tps_reel(MW)'].to_numpy())
conso_reel = tuple(comp['conso_tps_reel(MW)'])
conso_pred = tuple(comp['conso_moy_pred(MW)'])
distance_euclidean= distance.euclidean(conso_reel,conso_pred)
df_metrics['pct_dist_euclid']=100*(distance_euclidean/norm)
resultat_metrics=df_metrics.to_dict('records')
print(df_metrics)


def metrics_json(new_data, file_name= data_in_dir +'model_metrics_bretagne_db.json'):
    with open(file_name, 'r') as infile:
        file_data = json.load(infile)

    merged_contents = []
    dico_date_model = []
    dico_date_perf_cal = []
    
    merged_contents.append(new_data[0])    
    for i,j in enumerate(file_data):
        dico_date_model.append(file_data[i]['date_model'])
        dico_date_perf_cal.append(file_data[i]['date_perf_calcul'])

    if (new_data[0]['date_model'] in dico_date_model) and (new_data[0]['date_perf_calcul'] not in dico_date_perf_cal) or \
    (new_data[0]['date_model'] not in dico_date_model) and (new_data[0]['date_perf_calcul'] not in dico_date_perf_cal):
        merged_contents.extend(file_data)
        with open(file_name, 'w') as infile:
            json.dump(merged_contents, infile, indent=2)
    else:
            print('La perf du modèle au %s a déjà été calculée' %jour_proc)
    with pd.option_context('display.max_columns', 10):
        print(pd.read_json(file_name))

metrics_json(new_data=resultat_metrics)

print('Fin script 5 : génération de', data_dir + 'obs_tps_reel_bretagne_'+ jour_proc + '.json', ' et mise à jour de ', data_dir +"model_metrics_bretagne_db.json")
