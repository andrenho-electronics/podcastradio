#include "mgr/manager.hh"

#include <memory>
using namespace std;

#include "globals.hh"
#include "screen/screenevent.hh"

Manager::Manager()
{
    screen_queue.push(make_unique<WelcomeScreen>());
}
