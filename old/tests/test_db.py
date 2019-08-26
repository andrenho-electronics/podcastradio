import unittest
from common.db import open_database

class TestDB(unittest.TestCase):

    def test_db(self):
        db = open_database(database_file=':memory:')
        self.assertEqual(1, db.cursor().execute("SELECT count(*) FROM sqlite_master WHERE name = 'episodes'").fetchone()[0])
