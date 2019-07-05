#include "input/input_debug.hh"

#include <cstdlib>

#include <curses.h>

std::optional<InputEvent> 
InputDebug::read() const {
    int ch = getch();
    switch (ch) {
        case 'q':
            nocbreak();
            keypad(stdscr, 0);
            endwin();
            exit(0);
    }
    return {};
}
