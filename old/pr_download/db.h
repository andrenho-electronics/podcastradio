#ifndef DB_H_
#define DB_H_

typedef struct Database Database;

Database* db_init(const char* path);
char*     db_reserve_next_file(Database* db);
void      db_mark_as_downloaded(Database* db, char* url, char* filename);
void      db_register_error(Database* db, char* url, char* error_desc); 
void      db_mark_as_removed(Database* db, char* filename);
char*     db_next_file_to_remove(Database* db);
void      db_close(Database* db);

#endif
