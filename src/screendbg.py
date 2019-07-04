import curses

from screen import Screen

class ScreenDebug(Screen):
    
    def __init__(self):
        Screen.__init__(self)
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def run(self):
        pass

    def __del__(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
