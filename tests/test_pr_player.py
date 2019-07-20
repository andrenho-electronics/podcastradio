import unittest

import common.config as config
import common.db as db
from pr_player.pr_player import PodcastPlayer

class BaseTest(unittest.TestCase):

    def setUp(self):
        self.db = db.open_database(database_file=':memory:')
        self.pd = PodcastDownloader(self.cfg, self.db)

    def tearDown(self):
        self.db.close()

