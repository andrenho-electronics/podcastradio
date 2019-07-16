import pr_podcast.pr_podcast as pr_podcast

import common.config as config
import common.db as db
import logging
import logging.handlers
import os
import time

logging.basicConfig(level='INFO')
if os.name == 'posix':
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(logging.handlers.SysLogHandler(address='/dev/log/'))

cfg = config.Config().read_config_file('podcastradio.ini')
db  = db.open_database(cfg)
pm  = pr_podcast.PodcastManager(cfg, db)

while True:
    logging.info('-------------------------------------------------------')
    logging.info('Executing loop...')
    pm.cfg = config.Config().read_config_file('podcastradio.ini')
    pm.update_podcast_list()
    pm.mark_episodes_for_download()
    logging.info('Waiting for next loop...')
    time.sleep(120)

