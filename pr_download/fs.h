#ifndef FS_H_
#define FS_H_

void  fs_init(void);
char* fs_download_file(char* url, char** error_desc);
void  fs_remove_file(char* filename);

#endif
