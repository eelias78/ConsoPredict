from pydantic import BaseModel, Field


class AuthDetails(BaseModel):
    Identifiant: str
    MotDePasse: str

class Profil(BaseModel):
    Nom:str = Field(min_length=1, max_length=100)
    Prenom:str = Field(min_length=1, max_length=100)
    Email:str = Field(min_length=1, max_length=100)
    Alias:str = Field(min_length=1, max_length=100)