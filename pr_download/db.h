#ifndef DB_H_
#define DB_H_

void  db_init(const char* path);
char* db_reserve_next_file(void);
void  db_mark_as_downloaded(char* url, char* filename);
void  db_register_error(char* url, char* error_desc); 
void  db_mark_as_removed(char* filename);
char* db_next_file_to_remove(void);
void  db_close(void);

#endif
