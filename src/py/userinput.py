from abc import ABC, abstractmethod

class UserInput(ABC):

    @abstractmethod
    def get_event(self, data):
        pass

def create(debug):
    from userinputdbg import UserInputDebug
    return UserInputDebug()
