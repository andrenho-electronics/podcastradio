import curses

from screen import Screen

class ScreenDebug(Screen):
    
    def __init__(self):
        Screen.__init__(self)
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self.stdscr.clear()
        self.stdscr.refresh()
        self.data = self.stdscr

    def get_data(self):
        return self.data

    def run(self):
        pass

    def __del__(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
