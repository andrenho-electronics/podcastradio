#include "db.h"

#include <stdlib.h>

typedef struct Database {
} Database;

Database*
db_init(const char* path)
{
    (void) path;
    return NULL;
}

void
db_close(Database* db)
{
    (void) db;
}

char*
db_reserve_next_file(Database* db)
{
    (void) db;
    return NULL;
}

void
db_mark_as_downloaded(Database* db, char* url, char* filename)
{
    (void) url; (void) filename;
    (void) db;
}

void
db_register_error(Database* db, char* url, char* error_desc)
{
    (void) url; (void) error_desc;
    (void) db;
}

void
db_mark_as_removed(Database* db, char* filename)
{
    (void) filename;
    (void) db;
}

char*
db_next_file_to_remove(Database* db)
{
    (void) db;
    return NULL;
}
