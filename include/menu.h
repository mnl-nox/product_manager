#ifndef MENU_H
#define MENU_H

#include "product_store.h"
#include "user_store.h"

void initial_menu(void);
int menu_run(UserStore *store, ProductStore *product_store);

#endif // MENU_H
