from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class Users_db(Base):
    __tablename__= 'users'

    id = Column(Integer, primary_key=True, index=True)
    Nom = Column(String)
    Prenom = Column(String)
    Email = Column(String)
    Alias = Column(String)
    Date = Column(DateTime, default=datetime.now)