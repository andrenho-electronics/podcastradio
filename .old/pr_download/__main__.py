#!/usr/bin/env python3

import pr_download.pr_download as pr_download

import logging
import logging.handlers
import os
import time

import common.config as config
import common.db as db

logging.basicConfig(level='INFO')
if os.name == 'posix':
    root_logger = logging.getLogger()
    root_logger.addHandler(logging.handlers.SysLogHandler())

cfg = config.Config().read_config_file('podcastradio.ini')
db  = db.open_database(cfg)
pd  = pr_download.PodcastDownloader(cfg, db)

while True:
    logging.info('-------------------------------------------------------')
    logging.info('Executing loop...')

    # download files
    url = pd.reserve_next_file()
    if url:
        try:
            filename = pd.download_file(url, pd.incomplete_download_filename(url))
            pd.mark_file_as_downloaded(url, filename)
        except Exception as e:
            pd.register_error(url, e)

    # remove files
    for filename in pd.files_to_remove():
        pd.remove_file(filename)
        pd.mark_file_as_removed(filename)

    logging.info('Waiting for next loop...')
    if url is None:
        time.sleep(120)
