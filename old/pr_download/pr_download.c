#include <stdlib.h>
#include <unistd.h>

#include "config.h"
#include "db.h"
#include "fs.h"

int main() {
    Config* config = config_load();
    if (!config)
        return EXIT_FAILURE;

    Database* db = db_init(config->database_file);
    fs_init();

    for (;;) {
        // download files
        char* url = db_reserve_next_file(db);
        if (url) {
            char* error_desc = NULL;
            char* filename = fs_download_file(url, &error_desc);
            if (filename) {
                db_mark_as_downloaded(db, url, filename);
                free(filename);
            } else {
                db_register_error(db, url, error_desc); 
                free(error_desc);
            }
            free(url);
        }

        // remove files
        char* filename = NULL;
        while ((filename = db_next_file_to_remove(db))) {
            fs_remove_file(filename);
            db_mark_as_removed(db, filename);
            free(filename);
        }

        // wait
        sleep(1);
    }
}

// vim: ts=4:sw=4:sts=4:expandtab
