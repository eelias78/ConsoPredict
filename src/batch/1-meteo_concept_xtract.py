# Librairies
import os
import json
import requests
import pandas as pd
from datetime import datetime
from pandas import json_normalize
from os.path import dirname, abspath

# Paramètres de connexion à l'API Météo concept
token='01945a30cc37c7565ae1d77010e0728a1d4863c2cd06f5e72362c9e9a4a078b4'

url = "https://api.meteo-concept.com/api/forecast/daily/?token={token}&insee={sta_ess}"

print('Démarrage script 1')

# Les stations météo essentielles
fic_sta_ess = pd.read_table(dirname(dirname(abspath(__file__))) + '/data/stations.txt', sep="\t",index_col='Code Insee', dtype={"Code Insee":str})   
dico_stat_ess=fic_sta_ess.to_dict()
sta_ess=list(dico_stat_ess['Region'].keys())

# Extraction des données météo prévisionnelles pour les stations essentielles
df = pd.DataFrame()

for i in sta_ess:
    r = requests.get(url, params={"token":token,"insee":i}).json()
    r['city']['code_insee'] = r['city']["insee"]
    r['city']['localite'] = r['city']["name"]
    del r['city']["insee"], r['city']["name"]
    # Récupération du bon code insee (présent dans le dictionnaire 'city')
    data = json_normalize(r, 'forecast').assign(**r['city'])
    df =pd.concat([df, data]) 
    df = df.reset_index(drop=True)

# Mapping code insee/region
df['region']= df['code_insee'].map(dico_stat_ess['Region'])

# Datation du df et affichage
now = datetime.now()
df['date_val']= now.strftime('%Y-%m-%d')

# Datation des fichiers en sortie pour le cron job (chaque 14 jrs)
dt_fic = now.strftime("%Y-%m-%d")

# Stockage des prévisions dans un fichier json
file_path= dirname((dirname(abspath(__file__)))) + "/data/raw_4_prediction/meteo_concept_dt_val_"
df.to_json(file_path + dt_fic + '.json',orient="records")
print('Fin script 1 : ',pd.read_json(file_path + dt_fic + '.json').shape[0],' lignes générées dans ', file_path + dt_fic)