#include <assert.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "config.h"

int tests_run = 0;

int test_config()
{
    Config* config = config_load_file("configerror.ini");
    assert(config);
    config_free(config);

    config = config_load_file("configempty.ini");
    assert(config);
    assert(0 == strcmp(config->database_file, "/var/db/podcastradio/podcastradio.db"));
    assert(0 == strcmp(config->download_path, "/var/db/podcastradio/download"));
    config_free(config);

    config = config_load();
    assert(config);
    assert(0 == strcmp(config->database_file, "podcastradio.db"));
    assert(0 == strcmp(config->download_path, "download"));
    config_free(config);
    
    return EXIT_SUCCESS;
}

int main()
{
    int r = test_config();
    if (r == EXIT_SUCCESS)
        printf("ALL TESTS SUCCESSFUL.\n");
    return r;
}
