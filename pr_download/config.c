#include "config.h"

#include <stdlib.h>
#include <string.h>

#include "toml.h"

Config config = (Config) {
    .database_file = NULL,
    .download_path = NULL,
};

bool
config_load()
{
    return config_load_file("podcastradio.ini");
}

bool
config_load_file(char* filename)
{
    // reset config
    free(config.database_file);
    config.database_file = strdup("/var/db/podcastradio/podcastradio.db");
    free(config.download_path);
    config.download_path = strdup("/var/db/podcastradio/download");

    // open file
    FILE* fp = fopen(filename, "r");
    if (!fp) {
        perror("fopen");
        return false;
    }

    // parse file
    char errbuf[200];
    toml_table_t* conf = toml_parse_file(fp, errbuf, sizeof(errbuf));
    fclose(fp);
    if (!conf) {
        fprintf(stderr, "ERROR: %s\n", errbuf);
        return false;
    }

    // find config section
    toml_table_t* config_section = toml_table_in(conf, "config");
    if (!config_section)
        return true;  // use defaults

    // load keys
    const char* database_file = toml_raw_in(config_section, "database_file");
    if (database_file) {
        free(config.database_file);
        config.database_file = strdup(database_file);
    }

    const char* download_path = toml_raw_in(config_section, "download_path");
    if (download_path) {
        free(config.download_path);
        config.download_path = strdup(download_path);
    }

    // free everything
    toml_free(conf);

    return true;
}
