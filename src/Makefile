OBJ = main.o

all:
	$(error Not implemented.)

debug: CPPFLAGS ?= -DDEBUG -O0 -ggdb
debug: $(OBJ)
	$(CXX) -o prdebug $(OBJ) $(LIBS)

clean:
	rm -f podcastradio prdebug **/*.o
