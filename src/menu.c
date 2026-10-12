#include "menu.h"

#include "product_store.h"
#include "user_service.h"

#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void clear_input_buffer(void)
{
    int ch;
    while ((ch = getchar()) != '\n' && ch != EOF) {
    }
}

static void trim_newline(char *text)
{
    if (text == NULL) {
        return;
    }

    size_t length = strlen(text);
    while (length > 0U && (text[length - 1U] == '\n' || text[length - 1U] == '\r')) {
        text[length - 1U] = '\0';
        --length;
    }
}

static bool read_line(char *buffer, size_t size, const char *prompt)
{
    if (buffer == NULL || size == 0U) {
        return false;
    }

    if (prompt != NULL) {
        printf("%s", prompt);
        fflush(stdout);
    }

    if (fgets(buffer, (int)size, stdin) == NULL) {
        return false;
    }

    trim_newline(buffer);
    if (buffer[0] == '\0') {
        return false;
    }

    return true;
}

static bool read_optional_line(char *buffer, size_t size, const char *prompt, const char *current_value)
{
    if (buffer == NULL || size == 0U) {
        return false;
    }

    if (current_value != NULL && current_value[0] != '\0') {
        printf("%s [%s]: ", prompt, current_value);
    } else {
        printf("%s: ", prompt);
    }
    fflush(stdout);

    char temporary[256];
    if (fgets(temporary, sizeof temporary, stdin) == NULL) {
        return false;
    }

    trim_newline(temporary);
    if (temporary[0] == '\0') {
        if (current_value != NULL) {
            (void)snprintf(buffer, size, "%s", current_value);
            return true;
        }
        buffer[0] = '\0';
        return true;
    }

    (void)snprintf(buffer, size, "%s", temporary);
    return true;
}

static bool read_unsigned(unsigned int *value, const char *prompt)
{
    if (value == NULL) {
        return false;
    }

    char buffer[32];
    if (!read_line(buffer, sizeof buffer, prompt)) {
        return false;
    }

    errno = 0;
    char *end = NULL;
    unsigned long parsed = strtoul(buffer, &end, 10);
    if (errno != 0 || buffer[0] == '\0' || *end != '\0' || parsed > UINT_MAX) {
        puts("Valor inválido.");
        return false;
    }

    *value = (unsigned int)parsed;
    return true;
}

static void print_user_banner(const User *user)
{
    if (user == NULL) {
        return;
    }

    printf("ID: %u\n", user->id);
    printf("Nome: %s\n", user->name);
    printf("Telefone: %s\n", user->phone);
    printf("Username: %s\n", user->username);
    printf("Status: %s\n", user->active ? "ATIVO" : "INATIVO");
}

static void print_user_list(const User *users, size_t count)
{
    if (count == 0U) {
        puts("Nenhum usuário encontrado.");
        return;
    }

    puts("ID    Nome                 Telefone            Username");
    puts("------------------------------------------------------");
    for (size_t i = 0U; i < count; ++i) {
        printf("%4u  %-20s %-18s %s\n",
               users[i].id,
               users[i].name,
               users[i].phone,
               users[i].username);
    }
}

static void print_product_list(const Product *products, size_t count)
{
    if (count == 0U) {
        puts("Nenhum item vinculado.");
        return;
    }

    puts("ID    Nome                 Tipo          Referência");
    puts("------------------------------------------------------");
    for (size_t i = 0U; i < count; ++i) {
        printf("%4u  %-20s %-12s %s\n",
               products[i].id,
               products[i].name,
               products[i].type,
               products[i].reference);
    }
}

static void handle_list_active_users(UserStore *store)
{
    User users[USER_STORE_MAX_USERS];
    size_t count = user_store_list_active(store, users, USER_STORE_MAX_USERS);
    print_user_list(users, count);
}

static void handle_list_inactive_users(UserStore *store)
{
    if (store == NULL) {
        return;
    }

    bool any = false;
    for (size_t i = 0U; i < store->count; ++i) {
        if (!store->users[i].active) {
            if (!any) {
                puts("Usuários inativos:");
                any = true;
            }
            print_user_banner(&store->users[i]);
            puts("-----------------------------");
        }
    }

    if (!any) {
        puts("Nenhum usuário inativo.");
    }
}

static void handle_create_user(UserStore *store)
{
    User user;
    char name[USER_NAME_MAX];
    char phone[USER_PHONE_MAX];
    char username[USER_LOGIN_MAX];

    user_init(&user);

    if (!read_line(name, sizeof name, "Nome: ") || !read_line(phone, sizeof phone, "Telefone: ") ||
        !read_line(username, sizeof username, "Username: ")) {
        puts("Entrada inválida. Cadastro cancelado.");
        return;
    }

    (void)snprintf(user.name, sizeof user.name, "%s", name);
    (void)snprintf(user.phone, sizeof user.phone, "%s", phone);
    (void)snprintf(user.username, sizeof user.username, "%s", username);

    if (!user_validate(&user)) {
        puts("Dados inválidos para cadastro.");
        return;
    }

    unsigned int created_id = 0U;
    if (user_service_create(store, &user, &created_id)) {
        printf("Usuário criado com sucesso. ID: %u\n", created_id);
    } else {
        puts("Não foi possível criar o usuário. Verifique os dados e a disponibilidade de usuário.");
    }
}

static void handle_find_user(UserStore *store)
{
    unsigned int user_id = 0U;
    if (!read_unsigned(&user_id, "ID do usuário: ")) {
        return;
    }

    User *user = user_service_find(store, user_id);
    if (user == NULL) {
        puts("Usuário não encontrado.");
        return;
    }

    print_user_banner(user);
}

static void handle_update_user(UserStore *store)
{
    unsigned int user_id = 0U;
    if (!read_unsigned(&user_id, "ID do usuário: ")) {
        return;
    }

    User *user = user_service_find(store, user_id);
    if (user == NULL) {
        puts("Usuário não encontrado.");
        return;
    }

    User updated = *user;
    char name[USER_NAME_MAX];
    char phone[USER_PHONE_MAX];
    char username[USER_LOGIN_MAX];

    if (!read_optional_line(name, sizeof name, "Novo nome", user->name) ||
        !read_optional_line(phone, sizeof phone, "Novo telefone", user->phone) ||
        !read_optional_line(username, sizeof username, "Novo username", user->username)) {
        puts("Falha ao ler os dados de atualização.");
        return;
    }

    if (name[0] != '\0') {
        (void)snprintf(updated.name, sizeof updated.name, "%s", name);
    }
    if (phone[0] != '\0') {
        (void)snprintf(updated.phone, sizeof updated.phone, "%s", phone);
    }
    if (username[0] != '\0') {
        (void)snprintf(updated.username, sizeof updated.username, "%s", username);
    }

    if (!user_service_update(store, user_id, &updated)) {
        puts("Não foi possível atualizar o cadastro. Verifique os dados e o username.");
        return;
    }

    puts("Cadastro atualizado com sucesso.");
}

static void handle_deactivate_user(UserStore *store)
{
    unsigned int user_id = 0U;
    if (!read_unsigned(&user_id, "ID do usuário: ")) {
        return;
    }

    User *user = user_service_find(store, user_id);
    if (user == NULL) {
        puts("Usuário não encontrado.");
        return;
    }

    printf("Usuário encontrado:\n");
    print_user_banner(user);
    puts("Desativar este usuário? [S/N]");

    int choice = getchar();
    clear_input_buffer();
    if (choice == 'S' || choice == 's') {
        if (user_service_deactivate(store, user_id)) {
            puts("Usuário desativado com sucesso.");
        } else {
            puts("Não foi possível desativar o usuário.");
        }
        return;
    }

    puts("Operação cancelada.");
}

static void handle_reactivate_user(UserStore *store)
{
    unsigned int user_id = 0U;
    if (!read_unsigned(&user_id, "ID do usuário: ")) {
        return;
    }

    User *user = user_service_find(store, user_id);
    if (user == NULL) {
        puts("Usuário não encontrado.");
        return;
    }

    if (user->active) {
        puts("Este usuário já está ativo.");
        return;
    }

    if (user_service_reactivate(store, user_id)) {
        puts("Usuário reativado com sucesso.");
    } else {
        puts("Não foi possível reativar o usuário.");
    }
}

static void handle_manage_products(UserStore *store, ProductStore *product_store)
{
    if (store == NULL || product_store == NULL) {
        return;
    }

    unsigned int user_id = 0U;
    if (!read_unsigned(&user_id, "ID do usuário: ")) {
        return;
    }

    User *user = user_service_find(store, user_id);
    if (user == NULL) {
        puts("Usuário não encontrado.");
        return;
    }

    for (;;) {
        puts("\nGerenciamento de produtos/ativos/serviços");
        puts("1. Listar itens");
        puts("2. Adicionar item");
        puts("3. Desativar item");
        puts("4. Voltar");

        char option[32];
        if (!read_line(option, sizeof option, "Escolha: ")) {
            puts("Entrada inválida.");
            return;
        }

        switch (option[0]) {
            case '1': {
                Product items[PRODUCT_STORE_MAX_ITEMS];
                size_t count = product_store_list_active_by_user(product_store, user_id, items, PRODUCT_STORE_MAX_ITEMS);
                print_product_list(items, count);
                break;
            }
            case '2': {
                Product product;
                char name[PRODUCT_NAME_MAX];
                char type[PRODUCT_TYPE_MAX];
                char reference[PRODUCT_REFERENCE_MAX];

                product_init(&product);
                if (!read_line(name, sizeof name, "Nome do item: ") || !read_line(type, sizeof type, "Tipo: ") ||
                    !read_line(reference, sizeof reference, "Referência: ")) {
                    puts("Dados do item inválidos.");
                    break;
                }

                (void)snprintf(product.name, sizeof product.name, "%s", name);
                (void)snprintf(product.type, sizeof product.type, "%s", type);
                (void)snprintf(product.reference, sizeof product.reference, "%s", reference);
                product.user_id = user_id;

                if (!product_validate(&product)) {
                    puts("Dados do item inválidos.");
                    break;
                }

                if (product_store_add(product_store, &product)) {
                    printf("Item adicionado com sucesso. ID: %u\n", product.id);
                } else {
                    puts("Não foi possível adicionar o item.");
                }
                break;
            }
            case '3': {
                unsigned int product_id = 0U;
                if (!read_unsigned(&product_id, "ID do item: ")) {
                    break;
                }

                if (product_store_deactivate(product_store, product_id)) {
                    puts("Item desativado com sucesso.");
                } else {
                    puts("Não foi possível desativar o item.");
                }
                break;
            }
            case '4':
                return;
            default:
                puts("Opção inválida.");
                break;
        }
    }
}

void initial_menu(void)
{
    puts("========================================");
    puts("             LOGIN_TERM");
    puts("        Gestão de Usuários");
    puts("========================================");
}

int menu_run(UserStore *store, ProductStore *product_store)
{
    if (store == NULL || product_store == NULL) {
        return 1;
    }

    for (;;) {
        initial_menu();
        puts("1. Listar usuários ativos");
        puts("2. Novo usuário");
        puts("3. Buscar usuário por ID");
        puts("4. Atualizar cadastro");
        puts("5. Desativar usuário");
        puts("6. Reativar usuário");
        puts("7. Produtos / Ativos / Serviços");
        puts("8. Usuários inativos");
        puts("0. Sair");
        puts("----------------------------------------");

        char option[32];
        if (!read_line(option, sizeof option, "Escolha uma opção: ")) {
            puts("Entrada inválida. Tente novamente.");
            clear_input_buffer();
            continue;
        }

        switch (option[0]) {
            case '1':
                handle_list_active_users(store);
                break;
            case '2':
                handle_create_user(store);
                break;
            case '3':
                handle_find_user(store);
                break;
            case '4':
                handle_update_user(store);
                break;
            case '5':
                handle_deactivate_user(store);
                break;
            case '6':
                handle_reactivate_user(store);
                break;
            case '7':
                handle_manage_products(store, product_store);
                break;
            case '8':
                handle_list_inactive_users(store);
                break;
            case '0':
                puts("Encerrando Product Manager.");
                return 0;
            default:
                puts("Opção inválida.");
                break;
        }

        puts("");
    }
}
