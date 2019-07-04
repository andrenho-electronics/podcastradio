#ifndef INPUT_HH_
#define INPUT_HH_

#include <optional>

#include "input/inputevent.hh"

class Input {
public:
    static unique_ptr<Input> create() { return nullptr; }  // TODO

    virtual std::optional<InputEvent> read() const = 0;
};

#endif
