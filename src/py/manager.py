import logging
import screenmsg

class Manager:

    def __init__(self, scr_queue):
        logging.debug("Manager initialized.")
        self.scr_queue = scr_queue
        self.scr_queue.put(screenmsg.WelcomeMessage())
