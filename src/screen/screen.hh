#ifndef SCREEN_HH_
#define SCREEN_HH_

#include <memory>

class Screen {
public:
    virtual ~Screen() {}
    static std::unique_ptr<Screen> create();

    void run();
    virtual void print_welcome_message() const = 0;
};

#endif
