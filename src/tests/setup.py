from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from collections import namedtuple

DatabaseData = namedtuple('DatabaseData', ['session', 'base'])
database_data = None

def session_base(echo=False):
    engine = create_engine('sqlite:///:memory:', echo=True)
    if database_data == None:
        Base = declarative_base()
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        database_data = DatabaseData(Base, session)
    return database_data