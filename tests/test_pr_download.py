import common.config as config
import common.db as db
from pr_download.pr_download import PodcastDownloader

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db = db.open_database(database_file=':memory:')
        cfg = config.Config()
        self.pd = PodcastDownloader(cfg, self.db)

    def tearDown(self):
        self.db.close()


# TODO:
# download file
# remove file
# reserve download
# mark file as downloaded
# register error
# files to remove
# mark file as removed
