#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "config.h"

int tests_run = 0;

int test_config()
{
    assert(config_load_file("configerror.ini"));

    assert(config_load_file("configempty.ini"));
    assert(0 == strcmp(config.database_file, "/var/db/podcastradio/podcastradio.db"));
    assert(0 == strcmp(config.download_path, "/var/db/podcastradio/download"));

    assert(config_load());
    assert(0 == strcmp(config.database_file, "podcastradio.db"));
    assert(0 == strcmp(config.download_path, "download"));
    
    return EXIT_SUCCESS;
}

int main()
{
    return test_config();
}
