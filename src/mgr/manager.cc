#include "mgr/manager.hh"

#include "globals.hh"
#include "screen/screenevent.hh"

Manager::Manager()
{
    screen_queue.push(WelcomeScreen());
}
