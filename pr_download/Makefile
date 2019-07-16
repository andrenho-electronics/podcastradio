OBJ = pr_download.o

CFLAGS = -Wall -Wextra
LIBS = 

pr_download: ${OBJ}
	gcc -o $@ $< ${CFLAGS} ${LIBS}

debug: CFLAGS += -O0 -ggdb
debug: pr_download

clean:
	rm ${OBJ} pr_download
