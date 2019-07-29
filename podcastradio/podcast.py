import datetime
from dataclasses import dataclass

@dataclass
class Episode:
    url:         str
    title:       str
    date:        datetime.datetime
    length:      float
    size_bytes:  int
    last_status: Status           
    audio:       Blob    = None

@dataclass
class Podcast:
    url:           str
    title:         str
    keep_episodes: int
    last_status:   Status
    image:         Blob          = None
    episodes:      List[Episode] = field(default_factory=list)

@dataclass
class Download:
    url:           str
    podcast_title: str
    episode_title: str
    perc_dload:    float = 0.0
    audio:         Blob  = None

