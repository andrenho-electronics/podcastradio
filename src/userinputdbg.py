import curses
import sys

from userinput import UserInput

class UserInputDebug(UserInput):
    
    def __init__(self):
        pass

    def get_event(self, stdscr):
        ch = stdscr.getch()
        if ch == ord('q'):
            curses.endwin()
            sys.exit()

    def __del__(self):
        pass
