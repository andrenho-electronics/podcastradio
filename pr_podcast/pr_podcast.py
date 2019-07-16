#!/usr/bin/env python3

import configparser
import logging
import os
import sqlite3
import time
import pprint
import requests
import sys
import threading
import xml.etree.ElementTree as ET  
from dataclasses import *
from email.utils import parsedate_tz
from requests.exceptions import HTTPError
from pprint import pprint
from typing import List

@dataclass
class Podcast:
    title:      str = ""
    image_path: str = None
    episodes:   List[str] = field(default_factory=list)

@dataclass
class Episode:
    url:    str = ""
    title:  str = ""
    nbytes: int = 0
    date:   int = 0
    length: int = 0

def none_if_error(lazy_value):
    try:
        return lazy_value()
    except Exception:
        return None

class PodcastManager:

    def __init__(self, cfg, db):
        self.cfg = cfg
        self.db = db

    def update_podcast_list(self, throw_exceptions=False):
        urls = self.__update_db_from_config()
        for url in urls:
            try:
                xml = self.__download_podcast_rss(url)
                info = self.__parse_podcast_rss(xml)
                if info:
                    self.__update_image(url, info)
                    self.__update_podcast_database(url, info)
            except Exception as e:
                self.db.cursor().execute('UPDATE podcasts SET error = ? WHERE url = ?', (str(e), url))
                self.db.commit()
                logging.warning(str(e))
                if throw_exceptions:
                    raise e
                continue

    def mark_episodes_for_download(self):
        for row in self.db.cursor().execute('SELECT url, keep_episodes FROM podcasts'):
            url = row[0]
            self.__remove_old_podcast_episodes(url, row[1])
            self.__download_new_podcast_episodes(url)

    # 
    # private: podcasts
    #

    def __update_db_from_config(self):
        c = self.db.cursor()
        urls_in_db = []
        # URLs in db but not in config - delete from DB
        for row in c.execute('SELECT url FROM podcasts'):
            if row[0] not in self.cfg.podcasts:
                c.execute('DELETE FROM podcasts WHERE url=?', (row[0],))
                logging.info('URL ' + row[0] + ' was deleted from database.')
            else:
                urls_in_db.append(row[0])
        # URLs in config but not in db - insert to db
        for url in self.cfg.podcasts:
            if url not in urls_in_db:
                c.execute('INSERT INTO podcasts ( url, keep_episodes ) VALUES ( ?, ? )',
                        (url, self.cfg.keep_episodes))
                urls_in_db.append(url)
                logging.info('URL ' + url + ' was inserted into database.')
        self.db.commit()
        return urls_in_db

    def __download_podcast_rss(self, url):
        response = requests.get(url)
        self.db.cursor().execute('UPDATE podcasts SET last_status = ? WHERE url = ?', (response.status_code, url))
        self.db.commit()
        response.raise_for_status()
        logging.info('Podcast XML file downloaded from URL ' + url)
        return response.content

    def __parse_podcast_rss(self, xml):
        root = ET.fromstring(xml)
        title_element = root.find('./channel/title')
        if title_element is not None:
            podcast = Podcast(
                title = title_element.text,
                image_path = none_if_error(lambda: root.find('./channel/image/url').text)
            )
            for item in root.findall('./channel/item'):
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    podcast.episodes.append(Episode(
                        url    = enclosure.attrib['url'],
                        title  = none_if_error(lambda: item.find('title').text),
                        nbytes = none_if_error(lambda: int(enclosure.attrib['length'])),
                        date   = none_if_error(lambda: int(time.mktime(parsedate_tz(item.find('pubDate').text)[0:9]))),  # date in unix timestamp format
                        length = none_if_error(lambda: item.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text)
                    ))
            logging.info('Parsed data from podcast RSS: ' + podcast.title + ' (' + str(len(podcast.episodes)) + ' episodes)')
            return podcast
        else:
            return None

    def __update_image(self, url, info):
        current_image = None
        try:
            current_image = self.db.cursor().execute('SELECT image_path FROM podcasts WHERE url = ?', (url,)).fetchone()[0]
        except:
            return
        if info.image_path != current_image:
            response = requests.get(info.image_path)
            if not response.ok:
                logging.warning('Error loading image file from URL ' + info.image_path)
                return
            filename = info.image_path[info.image_path.rfind("/")+1:]
            os.makedirs(self.cfg.image_path, exist_ok=True)
            full_filename = self.cfg.image_path + '/' + filename
            with open(self.cfg.image_path + '/' + filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)
            info.image_path = self.cfg.image_path + '/' + filename
            logging.info('Podcast image file downloaded from URL ' + info.image_path)

    def __update_podcast_database(self, url, info):
        self.db.cursor().execute('''
            UPDATE podcasts
               SET title = ?,
                   image_path = ?
             WHERE url = ?''', (info.title, info.image_path, url))
        for ep in info.episodes:
            self.db.cursor().execute('''
                INSERT OR IGNORE INTO episodes ( podcast_url, episode_url, title, date, length, nbytes )
                                VALUES ( ?, ?, ?, ?, ?, ? )''',
                (url, ep.url, ep.title, ep.date, ep.length, ep.nbytes))
        self.db.commit()
        logging.info('Tables updated for podcast ' + info.title)

    #
    # private: episodes
    #

    def __remove_old_podcast_episodes(self, url, keep):
        self.db.cursor().execute('''
            INSERT OR IGNORE INTO to_remove ( url )
                           SELECT episode_url
                             FROM episodes
                            WHERE podcast_url = ?
                              AND keep = 0
                              AND downloaded = 1
                         ORDER BY date DESC
                            LIMIT -1 OFFSET ?''', (url, keep))
        self.db.commit()
        logging.info('Episodes marked to remove')

    def __download_new_podcast_episodes(self, url):
        self.db.cursor().execute('''
            INSERT OR IGNORE INTO downloads ( url, podcast_title, episode_title, episode_rowid )
                           SELECT episode_url, ptitle, etitle, erowid
                             FROM     (SELECT episode_url, p.title ptitle, e.title etitle, e.rowid erowid, downloaded
                                         FROM episodes e
                                   INNER JOIN podcasts p ON p.url = e.podcast_url
                                        WHERE e.podcast_url = ?
                                     ORDER BY date DESC
                                        LIMIT ?)
                            WHERE downloaded = 0
                            UNION
                           SELECT episode_url, p.title ptitle, e.title etitle, e.rowid erowid
                             FROM episodes e
                       INNER JOIN podcasts p ON p.url = e.podcast_url
                            WHERE e.podcast_url = ?
                              AND downloaded = 0
                              AND keep = 1''', (url, self.cfg.keep_episodes, url))
        self.db.commit()

# vim: foldmethod=marker
