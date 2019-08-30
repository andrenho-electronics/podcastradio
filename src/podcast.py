from sqlalchemy import Column, String, Integer, Date

from base import Base

class Podcast(Base):
    __tablename__ = 'podcast'

    id = Column(Integer, primary_key=True)
    url = Column(String)

    @staticmethod
    def load_config_file(filename):
        raise NotImplementedError()

    @staticmethod
    def update_from_config_file(session):
        raise NotImplementedError()