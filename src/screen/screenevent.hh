#ifndef SCREENEVENT_HH_
#define SCREENEVENT_HH_

#include "screen.hh"

class ScreenEvent {
public:
    virtual ~ScreenEvent() {}
    virtual void execute(Screen& screen) = 0;
};

class WelcomeScreen : public ScreenEvent {
    void execute(Screen& screen) override {
        screen.print_welcome_message();
    }
};

#endif
