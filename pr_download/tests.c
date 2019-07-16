#include <stdio.h>
#include <string.h>

#include "config.h"

int tests_run = 0;

#define mu_assert(message, test) do { if (!(test)) return message; } while (0)
#define mu_run_test(test) do { char *message = test(); tests_run++; \
                                if (message) return message; } while (0)

static char* test_config()
{
    mu_assert("config error", !config_load_file("configerror.ini"));

    mu_assert("config empty", config_load_file("configempty.ini"));
    mu_assert("config default database file",
            0 == strcmp(config.database_file, "/var/db/podcastradio/podcastradio.db"));
    mu_assert("config default download path",
            0 == strcmp(config.download_path, "/var/db/podcastradio/download"));

    mu_assert("config default file", config_load());
    mu_assert("config default database file",
            0 == strcmp(config.database_file, "podcastradio.db"));
    mu_assert("config default download path",
            0 == strcmp(config.download_path, "download"));
    
    return 0;
}

static char* all_tests()
{
    mu_run_test(test_config);
    return 0;
}

int main()
{
    char* result = all_tests();
    if (result)
        printf("test failure on: '%s'\n", result);
    else
        printf("ALL TESTS PASSED\n");
    printf("Tests run: %d\n", tests_run);

    return result != NULL;
}
