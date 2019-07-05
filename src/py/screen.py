from abc import abstractmethod, ABC
import logging
import time
import threading

class Screen(threading.Thread, ABC):

    def __init__(self, scr_queue):
        threading.Thread.__init__(self)
        self.queue = scr_queue

    def run(self):
        while True:
            self.queue.execute(self)
            time.sleep(0.01)

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def print_welcome_message(self):
        pass


def create(scr_queue, debug):
    if debug:
        from screendbg import ScreenDebug
        scr = ScreenDebug(scr_queue)
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger().handlers = []
        logging.getLogger().addHandler(scr)
        logging.debug("Screen initialized.")
        return scr
    else:
        raise NotImplementedError()
