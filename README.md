# podcastradio
A car radio that plays podcasts, using Raspberry Pi Zero.

# v1

![design](v1.jpg)
(TODO - draw: audio USB dongle, extra pushbuttons?)

Shopping list:

- Devices
  - ~Raspberry Pi Zero~
  - USB audio card
  - ~USB A to micro B~
  - ~USB A to anything~
- Components
  - ~Power switch~
  - 2 infinite knobs
  - ~screen~
  - ~status leds~
  - ~USB input A~

# v2

![design](v2.jpg)

# Software design:

- Thread based. Threads communicate over synchronized queues.
- Threads:
  1. Main thread 
     - read config file
     - read input from user
     - manages everything
     - check for updates on config file
     - database module (saved every 5 seconds)
  2. Screen thread - manages screen and leds
     - on debugging, draw everything on the screen
  3. Download thread - download episodes on the background
  4. Player thread - plays mp3
- Additional execution: ftp
- Libraries necessary:
  - cpptoml
  - curses (debuggin)
  - wiringpi (Raspberry Pi)
  - sqlite
  - libcurl
  - fmod
