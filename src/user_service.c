#include "user_service.h"

#include <string.h>

bool user_service_create(UserStore *store, User *user, unsigned int *created_id)
{
    if (!user_store_add(store, user)) return false;
    if (created_id != NULL) *created_id = user->id;
    return true;
}

User *user_service_find(UserStore *store, unsigned int id)
{
    return user_store_find_by_id(store, id);
}

bool user_service_update(UserStore *store, unsigned int id, const User *new_data)
{
    User *current = user_store_find_by_id(store, id);
    if (current == NULL || new_data == NULL) return false;
    User candidate = *new_data;
    candidate.id = id;
    candidate.active = current->active;
    if (!user_validate(&candidate)) return false;
    for (size_t i = 0; i < store->count; ++i)
        if (store->users[i].id != id && strcmp(store->users[i].username, candidate.username) == 0) return false;
    *current = candidate;
    return true;
}

bool user_service_deactivate(UserStore *store, unsigned int id) { return user_store_deactivate(store, id); }
bool user_service_reactivate(UserStore *store, unsigned int id) { return user_store_reactivate(store, id); }
