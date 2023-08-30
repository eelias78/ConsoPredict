# Librairies
import os
import json
import pandas as pd
from os import listdir
from os.path import isfile, join, dirname, abspath


# Répertoire
in_data_dir = dirname(dirname(abspath(__file__)))+'/data/processed/' # BDD processed & ML data 
out_data_dir = dirname(dirname(abspath(__file__))) +'/data/model/' # base historique avec toutes les prédictions 

# Contenu du répertoire des extractions
def fichierBrut(in_data_dir: str):
    files = [f for f in listdir(in_data_dir) if isfile(join(in_data_dir, f)) and "model" in f]
    print(files)
    return(files)
    
# Positionnement dans le répertoire des fichiers bruts et agrégation
os.chdir(in_data_dir)

# Listing des extractions existantes + récupération du contenu de toutes les extractions dans un fichier unique
liste_fic = fichierBrut(in_data_dir)

def merge_JsonFiles(liste_fic):
    merged_contents = []

    for fichier in liste_fic : 
        with open(fichier,'r') as infile:
            merged_contents.extend(json.load(infile))

    with open(out_data_dir +"model_bretagne_db.json", "w") as outfile:
        json.dump(merged_contents,outfile)

merge_JsonFiles(liste_fic)


df = pd.read_json(out_data_dir +"model_bretagne_db.json")

print(df)