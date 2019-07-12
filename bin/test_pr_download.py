from pr_download import *
import os
import responses
import sqlite3
import tempfile
import unittest


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        create_database_objects(self.db)

    def tearDown(self):
        self.db.close()


class TestConfig(unittest.TestCase):

    def test_default_config(self):
        cfg = read_config_file('test/empty_config.ini')
        self.assertTrue(cfg is not None)
        def fail_cfg():
            cfg = read_config_file('test/non_existing.ini')
        self.assertRaises(Exception, fail_cfg)

    def test_load_config(self):
        cfg = read_config_file('test/download.ini')
        self.assertEqual(cfg.podcasts, ['http://localhost/op1'])
        self.assertEqual(cfg.keep_episodes, 2)
        self.assertEqual(cfg.download_path, 'download')
        self.assertEqual(cfg.download_threads, 4)

    def test_corruped_ini(self):
        def fail_cfg():
            cfg = read_config_file('test/corrupted.ini')
        self.assertRaises(Exception, fail_cfg)


class TestCheckPodcasts(BaseTest):

    def test_no_podcasts(self):
        cfg = Config()
        check_podcasts(cfg, self.db, True)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 0)

    @responses.activate
    def test_empty_rss(self):
        cfg = Config()
        cfg.podcasts = ['http://localhost/op1']
        responses.add(responses.GET, 'http://localhost/op1', body='<?xml version="1.1"?><!DOCTYPE _[<!ELEMENT _ EMPTY>]><_/>', status=200)
        check_podcasts(cfg, self.db, True)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 1)

    @responses.activate
    def test_title_only(self):
        cfg = Config()
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
        cfg = Config()
        cfg.podcasts = ['http://localhost/op1']
        responses.add(responses.GET, 'http://localhost/op1', body='Not found', status=404)
        check_podcasts(cfg, self.db)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM podcasts').fetchone()[0], 1)
        self.assertEqual(self.db.cursor().execute('SELECT title FROM podcasts LIMIT 1').fetchone()[0], None)
        self.assertEqual(self.db.cursor().execute('SELECT last_status FROM podcasts LIMIT 1').fetchone()[0], 404)
    
    @responses.activate
    def test_remove_podcast(self):
        cfg = Config()
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
            cfg = Config()
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
        cfg = Config()
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
<rss>
    <channel>
        <title>My podcast</title>
        <image>
            <url>http://localhost/image.jpg</url>
        </image>
        <item>
            <title>Episode 1</title>
            <pubDate>Wed, 10 Jul 2019 13:01:37 -0300</pubDate>
            <itunes:duration>00:10:10</itunes:duration>
            <enclosure url="https://localhost/episode1.mp3" length="9760190" type="audio/mpeg"/>
        </item>
        <item>
            <title>Episode 2</title>
            <pubDate>Wed, 11 Jul 2019 13:01:37 -0300</pubDate>
            <itunes:duration>00:12:10</itunes:duration>
            <enclosure url="https://localhost/episode2.mp3" length="8760190" type="audio/mpeg"/>
        </item>
    </channel>
</rss>
'''

class TestCheckEpisodes(BaseTest):

    @responses.activate
    def test_episodes(self):
        cfg = Config()
        cfg.podcasts = ['http://localhost/op1']
        responses.add(responses.GET, 'http://localhost/op1', body=podcast1_xml)
        check_podcasts(cfg, self.db, True)
        self.assertEqual(self.db.cursor().execute('SELECT count(*) FROM episodes').fetchone()[0], 2)
        # TODO - check each individual value

# check_podcasts:
#  - interpret podcast XML with episodes
#  - interpret podcast XML with broken episodes
# download_episodes (identify episodes to download)
#  - simply download episodes
#  - don't redownload
#  - keep episodes marked as keep
#  - clear old episodes
# DownloadThread:
#  - reserve episode
#  - download episode
#  - download error
#  - connection broken in the middle