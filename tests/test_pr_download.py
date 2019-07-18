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


# TODO:
# download file
#  - error on download
#  - download incomplete file
# remove file
#  - valid file
#  - invalid file
# reserve download
# mark file as downloaded
# register error
# files to remove
# mark file as removed
# incomplete download_filename
