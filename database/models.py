from email.policy import default
from sqlalchemy import BIGINT, DateTime, TEXT, Boolean, Column, ForeignKey, Integer, String, UniqueConstraint, false
from pydantic import BaseModel, Field
from database.session import Base
import datetime


class User(Base):
    __tablename__ = "editor_user"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(String(100), unique = True)
    user_name = Column(String(20), unique = True)
    user_pw = Column(String(100))
    email = Column(String(100))
    picture = Column(TEXT)
    locale = Column(String(100))
    key = Column(String(10))
    doi_bag = Column(TEXT)
    create_dt = Column(DateTime, default = datetime.datetime.now())
    last_mod_dt = Column(DateTime, default = datetime.datetime.now())

class Project(Base):
    __tablename__ = "editor_project"
    id = Column(Integer, primary_key = True, index = True)
    project_key = Column(String(10), unique = True)
    project_name = Column(String(20), unique = True)
    user_key = Column(String(10), ForeignKey("editor_user.key"))
    json = Column(TEXT)
    doi = Column(String(500))
    thumbnail = Column(TEXT)
    author_img = Column(TEXT)
    play = Column(TEXT)
    voices = Column(TEXT)
    frame = Column(TEXT)
    
    create_dt = Column(DateTime, default = datetime.datetime.now())
    last_mod_dt = Column(DateTime, default = datetime.datetime.now())
    