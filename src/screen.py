from abc import abstractmethod
import threading

class Screen(threading.Thread):

    @abstractmethod
    def run(self):
        pass

def create(debug):
    from screendbg import ScreenDebug
    return ScreenDebug()
