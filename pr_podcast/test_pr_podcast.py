from pr_podcast import *
import config
import db
import pprint
import os
import responses
import sqlite3
import tempfile
import unittest

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db = db.open_database(database_file=':memory:')

    def tearDown(self):
        self.db.close()


class TestCheckPodcasts(BaseTest):

    def test_no_podcasts(self):
        cfg = config.Config()
        check_podcasts(cfg, self.db, True)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 0)

    @responses.activate
    def test_empty_rss(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        responses.add(responses.GET, 'http://localhost/op1', body='<?xml version="1.1"?><!DOCTYPE _[<!ELEMENT _ EMPTY>]><_/>', status=200)
        check_podcasts(cfg, self.db, True)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 1)

    @responses.activate
    def test_title_only(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        responses.add(responses.GET, 'http://localhost/op1', body='''
            <rss>
                <channel>
                    <title>My podcast</title>
                </channel>
            </rss>
        ''', status=200)
        check_podcasts(cfg, self.db, True)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 1)
        self.assertEqual(self.db.cursor().execute('SELECT title FROM podcasts LIMIT 1').fetchone()[0], 'My podcast')
        self.assertEqual(self.db.cursor().execute('SELECT last_status FROM podcasts LIMIT 1').fetchone()[0], 200)

    @responses.activate
    def test_failed(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        responses.add(responses.GET, 'http://localhost/op1', body='Not found', status=404)
        check_podcasts(cfg, self.db)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 1)
        self.assertEqual(self.db.cursor().execute('SELECT title FROM podcasts LIMIT 1').fetchone()[0], None)
        self.assertEqual(self.db.cursor().execute('SELECT last_status FROM podcasts LIMIT 1').fetchone()[0], 404)
    
    @responses.activate
    def test_remove_podcast(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        responses.add(responses.GET, 'http://localhost/op1', body='<?xml version="1.1"?><!DOCTYPE _[<!ELEMENT _ EMPTY>]><_/>', status=200)
        check_podcasts(cfg, self.db, True)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 1)
        cfg.podcasts = []
        check_podcasts(cfg, self.db, True)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 0)

    @responses.activate
    def test_image(self):
        tempdir = '/tmp/test_image'
        try:
            cfg = config.Config()
            cfg.podcasts = ['http://localhost/op1']
            cfg.image_path = tempdir
            responses.add(responses.GET, 'http://localhost/op1', body='''
                <rss>
                    <channel>
                        <title>My podcast</title>
                        <image>
                            <url>http://localhost/image.jpg</url>
                        </image>
                    </channel>
                </rss>
            ''', status=200)
            responses.add(responses.GET, 'http://localhost/image.jpg', b'My image', status=200)
            check_podcasts(cfg, self.db, True)
            self.assertEqual(self.db.cursor().execute('SELECT image_path FROM podcasts LIMIT 1').fetchone()[0], tempdir + '/image.jpg')
            with open(tempdir + '/image.jpg', mode='rb') as f:
                self.assertEqual(f.read(), b'My image')
        finally:
            os.remove(tempdir + '/image.jpg')
            os.rmdir(tempdir)

    @responses.activate
    def test_broken_xml(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        responses.add(responses.GET, 'http://localhost/op1', body='''
            <rss>
                <chan...
        ''', status=200)
        check_podcasts(cfg, self.db)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 1)
        self.assertEqual(self.db.cursor().execute('SELECT title FROM podcasts LIMIT 1').fetchone()[0], None)
        self.assertNotEqual(self.db.cursor().execute('SELECT error FROM podcasts LIMIT 1').fetchone()[0], None)


podcast1_xml = '''
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:media="http://search.yahoo.com/mrss" version="2.0">
    <channel>
        <title>My podcast</title>
        <image>
            <url>http://localhost/image.jpg</url>
        </image>
        <item>
            <title>Episode 1</title>
            <pubDate>Wed, 10 Jul 2019 13:01:37 -0300</pubDate>
            <itunes:duration>00:10:10</itunes:duration>
            <enclosure url="https://localhost/episode1.mp3" length="9760190" type="audio/mpeg" />
        </item>
        <item>
            <title>Episode 2</title>
            <pubDate>Wed, 11 Jul 2019 13:01:37 -0300</pubDate>
            <enclosure url="https://localhost/episode2.mp3" type="audio/mpeg" />
        </item>
    </channel>
</rss>
'''

class TestCheckEpisodes(BaseTest):

    @responses.activate
    def test_episodes(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        cfg.image_path = 'images'
        responses.add(responses.GET, 'http://localhost/op1', body=podcast1_xml)
        responses.add(responses.GET, 'http://localhost/image.jpg', b'My image')
        check_podcasts(cfg, self.db, True)
        self.assertEqual(2, self.db.cursor().execute('SELECT count(*) FROM episodes').fetchone()[0])
        podcast_url, title, date, length, nbytes, downloaded, keep = \
            self.db.cursor().execute("""SELECT podcast_url, title, date, length, nbytes, downloaded, keep 
                                          FROM episodes 
                                         WHERE episode_url='https://localhost/episode1.mp3'""").fetchone()
        self.assertEqual('http://localhost/op1', podcast_url)
        self.assertEqual('Episode 1', title)
        self.assertTrue(date > 0)
        self.assertEqual(9760190, nbytes)
        self.assertEqual(0, downloaded)
        self.assertEqual(0, keep)

    @responses.activate
    def test_broken_xml1(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        cfg.image_path = 'images'
        responses.add(responses.GET, 'http://localhost/op1', body='<rss><channel><title>X</title><item></item></channel></rss>')
        check_podcasts(cfg, self.db, True)
        self.assertEqual(0, self.db.cursor().execute('SELECT count(*) FROM episodes').fetchone()[0])

    @responses.activate
    def test_broken_xml2(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        cfg.image_path = 'images'
        responses.add(responses.GET, 'http://localhost/op1', body='<rss><channel><title>X</title><item><enclosure url="xxx"/></item></channel></rss>')
        check_podcasts(cfg, self.db, True)
        self.assertEqual(1, self.db.cursor().execute('SELECT count(*) FROM episodes').fetchone()[0])

class ChooseEpisodesToDownload(BaseTest):

    @responses.activate
    def test_simple(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        cfg.image_path = 'images'
        cfg.keep_episodes = 5
        responses.add(responses.GET, 'http://localhost/op1', body=podcast1_xml)
        responses.add(responses.GET, 'http://localhost/image.jpg', b'My image')
        check_podcasts(cfg, self.db, True)
        download_episodes(self.db, cfg)
        self.assertEqual(2, self.db.cursor().execute('SELECT count(*) FROM downloads').fetchone()[0])
        ptitle, etitle = self.db.cursor().execute("SELECT podcast_title, episode_title FROM downloads WHERE url='https://localhost/episode1.mp3'").fetchone()
        self.assertEqual('My podcast', ptitle)
        self.assertEqual('Episode 1', etitle)
        etitle = self.db.cursor().execute("SELECT episode_title FROM downloads WHERE url='https://localhost/episode2.mp3'").fetchone()[0]
        self.assertEqual('Episode 2', etitle)

    @responses.activate
    def test_just_one(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        cfg.image_path = 'images'
        cfg.keep_episodes = 1
        responses.add(responses.GET, 'http://localhost/op1', body=podcast1_xml)
        responses.add(responses.GET, 'http://localhost/image.jpg', b'My image')
        check_podcasts(cfg, self.db, True)
        download_episodes(self.db, cfg)
        self.assertEqual(1, self.db.cursor().execute('SELECT count(*) FROM downloads').fetchone()[0])
        url = self.db.cursor().execute("SELECT url FROM downloads").fetchone()[0]
        self.assertEqual('https://localhost/episode2.mp3', url)  # latest episode first

    @responses.activate
    def test_new_episode_downloaded(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        cfg.image_path = 'images'
        cfg.keep_episodes = 1
        responses.add(responses.GET, 'http://localhost/op1', body=podcast1_xml)
        responses.add(responses.GET, 'http://localhost/image.jpg', b'My image')
        # loop
        check_podcasts(cfg, self.db, True)
        download_episodes(self.db, cfg)
        self.assertEqual(1, self.db.cursor().execute('SELECT count(*) FROM downloads').fetchone()[0])
        url = self.db.cursor().execute("SELECT url FROM downloads").fetchone()[0]
        self.assertEqual('https://localhost/episode2.mp3', url)  # latest episode first
        # mark episode 2 as downloaded
        self.db.cursor().execute('UPDATE episodes SET downloaded = 1 WHERE episode_url = ?', (url,))
        self.db.commit()
        # loop again, it should not change anything
        check_podcasts(cfg, self.db, True)
        download_episodes(self.db, cfg)
        self.assertEqual(1, self.db.cursor().execute('SELECT count(*) FROM downloads').fetchone()[0])
        url = self.db.cursor().execute("SELECT url FROM downloads").fetchone()[0]
        self.assertEqual('https://localhost/episode2.mp3', url)  # latest episode first
        # add a new episode
        self.db.cursor().execute('''
            INSERT INTO episodes ( podcast_url, episode_url, title, date )
                 VALUES ( 'http://localhost/op1', 'https://localhost/episode3.mp3', 'My Episode 3', 2562774497 )''')
        self.db.commit()
        # assume episode 2 was downloaded
        self.db.cursor().execute("UPDATE episodes SET downloaded=1 WHERE episode_url='https://localhost/episode2.mp3'")
        self.db.cursor().execute("DELETE FROM downloads")
        self.db.commit()
        # loop again
        download_episodes(self.db, cfg)
        # now, the episode 3 must be set for download -- let's assume is downloaded
        self.assertEqual(1, self.db.cursor().execute('SELECT count(*) FROM downloads').fetchone()[0])
        self.assertEqual('My Episode 3', self.db.cursor().execute('SELECT episode_title FROM downloads').fetchone()[0])
        self.db.cursor().execute("UPDATE episodes SET downloaded=1 WHERE episode_url='https://localhost/episode3.mp3'")
        self.db.commit()
        # on the next loop, episode 2 must be set for remove
        download_episodes(self.db, cfg)
        self.assertEqual(1, self.db.cursor().execute('SELECT count(*) FROM to_remove').fetchone()[0])
        self.assertEqual('https://localhost/episode2.mp3', self.db.cursor().execute('SELECT url FROM to_remove').fetchone()[0])

    @responses.activate
    def test_keep_episodes(self):
        cfg = config.Config()
        cfg.podcasts = ['http://localhost/op1']
        cfg.image_path = 'images'
        cfg.keep_episodes = 1
        responses.add(responses.GET, 'http://localhost/op1', body=podcast1_xml)
        responses.add(responses.GET, 'http://localhost/image.jpg', b'My image')
        # loop
        check_podcasts(cfg, self.db, True)
        download_episodes(self.db, cfg)
        # mark episode 2 as downloaded, and also as kept
        self.db.cursor().execute('UPDATE episodes SET keep = 1 WHERE episode_url = ?', ('https://localhost/episode2.mp3',))
        self.db.commit()
        # loop again, and assume episode 2 was downloaded
        check_podcasts(cfg, self.db, True)
        download_episodes(self.db, cfg)
        self.db.cursor().execute('UPDATE episodes SET downloaded = 1 WHERE episode_url = ?', ('https://localhost/episode2.mp3',))
        self.db.cursor().execute("DELETE FROM downloads")
        self.db.commit()
        # add a new episode
        self.db.cursor().execute('''
            INSERT INTO episodes ( podcast_url, episode_url, title, date )
                 VALUES ( 'http://localhost/op1', 'https://localhost/episode3.mp3', 'My Episode 3', 2562774497 )''')
        self.db.commit()
        # loop again
        self.assertEqual(0, self.db.cursor().execute('SELECT count(*) FROM downloads').fetchone()[0])
        download_episodes(self.db, cfg)
        # now, the episode 3 must be set for download -- let's assume is downloaded
        self.assertEqual(1, self.db.cursor().execute('SELECT count(*) FROM downloads').fetchone()[0])
        self.assertEqual('My Episode 3', self.db.cursor().execute('SELECT episode_title FROM downloads').fetchone()[0])
        self.db.cursor().execute("UPDATE episodes SET downloaded=1 WHERE episode_url='https://localhost/episode3.mp3'")
        self.db.commit()
        # on the next loop, episode 2 must NOT be set for remove
        download_episodes(self.db, cfg)
        self.assertEqual(0, self.db.cursor().execute('SELECT count(*) FROM to_remove').fetchone()[0])

