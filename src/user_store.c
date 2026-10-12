#include "user_store.h"

#include <string.h>

void user_store_init(UserStore *store)
{
    if (store != NULL) { memset(store, 0, sizeof *store); store->next_id = 1001U; }
}

bool user_store_add(UserStore *store, User *user)
{
    if (store == NULL || user == NULL || store->count >= USER_STORE_MAX_USERS ||
        store->next_id == 0 || !user_validate(user)) return false;
    for (size_t i = 0; i < store->count; ++i)
        if (strcmp(store->users[i].username, user->username) == 0) return false;
    user->id = store->next_id++;
    user->active = true;
    store->users[store->count++] = *user;
    return true;
}

User *user_store_find_by_id(UserStore *store, unsigned int id)
{
    if (store == NULL || id == 0) return NULL;
    for (size_t i = 0; i < store->count; ++i) if (store->users[i].id == id) return &store->users[i];
    return NULL;
}

const User *user_store_find_by_id_const(const UserStore *store, unsigned int id)
{
    if (store == NULL || id == 0) return NULL;
    for (size_t i = 0; i < store->count; ++i) if (store->users[i].id == id) return &store->users[i];
    return NULL;
}

bool user_store_deactivate(UserStore *store, unsigned int id)
{
    User *user = user_store_find_by_id(store, id);
    return user != NULL && user_set_active(user, false);
}

bool user_store_reactivate(UserStore *store, unsigned int id)
{
    User *user = user_store_find_by_id(store, id);
    return user != NULL && user_set_active(user, true);
}

size_t user_store_list_active(const UserStore *store, User *out, size_t capacity)
{
    if (store == NULL || (capacity > 0 && out == NULL)) return 0;
    size_t total = 0;
    for (size_t i = 0; i < store->count; ++i) {
        if (!store->users[i].active) continue;
        if (total < capacity) out[total] = store->users[i];
        ++total;
    }
    return total;
}
