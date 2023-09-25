# Librairies
import os
import json
import pandas as pd
from os import listdir
from os.path import isfile, join, dirname, abspath



# Répertoire
data_dir = dirname(dirname(abspath(__file__)))+'/data/pred_model/' # ML data 

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

df = pd.read_json(data_dir +"obs_tps_reel_bretagne_db.json")
print(df.sort_values('date').reset_index(drop=True))


