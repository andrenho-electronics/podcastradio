OBJ = main.o

CPPFLAGS = -I. -std=c++17
LDFLAGS = -lpthread

all:
	$(error Not implemented.)

debug: CPPFLAGS ?= -DDEBUG -O0 -ggdb
debug: $(OBJ)
	$(CXX) -o prdebug $(OBJ) $(LDFLAGS)

clean:
	rm -f podcastradio prdebug **/*.o
