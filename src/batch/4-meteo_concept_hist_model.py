# Librairies
import os
import json
import pandas as pd
from os import listdir
from os.path import isfile, join, dirname, abspath

import mysql.connector
import time


# Informations de connexion à la base de données
db_config = {
    "host": os.environ.get("DB_HOST", "db"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "pwd"),
    "database": os.environ.get("DB_NAME", "dbconsopredict"),
    "port": int(os.environ.get("DB_PORT", 3306))
}

def test_database_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to the database")
            
            # Exécuter une requête SELECT
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM USERS")
            result = cursor.fetchall()
            print("SELECT * FROM USERS returned:", result)
            cursor.close()
            connection.close()
        else:
            print("Connection failed")
    except Exception as e:
        print("Error:", str(e))

print("test connexion base de données")
test_database_connection()

print('Démarrage script hist model')

# Répertoire
data_dir = dirname(dirname(abspath(__file__)))+'/data/pred_model/' # ML data 

# Contenu du répertoire des extractions
def fichierBrut(in_data_dir: str):
    files = [f for f in listdir(data_dir) if isfile(join(data_dir, f)) and '-' in f]
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

    with open(data_dir +"model_bretagne_db.json", "w") as outfile:
        json.dump(merged_contents,outfile)

merge_JsonFiles(liste_fic)

df = pd.read_json(data_dir +"model_bretagne_db.json")
print('Fin script hist model : ',df.shape[0],' lignes historisées')
