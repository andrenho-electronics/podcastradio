#include "screen/screen_debug.hh"

#include <curses.h>

ScreenDebug::ScreenDebug()
{
    initscr();
    noecho();
    cbreak();
    keypad(stdscr, 1);
    
    refresh();
    redraw_everything();
}

ScreenDebug::~ScreenDebug()
{
    nocbreak();
    keypad(stdscr, 0);
    endwin();
}

void
ScreenDebug::print_welcome_message() const
{
    mvwaddstr(screen.get(), 2, 5, "Welcome  to");
    mvwaddstr(screen.get(), 4, 10, "PODCAST RADIO");
    wrefresh(screen.get());
}

//----------------------------------------------------

void
ScreenDebug::redraw_everything()
{
    create_windows();
    draw_boxes();
    refresh();
}

void
ScreenDebug::create_windows()
{
    panel.reset(newwin(16, 40, 0, 0));
    screen.reset(newwin(16, 40, 0, 41));
    logs.reset(newwin(LINES - 17, COLS, 17, 0));
}

void
ScreenDebug::draw_boxes() const
{
    box(panel.get(), 0, 0);
    mvwaddstr(panel.get(), 2, 5, "< Volume  >");
    wattron(panel.get(), A_REVERSE); mvwaddstr(panel.get(), 3, 5, "   A S D   "); wattroff(panel.get(), A_REVERSE);
    mvwaddstr(panel.get(), 5, 5, "<  Tuner  >");
    wattron(panel.get(), A_REVERSE); mvwaddstr(panel.get(), 6, 5, "   Z X C   "); wattroff(panel.get(), A_REVERSE);
    mvwaddstr(panel.get(), 8, 5, "[ ] Status 1");
    mvwaddstr(panel.get(), 9, 5, "[ ] Status 2");
    mvwaddstr(panel.get(), 10, 5, "[ ] Status 3");
    wrefresh(panel.get());

    box(screen.get(), 0, 0);
    wrefresh(screen.get());
}
