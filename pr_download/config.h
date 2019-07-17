#ifndef CONFIG_H_
#define CONFIG_H_

#include <stdbool.h>

typedef struct Config {
    char* database_file;
    char* download_path;
} Config;

extern Config config;

bool config_load(void);
bool config_load_file(char* filename);
void config_free();

#endif
