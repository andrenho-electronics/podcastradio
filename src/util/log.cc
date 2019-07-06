#include "util/log.hh"

using namespace std;

#include "globals.hh"

void
log(string text)
{
    screen_queue.push<LogMessage>(text);
}
