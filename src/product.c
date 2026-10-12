#include "product.h"

#include <string.h>

void product_init(Product *product)
{
    if (product != NULL) { memset(product, 0, sizeof *product); product->active = true; }
}

bool product_validate(const Product *product)
{
    return product != NULL && product->id > 0 && product->user_id > 0 &&
           product->name[0] != '\0' && product->type[0] != '\0' &&
           memchr(product->name, '\0', sizeof product->name) != NULL &&
           memchr(product->type, '\0', sizeof product->type) != NULL &&
           memchr(product->reference, '\0', sizeof product->reference) != NULL;
}

bool product_set_active(Product *product, bool active)
{
    if (product == NULL || product->id == 0) return false;
    product->active = active;
    return true;
}
