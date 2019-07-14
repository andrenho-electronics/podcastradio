import configparser
import logging
import os
from typing import List
from dataclasses import *

@dataclass
class Config:
    podcasts:         List[str] = field(default_factory=list)
    keep_episodes:    int = 5
    download_path:    str = '/var/db/podcastradio/download'
    image_path:       str = '/var/db/podcastradio/images'
    download_threads: int = 3

    def read_config_file(self, filename):
        config = configparser.ConfigParser(delimiters=('=',), allow_no_value=True)
        if len(config.read(filename)) == 0:
            logging.warning('File ' + filename + ' not found.')
            return self
        if config.has_section('podcasts'):
            for key in config['podcasts']:
                podcast_name = key
                value = config['podcasts'][key]
                if value:
                    podcast_name += '=' + value
                self.podcasts.append(podcast_name)
        try:
            self.keep_episodes = int(config['config']['keep_episodes'])
        except KeyError:
            pass
        try:
            self.download_path = config['config']['download_path']
            os.makedirs(self.download_path, exist_ok=True)
        except KeyError:
            pass
        try:
            self.image_path = config['config']['image_path']
            os.makedirs(self.image_path, exist_ok=True)
        except KeyError:
            pass
        try:
            self.download_threads = int(config['config']['download_threads'])
        except KeyError:
            pass
        return self

