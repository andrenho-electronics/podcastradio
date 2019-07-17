OBJ = config.o db.o fs.o

CFLAGS = -std=c11 -D_GNU_SOURCE -Wall -Wextra `pkg-config --cflags sqlite3 libcurl` -fdiagnostics-color=always
LIBS = -fPIC -L/usr/local/lib `pkg-config --libs sqlite3 libcurl`

CFLAGS += -fno-stack-protector

# main executable

pr_download: pr_download.o ${OBJ}
	gcc -o $@ pr_download.o ${OBJ} ${CFLAGS} ${LIBS}

# debugging version

debug: CFLAGS += -O0 -ggdb
debug: LIBS += -O0 -ggdb
debug: pr_download

# unit testing

test_pr_download: CFLAGS += -O0 -ggdb
test_pr_download: LIBS += -O0 -ggdb
test_pr_download: tests.o ${OBJ}
	gcc -o $@ tests.o ${OBJ} ${CFLAGS} ${LIBS}

check: test_pr_download
	valgrind --leak-check=full --show-leak-kinds=all ./test_pr_download

# clean up

clean:
	rm -f ${OBJ} pr_download test_pr_download

