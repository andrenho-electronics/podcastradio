from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import namedtuple

from base import Base

Session = None

def session_base(echo=False):
    global Session
    if Session == None:
        engine = create_engine('sqlite:///:memory:', echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
    return Session