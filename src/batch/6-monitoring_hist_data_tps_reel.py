# Librairies
import os
import json
import pandas as pd
from os import listdir
from os.path import isfile, join, dirname, abspath

import mysql.connector
import time
from datetime import datetime

print('Démarrage script 6')

# Informations de connexion à la base de données
db_config = {
    "host": os.environ.get("DB_HOST", "db"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "pwd"),
    "database": os.environ.get("DB_NAME", "dbconsopredict"),
    "port": int(os.environ.get("DB_PORT", 3306))
}
# Initialisation de la connexion à la base de données
connection = mysql.connector.connect(**db_config)

# Fonction de test de la connexion à la base de données, renvoyant le nb de lignes dans PREDICTIONS
def test_database_connection():
    try:
        if connection.is_connected():
            print("Connected to the database")
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM OBSERVATIONS")
            result = cursor.fetchall()[0]
            print("Nb lignes dans table OBSERVATIONS :", result)
            cursor.close()
        else:
            print("Connection failed")
    except Exception as e:
        print("Error:", str(e))

# Compte du nb de lignes avant insertion
test_database_connection()

# Répertoire
data_dir = dirname(dirname(abspath(__file__)))+'/data/raw_4_obs_tps_reel/' # ML data 

# Création de la date du process
now = datetime.now()
dt_fic = now.strftime("%Y-%m-%d")

# Positionnement dans le répertoire des fichiers bruts
os.chdir(data_dir)

df = pd.read_json(data_dir +"obs_tps_reel_bretagne_"+ dt_fic +".json")

# Nom de la table dans la base de données MySQL
table_name = 'OBSERVATIONS'
columns_name = 'code_insee_region, libelle_region, heure, date_heure, consommation'

# Insertion des données dans la table PREDICTIONS (ligne par ligne)
try:
    cursor = connection.cursor()
    for index, row in df.iterrows():
        values = tuple(row)
        query = f"INSERT INTO {table_name} ({columns_name}) VALUES {values}"
        cursor.execute(query)
    connection.commit()
except Exception as e:
    connection.rollback()
    print(f"Une erreur s'est produite : {str(e)}")
finally:
    cursor.close()

# Compte du nb de lignes après insertion
test_database_connection()
connection.close()

# Contenu du répertoire des extractions
def fichierBrut(in_data_dir: str):
    files = [f for f in listdir(data_dir) if isfile(join(data_dir, f)) and 'obs_tps_reel_bretagne_20' in f]
    print(files)
    return(files)
    
# Positionnement dans le répertoire des fichiers bruts et agrégation
os.chdir(data_dir)

# Listing des extractions existantes + récupération du contenu de toutes les extractions dans un fichier unique
liste_fic = fichierBrut(data_dir)

def merge_JsonFiles(liste_fic):
    merged_contents = []

    for fichier in liste_fic : 
        with open(fichier,'r') as infile:
            merged_contents.extend(json.load(infile))

    with open(data_dir +"obs_tps_reel_bretagne_db.json", "w") as outfile:
        json.dump(merged_contents,outfile)

merge_JsonFiles(liste_fic)

print('Fin script 6 : mise à jour de ', data_dir +"obs_tps_reel_bretagne_db.json", ' et historisation en base de données')
