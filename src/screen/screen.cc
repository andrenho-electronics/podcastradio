#include "screen/screen.hh"

#include <memory>
#include <thread>
using namespace std;

#include "globals.hh"
#include "screen/screen_debug.hh"

std::unique_ptr<Screen>
Screen::create() { 
#ifdef DEBUG
    return std::make_unique<ScreenDebug>();
#else
    return std::make_unique<ScreenRPI>();
#endif
}

void
Screen::run()
{
    for (;;) {
        screen_queue.execute(*this);
        this_thread::sleep_for(10ms);
    }
}
