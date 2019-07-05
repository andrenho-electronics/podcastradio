import queue
from abc import abstractmethod, ABC

class Message(ABC):

    @abstractmethod
    def execute(self, data):
        pass


class SyncQueue(queue.SimpleQueue):

    def __init__(self, klass):
        queue.SimpleQueue.__init__(self)
        if not issubclass(klass, Message):
            raise Exception('Class ' + repr(klass) + ' is not instance of class Message.')
        self.klass = klass

    def put(self, item, block=True, timeout=None):
        if not isinstance(item, self.klass):
            raise Exception('Item ' + repr(item) + ' is not instance of class ' + repr(self.klass))
        return queue.SimpleQueue.put(self, item, block, timeout)

    def execute(self, data):
        while not self.empty():
            obj = self.get_nowait()
            obj.execute(data)
