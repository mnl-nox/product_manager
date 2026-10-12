#include "user.h"

#include <string.h>

void user_init(User *user)
{
    if (user != NULL) { memset(user, 0, sizeof *user); user->active = true; }
}

bool user_validate(const User *user)
{
    return user != NULL && user->name[0] != '\0' &&
           user->phone[0] != '\0' && user->username[0] != '\0' &&
           memchr(user->name, '\0', sizeof user->name) != NULL &&
           memchr(user->phone, '\0', sizeof user->phone) != NULL &&
           memchr(user->username, '\0', sizeof user->username) != NULL;
}

bool user_set_active(User *user, bool active)
{
    if (user == NULL || user->id == 0) return false;
    user->active = active;
    return true;
}
