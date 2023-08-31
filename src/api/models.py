from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class Users_db(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key=True, index=True)
    Date = Column(DateTime, default=datetime.now)
    Nom = Column(String)
    Prenom = Column(String)
    Email = Column(String)
    Alias = Column(String)
    MotdePasse = Column(String)

class Token_db(Base):
    __tablename__= 'token'
    
    id = Column(Integer, primary_key=True, index=True)
    Token = Column(String)