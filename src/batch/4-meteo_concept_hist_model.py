# Librairies
import os
import json
import pandas as pd
from os import listdir
from os.path import isfile, join, dirname, abspath

import mysql.connector
import time
from datetime import datetime

# Informations de connexion à la base de données
db_config = {
    "host": os.environ.get("DB_HOST", "db"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "pwd"),
    "database": os.environ.get("DB_NAME", "dbconsopredict"),
    "port": int(os.environ.get("DB_PORT", 3306))
}
connection = mysql.connector.connect(**db_config)

def test_database_connection():
    try:
        if connection.is_connected():
            print("Connected to the database")
            
            # Exécuter une requête SELECT
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM PREDICTIONS")
            result = cursor.fetchall()
            print("SELECT COUNT(*) FROM PREDICTIONS returned:", result)
            cursor.close()
        else:
            print("Connection failed")
    except Exception as e:
        print("Error:", str(e))

print("SELECT en base de données avant insertion")
test_database_connection()

print('Démarrage script hist model')

# Répertoire
data_dir = dirname(dirname(abspath(__file__)))+'/data/pred_model/' # ML data 
# Création de la date du process
now = datetime.now()
#dt_fic = now.strftime("%Y-%m-%d")
dt_fic = '2023-08-20'

# Positionnement dans le répertoire des fichiers bruts et agrégation
os.chdir(data_dir)

df = pd.read_json(data_dir +"model_bretagne_"+ dt_fic +".json")

# Nom de la table dans la base de données MySQL
table_name = 'PREDICTIONS'
columns_name = 'localite, date_prediction, jour_predit, id_jour, conso, date_model'

try:
    cursor = connection.cursor()
    for index, row in df.iterrows():
        values = tuple(row)
        query = f"INSERT INTO {table_name} ({columns_name}) VALUES {values}"
        print(query)
        cursor.execute(query)
    connection.commit()
except Exception as e:
    connection.rollback()
    print(f"Une erreur s'est produite : {str(e)}")
finally:
    cursor.close()

print("SELECT en base de données après insertion")
test_database_connection()

connection.close()

print('Fin script hist model')
