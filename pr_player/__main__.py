import pr_player.pr_player as pr_player

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
pp  = pr_player.PodcastPlayer(cfg, db)

current_state = 'pause'
while True:
    if pp.state() != 'over':
        if pp.state() == 'play' and current_state != 'play':
            pp.play()
            current_state = 'play'
        else if pp.state() != 'play' and current_state == 'play':
            pp.pause()
            current_state = 'pause'
    pp.check_for_end_of_audio()
    time.sleep(0.3)
