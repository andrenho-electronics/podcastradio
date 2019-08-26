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



# TODO - test list
#  - mock vlc
#  - 1 song playlist
#    - play/pause
#    - song over (without removal)
#    - song over (with removal)
#  - 3 song playlist
#    - play/pause
#    - song over (without removal)
#    - song over (with removal)
#  - exceptions
#    - play an empty playlist
#    - start playing in the middle of mp3
