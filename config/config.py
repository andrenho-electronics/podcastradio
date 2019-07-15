import configparser
import logging
import os
from typing import List
from dataclasses import *

@dataclass
class Config:
    podcasts:         List[str] = field(default_factory=list)
    keep_episodes:    int = None
    database_file:    str = None
    download_path:    str = None
    image_path:       str = None
    download_threads: int = None

    def read_config_file(self, filename, create_directories=True):
        config = configparser.ConfigParser(delimiters=('=',), allow_no_value=True)
        if len(config.read(filename)) == 0:
            logging.warning('File ' + filename + ' not found.')
            return self
        self.podcasts = self.__load_podcasts(config)
        self.keep_episodes    = self.__parse_field(config, 'config', 'keep_episodes', 5, int)
        self.download_path    = self.__parse_field(config, 'config', 'download_path', '/var/db/podcastradio/download')
        self.image_path       = self.__parse_field(config, 'config', 'image_path', '/var/db/podcastradio/images')
        self.database_file    = self.__parse_field(config, 'config', 'database_file', '/var/db/podcastradio/podcastradio.db')
        self.download_threads = self.__parse_field(config, 'config', 'download_threads', 3, int)
        if create_directories:
            self.__create_directories()
        return self

    def __load_podcasts(self, config):
        podcasts = []
        if config.has_section('podcasts'):
            for key in config['podcasts']:
                podcast_name = key
                value = config['podcasts'][key]
                if value:
                    podcast_name += '=' + value
                podcasts.append(podcast_name)
        return podcasts

    def __parse_field(self, config, section, variable, default_value, process=None):
        try:
            value = config[section][variable]
            if process is not None:
                value = process(value)
            return value
        except KeyError:
            return default_value

    def __create_directories(self):
        os.makedirs(self.download_path, exist_ok=True)
        os.makedirs(self.image_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.database_file), exist_ok=True)
