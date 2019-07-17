#include "config.h"

#include <regex.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

Config*
config_load()
{
    return config_load_file("podcastradio.ini");
}

Config*
config_load_file(char* filename)
{
    Config* config = NULL;

    // setup regexes
    regex_t section, kv;
    if(regcomp(&section, "^\\s*\\[(.+?)\\]\\s*$", REG_EXTENDED) != 0) {
        perror("regcomp");
        exit(1);
    }
    if(regcomp(&kv, "^\\s*([^ ]+?)\\s*=\\s*([^ ]+?)\\s*", REG_EXTENDED | REG_NEWLINE) != 0) {
        perror("regcomp");
        exit(1);
    }

    // open file
    FILE* fp = fopen(filename, "r");
    if (!fp) {
        perror("fopen");
        goto end;
    }
    
    // create config
    config = calloc(1, sizeof(Config));

    // read line by line
    char current_section[50];
    char* line = NULL;
    size_t len = 0;
    while (getline(&line, &len, fp) != -1) {
        regmatch_t match[3];
        if (regexec(&section, line, 3, match, 0) == 0) {
            current_section[0] = '\0';
            strncat(current_section, line + match[1].rm_so, match[1].rm_eo - match[1].rm_so);
        } else if (regexec(&kv, line, 3, match, 0) == 0) {
            if (strcmp(current_section, "config") == 0) {
                if (strncmp("database_file", line + match[1].rm_so, match[1].rm_eo - match[1].rm_so) == 0)
                    config->database_file = strndup(line + match[2].rm_so, match[2].rm_eo - match[2].rm_so);
                else if (strncmp("download_path", line + match[1].rm_so, match[1].rm_eo - match[1].rm_so) == 0)
                    config->download_path = strndup(line + match[2].rm_so, match[2].rm_eo - match[2].rm_so);
            }
        }
    }
    free(line);

    // if values not found, setup defaults
    if (!config->database_file)
        config->database_file = strdup("/var/db/podcastradio/podcastradio.db");
    if (!config->download_path)
        config->download_path = strdup("/var/db/podcastradio/download");
    
end:
    regfree(&section);
    regfree(&kv);
    if (fp) fclose(fp);
    return config;
}

void
config_free(Config* config)
{
    free(config->database_file);
    free(config->download_path);
    free(config);
}
