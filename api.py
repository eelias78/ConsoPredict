""" IMPORT DES LIBRAIRIES """

#import uvicorn
from fastapi import FastAPI, Query, Depends, Response
from pydantic import BaseModel
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
tags_metadata = [{
        "name": "Prévisions de consommation électrique (MW)",
        "description": "**_en fonction des prévisions météorologiques à horizon 14 jours_** "
        }]

app = FastAPI(title ='API par Label éCO2',
description ='Consommation électrique : prévisions et notation des Territoires',openapi_tags=tags_metadata)

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""" BLOC : LE ENDPOINT """

@app.get('/', tags=['Endpoint'])
async def get_index():
  return{"Bonjour et bienvenue sur cette API"}

""" BLOC : AUTHENTIFICATION  """

security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = {

    "daniel": {
        "username": "daniel",
        "name": "Daniel Datascientest",
        "hashed_password": pwd_context.hash('datascientest'),
    },

    "john" : {
        "username" :  "john",
        "name" : "John Datascientest",
        "hashed_password" : pwd_context.hash('secret'),
    }
}

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    username = credentials.username
    if not(users.get(username)) or not(pwd_context.verify(credentials.password, users[username]['hashed_password'])):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username



""" BLOC : SAISIE DE LA LOCALISATION """

list_station = ['50041','14137', '76116', '29075','22168', '35238', '61001', '56152', '44020']
list_station =Literal[tuple(list_station)]


class parametres:
    def __init__(self, Localisation: list_station=
                 Query(description="Code commune INSEE"), Start: int=
                 Query(description="Jour à partir duquel la prévision est demandée, inclus (0: aujourd'hui, 1: demain, etc.)"),
                 End: int=
                 Query(description="Jour jusqu'auquel la prévision est demandée, inclus (0: aujourd'hui, 1: demain, etc.)")):
        
        self.Localisation = Localisation
        self.Start = Start
        self.End = End

@app.get('/user/requete/', tags=['Prévisions de consommation électrique (MW)'])
def Saisie_des_parametres(params:parametres=Depends(),username: str = Depends(get_current_user)):
  return {"insee":params.Localisation, "datetime":params.Start}


#if __name__ == "__main__":
#    uvicorn.run(app, host = "127.0.0.1", port=8000)