#ifndef INPUT_HH_
#define INPUT_HH_

#include "input/inputevent.hh"

class Input {
public:
    static unique_ptr<Input> create() { return nullptr; }  // TODO
};

#endif
