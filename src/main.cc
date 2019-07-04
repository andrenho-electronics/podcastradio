#include <chrono>
#include <iostream>
#include <memory>
#include <optional>
#include <thread>
using namespace std;
using namespace std::chrono;

#include "input/input.hh"
#include "mgr/manager.hh"
#include "download/download.hh"
#include "player/player.hh"
#include "screen/screen.hh"
#include "util/config.hh"
#include "util/log.hh"
#include "util/syncqueue.hh"

Config                   cfg;
Log                      logs;
/*
SyncQueue<MainEvent>     main_queue;
SyncQueue<ScreenEvent>   screen_queue;
SyncQueue<DownloadEvent> dl_queue;
SyncQueue<PlayerEvent>   player_queue;
*/

int main()
{
    cfg.auto_load_on_change();

    auto last_update = steady_clock::now();
    auto input = Input::create();
    Manager mgr;

    // initialize threads
    thread thread_screen([]{ Screen::create()->run(); });
    thread thread_download([]{ Download().run(); });
    thread thread_player([]{ Player().run(); });

    // main loop
    for (;;) {

        // read and act on inputs
        optional<InputEvent> event = input->read();
        if (event.has_value())
            mgr.do_event(*event);
        
        // every one second
        if (steady_clock::now() >= last_update + 1s) {
            mgr.save_database();
            last_update = steady_clock::now();
        }
    }
}
