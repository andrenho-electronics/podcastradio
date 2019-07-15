import unittest
from common.config import Config

class TestConfig(unittest.TestCase):

    def test_default_config(self):
        cfg = Config().read_config_file('test/empty_config.ini', False)
        self.assertTrue(cfg is not None)
        def fail_cfg():
            cfg = read_config_file('test/non_existing.ini')
        self.assertRaises(Exception, fail_cfg)

    def test_load_config(self):
        cfg = Config().read_config_file('test/download.ini', False)
        self.assertEqual(cfg.podcasts, ['http://localhost/op1'])
        self.assertEqual(cfg.keep_episodes, 2)
        self.assertEqual(cfg.download_path, 'download')
        self.assertEqual(cfg.download_threads, 4)

    def test_corruped_ini(self):
        def fail_cfg():
            cfg = Config().read_config_file('test/corrupted.ini', False)
        self.assertRaises(Exception, fail_cfg)

    def test_equal_sign(self):
        cfg = Config().read_config_file('test/equalsign.ini', False)
        self.assertEquals(['http://localhost:8080/op1=123'], cfg.podcasts)