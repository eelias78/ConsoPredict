# Librairies
import json
import subprocess
import pandas as pd
from os.path import dirname, abspath



# Répertoire
data_dir = dirname(dirname(abspath(__file__))) + "/data/pred_model/"

model_perf = pd.read_json(data_dir+'model_metrics_bretagne_db.json')
model_perf.sort_values(by='date_model',inplace=True)

model_drift = pd.read_json(data_dir+'model_drift_bretagne_db.json')
model_drift.sort_values(by='date_model',inplace=True)
model_drift = model_drift.tail(4)

print(model_perf.iloc[:,2:])
print(model_drift.iloc[:,2:])

# Conditions pour ré-entrainement
if model_perf['pct_dist_euclid'].mean().round() > 40 or model_drift['pct_dist_euclid'].mean() > 30:
    subprocess.call(['python3', '9-model_retraining.py'])
else :
    print('Pas de ré-entraînement')