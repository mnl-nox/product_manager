#include "app_config.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void app_config_defaults(AppConfig *config)
{
    if (config == NULL) return;
    (void)snprintf(config->data_file, sizeof config->data_file, "%s", "data/users.csv");
    config->first_user_id = 1001U;
    config->max_users = 1024U;
}

static char *trim(char *text)
{
    while (*text == ' ' || *text == '\t' || *text == '\r' || *text == '\n') ++text;
    size_t length = strlen(text);
    while (length > 0 && (text[length - 1] == ' ' || text[length - 1] == '\t' ||
                          text[length - 1] == '\r' || text[length - 1] == '\n')) {
        text[--length] = '\0';
    }
    return text;
}

bool app_config_load(AppConfig *config, const char *path)
{
    if (config == NULL || path == NULL) return false;
    app_config_defaults(config);
    FILE *file = fopen(path, "r");
    if (file == NULL) return false;
    char line[512];
    bool valid = true;
    while (fgets(line, sizeof line, file) != NULL) {
        char *entry = trim(line);
        if (*entry == '\0' || *entry == '#') continue;
        char *separator = strchr(entry, '=');
        if (separator == NULL) { valid = false; break; }
        *separator++ = '\0';
        char *key = trim(entry), *value = trim(separator);
        char *end = NULL;
        if (strcmp(key, "data_file") == 0) {
            if (*value == '\0' || strlen(value) >= sizeof config->data_file) { valid = false; break; }
            (void)snprintf(config->data_file, sizeof config->data_file, "%s", value);
        } else if (strcmp(key, "first_user_id") == 0) {
            unsigned long parsed = strtoul(value, &end, 10);
            if (*value == '\0' || *end != '\0' || parsed == 0 || parsed > 0xffffffffUL) { valid = false; break; }
            config->first_user_id = (unsigned int)parsed;
        } else if (strcmp(key, "max_users") == 0) {
            unsigned long parsed = strtoul(value, &end, 10);
            if (*value == '\0' || *end != '\0' || parsed == 0 || parsed > 1024U) { valid = false; break; }
            config->max_users = (size_t)parsed;
        } else { valid = false; break; }
    }
    if (ferror(file)) valid = false;
    (void)fclose(file);
    return valid;
}
