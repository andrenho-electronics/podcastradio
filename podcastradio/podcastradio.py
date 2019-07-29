from dataclasses import dataclass
from podcast import Podcast

@dataclass
class PodcastRadio:
    podcasts:      List[Podcast] = field(default_factory=list)

    def update_podcast_list(self):
        pass
