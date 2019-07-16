#include "db.h"

#include <stdlib.h>

void
db_init()
{
}

char*
db_reserve_next_file()
{
    return NULL;
}

void
db_mark_as_downloaded(char* url, char* filename)
{
    (void) url; (void) filename;
}

void
db_register_error(char* url, char* error_desc)
{
    (void) url; (void) error_desc;
}

void
db_mark_as_removed(char* filename)
{
    (void) filename;
}

char*
db_next_file_to_remove()
{
    return NULL;
}
