import pr_player.pr_player as pr_player
import pr_player.state as state

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

current_state = state.State('', 'stop')
while True:
    new_state = pp.current_state()
    if new_state != current_state:
        if new_state.playing == 'play':
            pp.play()
        elif new_state.playing == 'pause':
            pp.pause()
        elif new_state.playing == 'done':
            pp.play_next()
        current_state = new_state
    pp.update_state()
    time.sleep(0.3)
