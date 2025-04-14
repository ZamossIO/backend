from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, Float
import jwt
from datetime import datetime, timedelta
from typing import Union
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel



# Создаем подключение к базе данных SQLite с помощью SQLAlchemy
engine = create_engine('sqlite:///pi.db', echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LoginForm(BaseModel):
    Email: str
    Password: str

#####

class User(Base):
    __tablename__ = 'Users'

    User_ID = Column(Integer, primary_key=True, index=True)
    Email = Column(String, unique=True)
    Name = Column(String)
    Password = Column(String)
    Birthday = Column(String)
    City = Column(String)
    Edu = Column(String)
    Course = Column(String)
    Group = Column(String)
    Phone = Column(String)
    Tg = Column(String)
    Discord = Column(String)
    VK = Column(String)

class Special(Base):
    __tablename__ = 'Special'

    ID_Special = Column(Integer, primary_key=True)
    Name = Column(String)


class OTF(Base):
    __tablename__ = 'OTF'

    ID_OTF = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    Category = Column(String, nullable=False)
    ID_Special = Column(Integer, ForeignKey('Special.ID_Special'))

    # Определяем отношение к таблице "Special"
    special = relationship("Special", back_populates="otfs")


# Определяем отношение от таблицы "Special" к таблице "OTF"
Special.otfs = relationship("OTF", order_by=OTF.ID_OTF, back_populates="special")


class TF(Base):
    __tablename__ = 'TF'

    ID_TF = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    ID_OTF = Column(Integer, ForeignKey('OTF.ID_OTF'))

    # Определяем отношение к таблице "OTF"
    otf = relationship("OTF", back_populates="tfs")


# Определяем отношение от таблицы "OTF" к таблице "TF"
OTF.tfs = relationship("TF", order_by=TF.ID_TF, back_populates="otf")


class TD(Base):
    __tablename__ = 'TD'

    ID_TD = Column(Integer, primary_key=True)
    Name = Column(String, nullable=False)
    ID_TF = Column(Integer, ForeignKey('TF.ID_TF'))

    # Определяем отношение к таблице "TF"
    tf = relationship("TF", back_populates="tds")


# Определяем отношение от таблицы "TF" к таблице "TD"
TF.tds = relationship("TD", order_by=TD.ID_TD, back_populates="tf")

class History(Base):
    __tablename__ = 'History'

    ID_Pass = Column(Integer, primary_key=True)
    User_ID = Column(Integer, ForeignKey('Users.User_ID'))
    DATE = Column(String, nullable=False)
    TIME = Column(String, nullable=False)

class Pass(Base):
    __tablename__ = 'Pass'

    Number = Column(Integer, primary_key=True)
    ID_Pass = Column(Integer, ForeignKey('History.ID_Pass'))
    Special = Column(Integer, ForeignKey('Special.ID_Special'))
    OTF = Column(Integer, ForeignKey('OTF.ID_OTF'))
    TF = Column(Integer, ForeignKey('TF.ID_TF'))
    TD = Column(Integer, ForeignKey('TD.ID_TD'))
    Score = Column(Integer, nullable=False)

class All_Pass(Base):
    __tablename__ = 'All_Pass'

    Number = Column(Integer ,primary_key=True)
    TD = Column(Integer, nullable=False)
    TF = Column(Integer, nullable=False)
    OTF = Column(Integer, nullable=False)
    Special = Column(Integer, nullable=False)
    Kol_vo = Column(Integer, nullable=False)
    SUMM = Column(Integer, nullable=False)
    Medium = Column(Float, nullable=False)

#########################################################################
class NewUser(BaseModel):
    Email: str
    Name: str
    Password: str
    Birthday: str = None
    City: str = None
    Edu: str = None
    Course: str = None
    Group: str = None

class User_Update(BaseModel):
    Token: str
    Name: str = None
    Password: str = None
    Birthday: str = None
    City: str = None
    Edu: str = None
    Course: str = None
    Group: str = None

class LoginData(BaseModel):
    Email: str
    Password: str

class User_info(BaseModel):
    Token: str

class Special_OFT(BaseModel):
    ID_Special: str

class RequestData(BaseModel):
    ID_Special: int
    OTF_Categories: str

class TokenRequest(BaseModel):
    Token: str

class PassResult(BaseModel):
    ID_Pass: int
    Special: int
    OTF: int
    TF: int
    TD: int
    Score: int

class PassInfo(BaseModel):
    ID_Pass: int

class PassResponse(BaseModel):
    ID_Pass: int
    Special: int
    OTF: int
    TF: int
    TD: int
    Score: int