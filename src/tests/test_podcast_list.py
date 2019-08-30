import unittest
from unittest.mock import MagicMock
from podcast import Podcast

from tests.setup import session_base

class TestPodcastList(unittest.TestCase):

    pod1 = 'localhost:8029/pod1'
    
    def test_new_podcast(self):
        Session = session_base(True)
        session = Session()
        Podcast.load_config_file = MagicMock(return_value=[
            TestPodcastList.pod1
        ])
        Podcast.update_from_config_file(session)
        podcasts = session.query(Podcast).all()
        self.assertEqual(1, len(podcasts))
        self.assertEqual(TestPodcastList.pod1, podcasts[0].url)