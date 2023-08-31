from pydantic import BaseModel, Field


class Profil(BaseModel):
    Nom:str = Field(min_length=1, max_length=100)
    Prenom:str = Field(min_length=1, max_length=100)
    Email:str = Field(min_length=1, max_length=100)
    Alias:str = Field(min_length=1, max_length=100)
    MotdePasse:str = Field(min_length=1, max_length=100)

class AuthDetails(BaseModel):
    Alias: str 
    MotdePasse: str