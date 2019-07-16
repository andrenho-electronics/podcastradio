OBJ = pr_download.o config.o db.o fs.o

CFLAGS = -Wall -Wextra
LIBS = -fPIC

pr_download: ${OBJ}
	gcc -o $@ ${OBJ} ${CFLAGS} ${LIBS}

debug: CFLAGS += -O0 -ggdb
debug: pr_download

clean:
	rm -f ${OBJ} pr_download
