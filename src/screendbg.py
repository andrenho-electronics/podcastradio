import curses
import logging

from screen import Screen

class ScreenDebug(Screen, logging.Handler):
    
    def __init__(self):
        Screen.__init__(self)
        logging.Handler.__init__(self, 'DEBUG')
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        #curses.curs_set(False)
        self.stdscr.keypad(True)
        self.__redraw_everything()

    def get_data(self):
        return self.stdscr

    def run(self):
        pass
    
    def emit(self, record):
        self.logs_text.addstr(record.getMessage() + "\n")
        self.logs_text.refresh()

    def __del__(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    ################################################

    def __create_windows(self):
        self.front = curses.newwin(16, 22, 0, 0)
        self.leds = curses.newwin(16, curses.COLS - 22 - 40, 0, 22)
        self.screen = curses.newwin(16, 40, 0, curses.COLS - 40)
        self.logs = curses.newwin(curses.LINES - 16, curses.COLS, 16, 0)
        self.logs_text = curses.newwin(curses.LINES - 18, curses.COLS - 2, 17, 1)
        self.logs_text.idlok(True)
        self.logs_text.scrollok(True)

    def __redraw_everything(self):
        self.stdscr.refresh()
        self.__create_windows()
        self.__draw_boxes()
        self.stdscr.refresh()

    def __draw_boxes(self):
        self.front.box()
        self.__write_front()
        self.__write_leds()
        self.screen.box()
        self.logs.box()
        self.front.refresh()
        self.screen.refresh()
        self.leds.refresh()
        self.logs.refresh()

    def __write_front(self):
        f = self.front
        f.addstr(2, 5, "< Volume  >")
        f.addstr(3, 5, "   A S D   ", curses.A_REVERSE)
        f.addstr(5, 5, "<  Tuner  >")
        f.addstr(6, 5, "   Z X C   ", curses.A_REVERSE)

    def __write_leds(self):
        f = self.leds
        f.addstr(3, 2, "[ ] Status 1")
        f.addstr(4, 2, "[ ] Status 2")
        f.addstr(5, 2, "[ ] Status 3")
