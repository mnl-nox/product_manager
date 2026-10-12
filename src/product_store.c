#include "product_store.h"

#include <string.h>

void product_store_init(ProductStore *store)
{
    if (store != NULL) {
        memset(store, 0, sizeof *store);
        store->next_id = 1U;
    }
}

bool product_store_add(ProductStore *store, Product *product)
{
    if (store == NULL || product == NULL || store->count >= PRODUCT_STORE_MAX_ITEMS) {
        return false;
    }

    product->id = store->next_id == 0 ? 1U : store->next_id++;
    product->active = true;

    if (!product_validate(product)) {
        return false;
    }

    store->items[store->count++] = *product;
    return true;
}

Product *product_store_find_by_id(ProductStore *store, unsigned int id)
{
    if (store == NULL || id == 0) {
        return NULL;
    }

    for (size_t i = 0; i < store->count; ++i) {
        if (store->items[i].id == id) {
            return &store->items[i];
        }
    }

    return NULL;
}

const Product *product_store_find_by_id_const(const ProductStore *store, unsigned int id)
{
    if (store == NULL || id == 0) {
        return NULL;
    }

    for (size_t i = 0; i < store->count; ++i) {
        if (store->items[i].id == id) {
            return &store->items[i];
        }
    }

    return NULL;
}

bool product_store_deactivate(ProductStore *store, unsigned int id)
{
    Product *product = product_store_find_by_id(store, id);
    return product != NULL && product_set_active(product, false);
}

bool product_store_reactivate(ProductStore *store, unsigned int id)
{
    Product *product = product_store_find_by_id(store, id);
    return product != NULL && product_set_active(product, true);
}

size_t product_store_list_by_user(const ProductStore *store, unsigned int user_id, Product *out, size_t capacity)
{
    if (store == NULL || (capacity > 0U && out == NULL)) {
        return 0U;
    }

    size_t total = 0U;
    for (size_t i = 0; i < store->count; ++i) {
        if (store->items[i].user_id != user_id) {
            continue;
        }

        if (total < capacity) {
            out[total] = store->items[i];
        }
        ++total;
    }

    return total;
}

size_t product_store_list_active_by_user(const ProductStore *store, unsigned int user_id, Product *out, size_t capacity)
{
    if (store == NULL || (capacity > 0U && out == NULL)) {
        return 0U;
    }

    size_t total = 0U;
    for (size_t i = 0; i < store->count; ++i) {
        if (store->items[i].user_id != user_id || !store->items[i].active) {
            continue;
        }

        if (total < capacity) {
            out[total] = store->items[i];
        }
        ++total;
    }

    return total;
}
