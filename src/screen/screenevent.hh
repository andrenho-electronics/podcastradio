#ifndef SCREENEVENT_HH_
#define SCREENEVENT_HH_

#include <string>

#include "screen.hh"

class ScreenEvent {
public:
    virtual ~ScreenEvent() {}
    virtual void execute(Screen& screen) = 0;
};


class LogMessage : public ScreenEvent {
public:
    LogMessage(std::string text) : text(text) {}

    void execute(Screen& screen) override {
        screen.print_log_message(text);
    }

private:
    std::string text;
};


class WelcomeScreen : public ScreenEvent {
    void execute(Screen& screen) override {
        screen.print_welcome_message();
    }
};

#endif
