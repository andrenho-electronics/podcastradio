#ifndef INPUT_HH_
#define INPUT_HH_

#include <memory>
#include <optional>

#include "input/inputevent.hh"

class Input {
public:
    static std::unique_ptr<Input> create();

    virtual std::optional<InputEvent> read() const = 0;
};

#endif
