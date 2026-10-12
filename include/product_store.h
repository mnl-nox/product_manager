#ifndef PRODUCT_STORE_H
#define PRODUCT_STORE_H

#include <stdbool.h>
#include <stddef.h>

#include "product.h"

#define PRODUCT_STORE_MAX_ITEMS 1024

typedef struct {
    Product items[PRODUCT_STORE_MAX_ITEMS];
    size_t count;
    unsigned int next_id;
} ProductStore;

void product_store_init(ProductStore *store);
bool product_store_add(ProductStore *store, Product *product);
Product *product_store_find_by_id(ProductStore *store, unsigned int id);
const Product *product_store_find_by_id_const(const ProductStore *store, unsigned int id);
bool product_store_deactivate(ProductStore *store, unsigned int id);
bool product_store_reactivate(ProductStore *store, unsigned int id);
size_t product_store_list_by_user(const ProductStore *store, unsigned int user_id, Product *out, size_t capacity);
size_t product_store_list_active_by_user(const ProductStore *store, unsigned int user_id, Product *out, size_t capacity);

#endif
