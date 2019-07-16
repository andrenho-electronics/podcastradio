OBJ = pr_download.o config.o db.o fs.o

CFLAGS = -Wall -Wextra `pkg-config --cflags sqlite3 libcurl`
LIBS = -fPIC -L/usr/local/lib `pkg-config --libs sqlite3 libcurl` -ltoml

pr_download: ${OBJ}
	gcc -o $@ ${OBJ} ${CFLAGS} ${LIBS}

debug: CFLAGS += -O0 -ggdb
debug: LIBS += -O0 -ggdb
debug: pr_download

clean:
	rm -f ${OBJ} pr_download
