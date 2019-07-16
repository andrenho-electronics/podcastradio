import unittest
from common.config import Config

class TestConfig(unittest.TestCase):

    def test_default_config(self):
        cfg = Config().read_config_file('tests/empty_config.ini', False)
        self.assertTrue(cfg is not None)
        def fail_cfg():
            cfg = read_config_file('tests/non_existing.ini')
        self.assertRaises(Exception, fail_cfg)

    def test_load_config(self):
        cfg = Config().read_config_file('tests/download.ini', False)
        self.assertEqual(['http://localhost/op1'], cfg.podcasts)
        self.assertEqual(2, cfg.keep_episodes)
        self.assertEqual('download', cfg.download_path)
        self.assertEqual(4, cfg.download_threads)

    def test_corruped_ini(self):
        def fail_cfg():
            cfg = Config().read_config_file('tests/corrupted.ini', False)
        self.assertRaises(Exception, fail_cfg)

    def test_equal_sign(self):
        cfg = Config().read_config_file('tests/equalsign.ini', False)
        self.assertEquals(['http://localhost:8080/op1=123'], cfg.podcasts)
