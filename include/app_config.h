#ifndef APP_CONFIG_H
#define APP_CONFIG_H

#include <stdbool.h>
#include <stddef.h>

#define APP_CONFIG_PATH "config.ini"
#define APP_CONFIG_DATA_FILE_MAX 256

typedef struct {
    char data_file[APP_CONFIG_DATA_FILE_MAX];
    unsigned int first_user_id;
    size_t max_users;
} AppConfig;

void app_config_defaults(AppConfig *config);
bool app_config_load(AppConfig *config, const char *path);

#endif
