#ifndef INPUT_DEBUG_HH_
#define INPUT_DEBUG_HH_

#include "input/input.hh"

class InputDebug : public Input {
public:
    std::optional<InputEvent> read() const override;
};

#endif
