import curses

from userinput import UserInput

class UserInputDebug(UserInput):
    
    def __init__(self):
        pass

    def get_event(self, stdscr):
        ch = stdscr.getch()

    def __del__(self):
        pass
