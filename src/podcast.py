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
        existing_podcasts = session.query(Podcast).all()
        found_podcasts = Podcast.load_config_file(CONFIG_FILENAME)
        for p in found_podcasts:
            if p not in existing_podcasts:
                existing_podcasts.add(p)