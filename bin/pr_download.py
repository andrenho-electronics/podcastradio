#!/usr/bin/env python3

import configparser
import logging
import os
import sqlite3
import time
import pprint
import requests
import threading
import xml.etree.ElementTree as ET  
from email.utils import parsedate_tz
from requests.exceptions import HTTPError
from pprint import pprint

# CONFIG #######################################################################

class Config:
    def __init__(self):
        self.podcasts = []
        self.keep_episodes = 5
        self.download_path = '/var/db/podcastradio/download'
        self.image_path = '/var/db/podcastradio/images'
        self.download_threads = 3

def read_config_file(filename):
    cfg = Config()
    config = configparser.ConfigParser(delimiters=('=',), allow_no_value=True)
    if len(config.read(filename)) == 0:
        raise Excpetion('File ' + filename + ' not found.')
    try:
        for key in config['podcasts']:
            cfg.podcasts.append(key)
    except KeyError:
        pass
    try:
        cfg.keep_episodes = int(config['config']['keep_episodes'])
    except KeyError:
        pass
    try:
        cfg.download_path = config['config']['download_path']
        os.makedirs(cfg.download_path, exist_ok=True)
    except KeyError:
        pass
    try:
        cfg.image_path = config['config']['image_path']
        os.makedirs(cfg.image_path, exist_ok=True)
    except KeyError:
        pass
    try:
        cfg.download_threads = int(config['config']['download_threads'])
    except KeyError:
        pass
    return cfg


# DATABASE #####################################################################

def create_database_objects(conn):
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS podcasts (
            url           TEXT PRIMARY KEY,
            title         TEXT,
            image_path    TEXT,
            keep_episodes INTEGER   DEFAULT 5,
            last_status   INTEGER,
            error         TEXT
        );
    ''')
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS episodes (
            podcast_url   TEXT,
            episode_url   TEXT,
            title         TEXT,
            date          INTEGER,
            length        TEXT,
            nbytes        INTEGER,
            downloaded    BOOLEAN   DEFAULT 0,
            keep          BOOLEAN   DEFAULT 0,
            PRIMARY KEY(podcast_url, episode_url),
            FOREIGN KEY(podcast_url) REFERENCES podcasts(url)
        );
    ''')
    conn.cursor().execute('''
        CREATE TABLE IF NOT EXISTS downloads (
            url             TEXT     PRIMARY KEY,
            episode_rowid   INTEGER  UNIQUE,
            podcast_title   TEXT,
            episode_title   TEXT,
            thread          INTEGER  DEFAULT NULL,
            episode_size    INTEGER  DEFAULT NULL,
            bytes_downd     INTEGER  DEFAULT 0,
            last_status     INTEGER,
            FOREIGN KEY(url) REFERENCES episodes(episode_url)
        );
    ''')

def open_database():
    conn = sqlite3.connect('podcastradio.db')
    create_database_objects(conn)
    return conn


# PODCASTS #####################################################################

def check_podcasts(cfg, db, throw_exceptions=False):

    def check_config_against_db(cfg, db):
        c = db.cursor()
        urls_in_db = []
        # URLs in db but not in config - delete from DB
        for row in c.execute('SELECT url FROM podcasts'):
            if row[0] not in cfg.podcasts:
                c.execute('DELETE FROM podcasts WHERE url=?', (row[0],))
                logging.info('URL ' + row[0] + ' was deleted from database.')
            else:
                urls_in_db.append(row[0])
        # URLs in config but not in db - insert to db
        for url in cfg.podcasts:
            if url not in urls_in_db:
                c.execute('INSERT INTO podcasts ( url, keep_episodes ) VALUES ( ?, ? )',
                        (url, cfg.keep_episodes))
                urls_in_db.append(url)
                logging.info('URL ' + url + ' was inserted into database.')
        db.commit()
        return urls_in_db

    def download_podcast_rss(url):
        response = requests.get(url)
        db.cursor().execute('UPDATE podcasts SET last_status = ? WHERE url = ?', (response.status_code, url))
        db.commit()
        response.raise_for_status()
        logging.info('Podcast XML file downloaded from URL ' + url)
        return response.content

    def parse_podcast_rss(xml):
        class PodcastInfo:
            pass
        class Episode:
            pass
        info = PodcastInfo()
        info.title = None
        info.image_path = None
        root = ET.fromstring(xml)
        title_element = root.find('./channel/title')
        if title_element is not None:
            info.title = title_element.text
            info.episodes = []
            image_element = root.find('./channel/image/url')
            if image_element is not None:
                info.image_path = image_element.text
            for item in root.findall('./channel/item'):
                ep = Episode()
                if item.find('enclosure') is not None:
                    ep.url = item.find('enclosure').attrib['url']
                    ep.title = item.find('title').text
                    ep.date = int(time.mktime(parsedate_tz(item.find('pubDate').text)[0:9]))  # date in unix timestamp format
                    try:
                        ep.length = item.find('{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text
                    except AttributeError:
                        pass
                    info.episodes.append(ep)
            logging.info('Parsed data from podcast RSS: ' + info.title + ' (' + str(len(info.episodes)) + ' episodes)')
            return info
        else:
            return None

    def update_image(cfg, url, db, info):
        current_image = None
        try:
            current_image = db.cursor().execute('SELECT image_path FROM podcasts WHERE url = ?', (url,)).fetchone()[0]
        except:
            return
        if info.image_path != current_image:
            response = requests.get(info.image_path)
            try:
                response.raise_for_status()
            except:
                logging.warning('Error loading image file from URL ' + info.image_path)
                return
            filename = info.image_path[info.image_path.rfind("/")+1:]
            os.makedirs(cfg.image_path, exist_ok=True)
            full_filename = cfg.image_path + '/' + filename
            with open(cfg.image_path + '/' + filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=128):
                    f.write(chunk)
            info.image_path = cfg.image_path + '/' + filename
            logging.info('Podcast image file downloaded from URL ' + info.image_path)

    def update_podcast_database(url, db, info):
        db.cursor().execute('''
            UPDATE podcasts
               SET title = ?,
                   image_path = ?
             WHERE url = ?''', (info.title, info.image_path, url))
        for ep in info.episodes:
            db.cursor().execute('''
                INSERT OR IGNORE INTO episodes ( podcast_url, episode_url, title, date, length )
                                VALUES ( ?, ?, ?, ?, ? )''',
                (url, ep.url, ep.title, ep.date, ep.length))
        db.commit()
        logging.info('Tables updated for podcast ' + info.title)

    urls = check_config_against_db(cfg, db)
    for url in urls:
        try:
            xml = download_podcast_rss(url)
            info = parse_podcast_rss(xml)
            if info:
                update_image(cfg, url, db, info)
                update_podcast_database(url, db, info)
        except Exception as e:
            db.cursor().execute('UPDATE podcasts SET error = ? WHERE url = ?', (str(e), url))
            db.commit()
            logging.warning(str(e))
            if throw_exceptions:
                raise e
            continue


# EPISODES #####################################################################

def download_episodes(db, cfg):

    def remove_old_podcast_episodes(url, keep, db, cfg):
        for row in db.cursor().execute('''
            SELECT rowid, episode_url, title
              FROM episodes
             WHERE podcast_url = ?
               AND keep = 0
               AND downloaded = 1
          ORDER BY date DESC
             LIMIT -1 OFFSET ?''', (url, keep)):
            os.remove(cfg.download_path + '/' + row[0])
            db.cursor.execute('UPDATE episodes SET downloaded = 0 WHERE episode_url = ?', (row[1],))
            logging.info("Removed episode '" + row[2] + "'")
        db.commit()

    def download_new_podcast_episodes(url, db):
        db.cursor().execute('''
            INSERT OR IGNORE INTO downloads ( url, podcast_title, episode_title, episode_rowid )
                 SELECT episode_url, ptitle, ptitle, erowid
                   FROM (SELECT episode_url, p.title ptitle, e.title etitle, e.rowid erowid, downloaded
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
                     AND keep = 1''', (url, cfg.keep_episodes, url))
        db.commit()

    for row in db.cursor().execute('SELECT url, keep_episodes FROM podcasts'):
        url = row[0]
        remove_old_podcast_episodes(url, row[1], db, cfg)
        download_new_podcast_episodes(url, db)


# DOWNLOAD THREAD ##############################################################

class DownloadThread(threading.Thread):

    counter = 0
    get_episode_lock = threading.Lock()

    @staticmethod
    def remove_thread_locks(db):
        db.cursor().execute('DELETE FROM downloads')
        db.commit()

    def __init__(self, cfg):
        threading.Thread.__init__(self)
        self.number = DownloadThread.counter
        self.cfg = cfg
        DownloadThread.counter += 1

    def run(self):
        logging.info('Download thread #' + str(self.number) + ' started.')
        db = open_database()
        while True:
            # find a new download
            download = None
            with DownloadThread.get_episode_lock:  # lock threads so another thread does not reserve the same download
                for row in db.cursor().execute('''
                    SELECT url, episode_rowid, podcast_title
                      FROM downloads 
                     WHERE thread IS NULL
                     LIMIT 1'''):
                    download = (row[0], row[1])
                    db.cursor().execute('UPDATE downloads SET thread = ? WHERE url = ?', 
                            (self.number, row[0]))
                    db.commit()
                    logging.info('Thread #' + str(self.number) + ': downloading ' + row[0] + ' (' + row[2] + ')')
            # download episode
            if download is not None:
                url, rowid = download
                with open(self.cfg.download_path + '/' + str(rowid), 'wb') as f:
                    try:
                        # open URL
                        response = requests.get(url, stream=True)
                        db.cursor().execute('UPDATE downloads SET last_response = ? WHERE url = ?', (response.status, url))
                        response.raise_for_status()
                        # get episode size
                        size = int(response.headers.get('content-length'))
                        db.cursor().execute('UPDATE downloads SET episode_size = ? WHERE url = ?', (size, url))
                        db.commit()
                        # download in 1 Mb chunks
                        downloaded = 0
                        for data in response.iter_content(chunk_size=(1024 * 1024)):  # 1 Mb chunks
                            downloaded += len(data)
                            f.write(data)
                            try:
                                db.cursor().execute('UPDATE downloads SET bytes_downd = ? WHERE url = ?', (downloaded, url))
                                db.commit()
                            except sqlite3.OperationalError:
                                pass   # ignore database locked
                        # episode finished downloading
                        db.cursor().execute('DELETE FROM downloads WHERE url = ?', (url,))
                        db.cursor().execute('''UPDATE episodes
                                                  SET downloaded = 1
                                                    , nbytes = ?
                                                WHERE episode_url = ?''', (size, url))
                        db.commit()
                        logging.info('Thread #' + str(self.number) + ': download finished of URL ' + url)
                    except Exception as e:
                        logging.warning('Error downloading url <' + url + '>: ' + str(e))
            # wait one second
            time.sleep(1)

# MAIN #########################################################################

if __name__ == '__main__':
    logging.basicConfig(level='INFO')
    db  = open_database()
    cfg = read_config_file('download.ini')

    DownloadThread.remove_thread_locks(db)
    for _ in range(0, cfg.download_threads):
        DownloadThread(cfg).start()

    while True:
        logging.info('-------------------------------------------------------')
        logging.info('Executing loop...')
        cfg = read_config_file('download.ini')
        check_podcasts(cfg, db)
        download_episodes(db, cfg)
        logging.info('Waiting for next loop...')
        time.sleep(120)
        #input("Press Enter to continue...")

# vim: foldmethod=marker
