import os
import os.path
import responses
import shutil
import unittest
import uuid

import common.config as config
import common.db as db
from pr_download.pr_download import PodcastDownloader

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db = db.open_database(database_file=':memory:')
        self.cfg = config.Config(
            download_path = 'tests/download'
        )
        os.makedirs('tests/download')
        self.pd = PodcastDownloader(self.cfg, self.db)

    def tearDown(self):
        self.db.close()
        shutil.rmtree('tests/download')

class TestDownloadFile(BaseTest):

    @responses.activate
    def test_download_success(self):
        url = 'http://localhost/podcast.mp3'
        responses.add(responses.GET, url, b'My podcast', status=200)
        filename = self.pd.download_file(url)
        self.assertIsNotNone(filename)
        self.assertEqual(str(uuid.UUID(filename)), filename, msg="Is filename an UUID?")
        try:
            self.assertTrue(os.path.isfile(self.pd.cfg.download_path + '/' + filename))
        finally:
            os.remove(self.pd.cfg.download_path + '/' + filename)

    @responses.activate
    def test_download_failed(self):
        url = 'http://localhost/podcast.mp3'
        responses.add(responses.GET, url, 'Not found', status=404)
        with self.assertRaises(Exception):
            self.pd.download_file(url)
        
    @responses.activate
    @unittest.skip("Can't simulate partial download")
    def test_download_incomplete(self):
        url = 'http://localhost/podcast.mp3'
        # create incomplete download file
        with open('tests/download/incomplete', 'wb') as f:
            f.write(b'XXX');
        try:
            # simulate download continuation
            responses.add(responses.GET, url, b'My podcast', status=200)
            filename = self.pd.download_file(url, 'incomplete')
            self.assertEqual('incomplete', filename)
            # check if initial part of download was not overwritten
            with open('tests/download/incomplete', 'rb') as f:
                self.assertEqual(b'XXXpodcast', f.read())
        finally:
            os.remove('tests/download/incomplete')


class TestDatabase(BaseTest):

    def test_update_download_filename(self):
        url = 'http://localhost/podcast.mp3'
        self.db.execute('INSERT INTO downloads ( url, episode_rowid ) VALUES ( ?,  ? )',
                (url, 0))
        self.pd.update_download_filename(url, 'test')
        self.assertEqual('test', self.db.execute('SELECT filename FROM downloads WHERE url = ?', (url,)).fetchone()[0])

    def test_incomplete_download_filename(self):
        url = 'http://localhost/podcast.mp3'
        self.db.execute('INSERT INTO downloads ( url, episode_rowid, filename ) VALUES ( ?,  ?, ? )',
                (url, 0, 'test'))
        self.db.commit()
        self.assertEqual('test', self.pd.incomplete_download_filename(url))

    def test_reserve_next_file(self):
        url1 = 'http://localhost/podcast1.mp3'
        url2 = 'http://localhost/podcast2.mp3'
        self.db.execute('INSERT INTO downloads ( url, episode_rowid ) VALUES ( ?, ? )', (url1, 1))
        self.db.execute('INSERT INTO downloads ( url, episode_rowid ) VALUES ( ?, ? )', (url2, 2))
        self.db.commit()
        url = self.pd.reserve_next_file()
        self.assertTrue(url == url1 or url == url2)
        self.assertEqual(1, self.db.execute('SELECT count(*) FROM downloads WHERE thread IS NOT NULL').fetchone()[0])
        self.assertEqual(os.getpid(), self.db.execute('SELECT thread FROM downloads WHERE url = ?', (url,)).fetchone()[0])
        url_next = self.pd.reserve_next_file()
        self.assertNotEqual(url, url_next)
        self.assertEqual(2, self.db.execute('SELECT count(*) FROM downloads WHERE thread IS NOT NULL').fetchone()[0])

    def test_mark_file_as_downloaded(self):
        podcast_url = 'http://localhost/podcast.xml'
        url = 'http://localhost/podcast.mp3'
        filename = 'xyz'
        self.db.execute('INSERT INTO podcasts ( url ) VALUES ( ? )', (podcast_url,))
        self.db.execute('INSERT INTO episodes ( podcast_url, episode_url ) VALUES ( ?, ? )', (podcast_url, url))
        self.db.execute('INSERT INTO downloads ( url, episode_rowid, filename ) VALUES ( ?, ?, ? )', (url, 1, filename))
        self.db.commit()
        self.pd.mark_file_as_downloaded(url, filename)
        row = self.db.execute('SELECT downloaded, last_status, filename FROM episodes WHERE episode_url = ?', (url,)).fetchone()
        self.assertEqual(1, row[0])
        self.assertEqual(200, row[1])
        self.assertEqual(filename, row[2])
        self.assertEqual(0, self.db.execute('SELECT count(*) FROM downloads WHERE url = ?', (url,)).fetchone()[0])

    def test_register_error(self):
        podcast_url = 'http://localhost/podcast.xml'
        url = 'http://localhost/podcast.mp3'
        self.db.execute('INSERT INTO podcasts ( url ) VALUES ( ? )', (podcast_url,))
        self.db.execute('INSERT INTO episodes ( podcast_url, episode_url ) VALUES ( ?, ? )', (podcast_url, url))
        self.db.execute('INSERT INTO downloads ( url, episode_rowid ) VALUES ( ?, ? )', (url, 1))
        self.pd.register_error(url, Exception('Page not found'), 404)
        row = self.db.execute('SELECT last_status, error FROM episodes WHERE episode_url = ?', (url,)).fetchone()
        self.assertEqual(404, row[0])
        self.assertEqual('Page not found', row[1])

    def test_files_to_remove(self):
        url1 = 'http://localhost/podcast1.mp3'
        url2 = 'http://localhost/podcast2.mp3'
        self.db.execute('INSERT INTO to_remove ( url ) VALUES ( ? )', (url1,))
        self.db.execute('INSERT INTO to_remove ( url ) VALUES ( ? )', (url2,))
        self.db.commit()
        urls = self.pd.files_to_remove()
        self.assertEqual(2, len(urls))
        self.assertTrue(url1 in urls)
        self.assertTrue(url2 in urls)

    def test_mark_file_as_removed(self):
        podcast_url = 'http://localhost/podcast.xml'
        url1 = 'http://localhost/podcast1.mp3'
        url2 = 'http://localhost/podcast2.mp3'
        filename = 'xyz'
        self.db.execute('INSERT INTO podcasts ( url ) VALUES ( ? )', (podcast_url,))
        self.db.execute('INSERT INTO episodes ( podcast_url, episode_url, filename ) VALUES ( ?, ?, ? )', 
                (podcast_url, url1, filename))
        self.db.execute('INSERT INTO to_remove ( url ) VALUES ( ? )', (url1,))
        self.db.execute('INSERT INTO to_remove ( url ) VALUES ( ? )', (url2,))
        self.db.commit()
        self.pd.mark_file_as_removed(filename)
        self.assertEqual(1, self.db.execute('SELECT count(*) FROM to_remove').fetchone()[0])
        self.assertEqual(url2, self.db.execute('SELECT url FROM to_remove').fetchone()[0])
        row = self.db.execute('SELECT downloaded, last_status, filename FROM episodes WHERE episode_url = ?', (url1,)).fetchone()
        self.assertEqual(0, row[0])
        self.assertEqual(None, row[1])
        self.assertEqual(None, row[2])
