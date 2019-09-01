from sqlalchemy import Column, String, Integer, Date

from base import Base

class Podcast(Base):
    __tablename__ = 'podcast'

    id = Column(Integer, primary_key=True)
    url = Column(String)

    @staticmethod
    def config_filename():
        raise NotImplementedError()


    @staticmethod
    def load_config_file():
        raise NotImplementedError()

    @staticmethod
    def update_from_config_file(session):
        existing_podcasts = session.query(Podcast).all()
        print(existing_podcasts)
        found_podcasts = Podcast.load_config_file()
        for p in found_podcasts:
            if p not in existing_podcasts:
                existing_podcasts.append(p)
