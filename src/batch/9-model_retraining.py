# Librairies
import json
import keras
import requests
import numpy as np
import pandas as pd
from datetime import datetime
from pandas import json_normalize
from os.path import dirname, abspath
from datetime import timedelta, date
from tcn import TCN, tcn_full_summary

print('Démarrage script 9')

# Répertoires
data_dir = dirname(dirname(abspath(__file__)))+'/data/raw_4_dev_model/' 
model_dir = dirname(dirname(abspath(__file__)))+'/model/' 

# Création de la date du process
now = datetime.now()

# Paramètres de connexion aux API Odré opendatasoft
region='Bretagne'
jour_proc = now.strftime("%Y-%m-%d")
date_deb = (now - timedelta(days=365))
jour_deb = date(date_deb.year, 1, 1)
jour_fin = (now - timedelta(days=180)).strftime("%Y-%m-%d")

# Requête consommation en temps réel
url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/exports/json?where=libelle_region%3D%27{first}%27and%20%27{second}%27%3C%3Ddate_heure%20and%20date_heure%3C%3D%27{third}%27&limit=-1&timezone=Europe%2FParis&use_labels=false&epsg=4326"
r = requests.get(url.format(first=region, second=jour_deb, third=jour_fin)).json()
tmp1 = json_normalize(r)

tmp1.rename(columns={'date':'datetime'}, inplace = True)
cols=tmp1.columns
tmp1 = tmp1.loc[:,cols[[3,4,6,7,8,9,10,11,12,13,14]]]
tmp1.fillna(0, inplace=True)
tmp1.replace('ND', 0, inplace = True)
tmp1['pompage'] = tmp1['pompage'].astype(float)
tmp1 = tmp1[tmp1['heure'].str.contains('15|45') == False]
df_co2=tmp1.loc[:,cols[[3,6,7,8,9,10,11,12,13,14]]].groupby(cols[3]).agg('sum')
df_co2.index=pd.DatetimeIndex(df_co2.index)
df_co2_dev_new = df_co2.copy()

# Requête consommation ayant servi à la modélisation
df_co2_dev_init = pd.read_csv(data_dir +'Conso_Bretagne.csv',sep=';',index_col=0)
df_co2_dev_init.index=pd.to_datetime(df_co2_dev_init.index)
df_co2_dev_init=df_co2_dev_init[(df_co2_dev_init.index.year>=2016)&(df_co2_dev_init.index.year<=2018)]
df_Y = pd.concat([df_co2_dev_init,df_co2_dev_new], axis=0)
print(df_Y.sort_index)

# Requête température
parametre='t'
region='Bretagne'

url = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/donnees-synop-essentielles-omm/exports/json?select=date%2C{second}&where=nom_reg%3D%27{first}%27%20and%20date%3E%3D%27{third}%27%20and%20date%3C%3D%27{fourth}%27&limit=-1&timezone=Europe%2FParis&use_labels=false&epsg=4326"
r = requests.get(url.format(first=region, second=parametre, third=jour_deb, fourth=jour_fin)).json()
tmp2 = json_normalize(r)
tmp2.dropna(axis=0, inplace=True)
tmp2['datetime'] = pd.to_datetime(tmp2['date'], utc=True).dt.date
df_bret_dev_new=tmp2.loc[:,['datetime','t']].groupby('datetime').agg('mean')
df_bret_dev_new.index = pd.DatetimeIndex(df_bret_dev_new.index)

df_bret_dev_init = pd.read_csv(data_dir +'Data_Bretagne.csv',sep=';',index_col=0, header=[0,1])
df_bret_dev_init.index=pd.to_datetime(df_bret_dev_init.index)
df_bret_dev_init = df_bret_dev_init[('t', 'mean')].to_frame()
df_bret_dev_init.columns = ['t']
df_bret = pd.concat([df_bret_dev_init,df_bret_dev_new], axis=0)
print(df_bret.sort_index)

df= df_Y.join(df_bret)
df["month"]=df.index.month
df["day"]=df.index.day_of_week
y=df.loc[:,cols[[6,7,9,10,11,12,13,14]]]
X=df.drop(cols[[6,7,8,9,10,11,12,13,14]],axis=1)
print(y)
print(X)

# La modélisation
from sklearn.preprocessing import RobustScaler
RS = RobustScaler()
X_scaled= RS.fit_transform(X.to_numpy())

# Nous allons découper les données par séquence de 14 jours
batch_size, timesteps, input_dim = 64, 14, 3
output_timesteps, output_dim = 14, 8

# Nous allons découper les données par paquets de 14 jours avec des recoupements
import random
indexes=random.sample(range(len(X)-14),int(len(X)*2/3))

from sklearn.model_selection import train_test_split
ind_train, ind_test = train_test_split(indexes,train_size=0.7,test_size=0.15,random_state=42)

ind_val=[ind for ind in indexes if (ind not in ind_test) & (ind not in ind_train)]

X_train=np.zeros([len(ind_train),timesteps,input_dim])
y_train=np.zeros([len(ind_train),output_timesteps,output_dim])
for j,k in enumerate(ind_train):
    X_train[j,:,:]=X_scaled[k:k+timesteps,:]
    y_train[j,:,:]=y.iloc[k:k+output_timesteps,:].to_numpy()

X_test=np.zeros([len(ind_test),timesteps,input_dim])
y_test=np.zeros([len(ind_test),output_timesteps,output_dim])
for j,k in enumerate(ind_test):
    X_test[j,:,:]=X_scaled[k:k+timesteps,:]
    y_test[j,:,:]=y.iloc[k:k+output_timesteps,:].to_numpy()

X_val=np.zeros([len(ind_val),timesteps,input_dim])
y_val=np.zeros([len(ind_val),output_timesteps,output_dim])
for j,k in enumerate(ind_val):
    X_val[j,:,:]=X_scaled[k:k+timesteps,:]
    y_val[j,:,:]=y.iloc[k:k+output_timesteps,:].to_numpy()

print(X_train.shape,X_test.shape,X_val.shape)
print(y_train.shape,y_test.shape,y_val.shape)

# Modèle
inputs=keras.layers.Input(shape=(timesteps, input_dim), name="Input")
layer_tcn=TCN(nb_filters=32,kernel_size=6, nb_stacks=1, return_sequences=True, dilations=[1, 2, 4, 8],name='TCN')
layer_Dense=keras.layers.Dense(output_dim, name='Dense')
x=layer_tcn(inputs)
outputs=layer_Dense(x)
model = keras.models.Model(inputs = inputs, outputs = outputs, name='Model_Bret_'+ jour_proc)

model.summary()

model.compile(optimizer="adam", loss="mae",
                  metrics=keras.metrics.MeanAbsoluteError())

nb_epochs=1000
training_history=model.fit(X_train, y_train, batch_size=batch_size,epochs=nb_epochs,validation_split=0.2)

train_acc = training_history.history['mean_absolute_error']
val_acc = training_history.history['val_mean_absolute_error']
train_loss = training_history.history['loss']
val_loss = training_history.history['val_loss']

y_pred=model.predict(X_test)

# Enregistrement du modèle
model.save(model_dir + 'model_bretagne' + jour_proc + '.keras')
model_as_json = model.to_json()
with open(model_dir + 'model_' + jour_proc + '.json', "w") as json_file:
    json_file.write(model_as_json)
# Enregistrement poids 
model.save_weights(model_dir + 'weights_' + jour_proc + '.h5')

print('Fin script 9, génération de ', model_dir + 'model_bretagne' + jour_proc + '.keras')
print('et ', model_dir + 'model_' + jour_proc + '.json')
print('et ', model_dir + 'weights_' + jour_proc + '.h5')

