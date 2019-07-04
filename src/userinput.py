from abc import abstractmethod

class UserInput:

    @abstractmethod
    def get_event(self):
        pass

def create(debug):
    from userinputdbg import UserInputDebug
    return UserInputDebug()
