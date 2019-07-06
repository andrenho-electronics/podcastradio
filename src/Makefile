OBJ = main.o 				\
	  input/input.o 		\
	  input/input_debug.o	\
	  mgr/manager.o			\
	  screen/screen.o		\
	  screen/screen_debug.o

LIBS=ncurses

CPPFLAGS = -I. -std=c++17 -Wall -Wextra `pkg-config --cflags ${LIBS}`
LDFLAGS = -lpthread `pkg-config --libs ${LIBS}`

all:
	$(error Not implemented.)

debug: CPPFLAGS += -DDEBUG -O0 -ggdb
debug: ${OBJ}
	${CXX} -o prdebug ${OBJ} ${LDFLAGS}

clean:
	rm -f podcastradio prdebug **/*.o
