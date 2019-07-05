from abc import abstractmethod, ABC
import threading

class Screen(threading.Thread, ABC):

    @abstractmethod
    def get_data(self):
        return self.data

    @abstractmethod
    def run(self):
        pass

def create(debug):
    from screendbg import ScreenDebug
    return ScreenDebug()
