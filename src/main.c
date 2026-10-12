#include "app_config.h"
#include "menu.h"
#include "product_store.h"
#include "user_store.h"

#include <stdio.h>

int main(void)
{
    AppConfig config;
    UserStore user_store;
    ProductStore product_store;

    if (!app_config_load(&config, APP_CONFIG_PATH)) {
        fprintf(stderr, "Aviso: não foi possível ler %s; usando valores padrão.\n", APP_CONFIG_PATH);
        app_config_defaults(&config);
    }

    user_store_init(&user_store);
    if (config.first_user_id > 0U) {
        user_store.next_id = config.first_user_id;
    }
    product_store_init(&product_store);
    return menu_run(&user_store, &product_store);
}
