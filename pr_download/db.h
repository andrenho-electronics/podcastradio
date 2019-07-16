#ifndef DB_H_
#define DB_H_

char* db_reserve_next_file(void);
void  db_mark_as_downloaded(char* url, char* filename);
void  db_register_error(char* url, char** error_desc); 
void  db_mark_as_removed(char* filename);

#endif
