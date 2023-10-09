# Librairies
import os
import json
import keras
import numpy as np
import pandas as pd
import sklearn
from datetime import datetime
from os.path import dirname, abspath
from tcn import TCN
from tcn import tcn_full_summary
from keras.models import model_from_json

print('Démarrage script 3')

# Création de la date du process
now = datetime.now()
dt_fic = now.strftime("%Y-%m-%d")

# Répertoires 
in_data_dir = dirname(dirname(abspath(__file__)))  + '/data/processed/' # BDD processed data
out_data_dir = dirname(dirname(abspath(__file__)))  + '/data/pred_model/' # BDD modelled data
in_model = dirname(dirname(abspath(__file__)))  + '/model/' # Paramètres modèles

# Chargement de la BDD
bretagne = pd.read_json(in_data_dir +"processed_bretagne_"+ dt_fic+".json", orient = 'columns')
bretagne['date model'] = dt_fic

# Vecteur des variables nécessaires au modèle
bretagne_array= bretagne[['feat_tmean','feat_month','feat_day_of_week']].to_numpy()

# Mise à l'échelle des données du vecteur
from sklearn.preprocessing import RobustScaler
RS = RobustScaler()
bretagne_scaled= RS.fit_transform(bretagne_array)

# Création de la matrice input du modèle
X_data = np.zeros(shape=(len(bretagne_scaled),14,3))

for j in (range(len(bretagne_scaled))): 
    X_data[j,:,:] = bretagne_scaled[j,:]

# Découpage des données par séquence de 14 jours
timesteps, input_dim = 14, 3
output_dim = 8

# Définition des paramètres du modèle
def get_model():
    inputs=keras.layers.Input(shape=(timesteps, input_dim), name="Input")
    layer_tcn=TCN(nb_filters=32,kernel_size=6, nb_stacks=1, return_sequences=True, dilations=[1, 2, 4, 8],name='TCN')
    layer_Dense=keras.layers.Dense(output_dim, name='Dense')
    x=layer_tcn(inputs)
    outputs=layer_Dense(x)
    model = keras.models.Model(inputs = inputs, outputs = outputs, name='Model_Bret')
    return model

model = get_model()

# Chargement du modèle développé sur la Bretagne
loaded_json = open(in_model + 'model.json', 'r').read()
reloaded_model = model_from_json(loaded_json, custom_objects={'TCN': TCN})
tcn_full_summary(model, expand_residual_blocks=False)

# Chargement des poids
reloaded_model.load_weights(in_model + 'weights.h5')

# Prédiction
y_pred=reloaded_model.predict(X_data)

# Création du dataframe en sortie 
df_tmp = pd.concat([bretagne[['localite','date prediction','date model']],pd.DataFrame(y_pred[:,0,0], columns =['conso(MW)'])],axis=1)

df =  pd.DataFrame()
for i in np.unique(df_tmp.localite):
    df = pd.concat([df,df_tmp[df_tmp['localite']==i].reset_index(drop=True)])

# Mise en forme
df['jour predit'] = df.index.rename('jour predit') + 1
df = df.reset_index(names='id jour')
df = df[['localite','date prediction','jour predit','id jour','conso(MW)', 'date model']]

df.to_json(out_data_dir +"model_bretagne_"+ dt_fic +".json", orient="records")

print('Fin script 3 : génération de ', out_data_dir +"model_bretagne_"+ dt_fic +".json") 
