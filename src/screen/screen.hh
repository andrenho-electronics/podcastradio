#ifndef SCREEN_HH_
#define SCREEN_HH_

class Screen {
public:
    static unique_ptr<Screen> create() { return nullptr; }  // TODO

    virtual void run() = 0;
};

#endif
