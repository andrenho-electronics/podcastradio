#ifndef SCREEN_DEBUG_HH_
#define SCREEN_DEBUG_HH_

#include "screen/screen.hh"

#include <memory>

#include <curses.h>

struct window_destroyer {
    void operator()(WINDOW* w) const { if (w) delwin(w); }
};

class ScreenDebug : public Screen {
public:
    ScreenDebug();
    ~ScreenDebug();

    void print_welcome_message() const override;

private:
    void redraw_everything();
    void create_windows();
    void draw_boxes() const;

    std::unique_ptr<WINDOW, window_destroyer> panel  { nullptr },
                                              screen { nullptr },
                                              logs   { nullptr };
};

#endif
