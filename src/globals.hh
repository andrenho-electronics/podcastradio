#ifndef GLOBALS_HH_
#define GLOBALS_HH_

#include "screen/screenevent.hh"
#include "util/config.hh"
#include "util/log.hh"
#include "util/syncqueue.hh"

extern Config                   cfg;
extern SyncQueue<ScreenEvent>   screen_queue;
/*
extern SyncQueue<MainEvent>     main_queue;
extern SyncQueue<DownloadEvent> dl_queue;
extern SyncQueue<PlayerEvent>   player_queue;
*/

#endif
