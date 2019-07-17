import os
import os.path
import responses
import unittest

import common.config as config
import common.db as db
from pr_download.pr_download import PodcastDownloader

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db = db.open_database(database_file=':memory:')
        cfg = config.Config(
            download_path = 'tests/download'
        )
        self.pd = PodcastDownloader(cfg, self.db)

    def tearDown(self):
        self.db.close()
        #os.rmdir('tests/download')

class TestDownloadFile(BaseTest):

    @responses.activate
    def test_download_success(self):
        url = 'http://localhost/podcast.mp3'
        responses.add(responses.GET, url, b'My podcast', status=200)
        filename = self.pd.download_file(url)
        self.assertIsNotNone(filename)
        try:
            self.assertTrue(os.path.isfile(self.pd.cfg.download_path + '/' + filename))
        finally:
            os.remove(self.pd.cfg.download_path + '/' + filename)

# TODO:
# download file
#  - download successful
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
