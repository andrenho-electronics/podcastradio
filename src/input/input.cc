#include "input/input.hh"

#include <memory>
using namespace std;

#include "input/input_debug.hh"

std::unique_ptr<Input>
Input::create() { 
#ifdef DEBUG
    return std::make_unique<InputDebug>();
#else
    return std::make_unique<InputRPI>();
#endif
}
