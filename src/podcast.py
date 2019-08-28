from sqlalchemy import Column, String, Integer, Date

from base import Base

class Podcast(Base):
    __tablename__ = 'podcast'

    id = Column(Integer, primary_key=True)
    url = Column(String)