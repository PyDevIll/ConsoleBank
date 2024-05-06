# Консольное приложение ВиртуалБанка


# Функции управления транзакциями и параметрами пользователя
def user_restore_from_file(user, file_name):
    try:
        f = open(file_name)
    except IOError:
        return False

    with f:
        # Загрузка данных пользователя
        if (first_line := f.readline().strip()) == '':  # файл пуст
            return False

        user["fio"] = first_line
        user["birth_year"] = f.readline().strip()
        user["pwd"] = f.readline().strip()
        user["balance"] = int(f.readline().strip())
        user["limit"] = int(f.readline().strip())

        user["transactions"] = []
        # Загрузка транзакций
        num = int(f.readline().strip())
        for i in range(num):
            user["transactions"].append({
                "amount": int(f.readline().strip()),
                "comment": f.readline().strip(),
            })

    return True


def user_save_to_file(user, file_name):
    with open(file_name, 'w') as f:
        # Запись данных пользователя
        f.write(user['fio'] + '\n')
        f.write(str(user['birth_year']) + '\n')
        f.write(user['pwd'] + '\n')
        f.write(str(user['balance']) + '\n')
        f.write(str(user['limit']) + '\n')

        # Запись транзакций
        f.write(str(len(user['transactions'])) + '\n')
        for record in user['transactions']:
            f.write(str(record['amount']) + '\n')
            f.write(record['comment'] + '\n')


def user_increase_balance(user, amount):
    if amount <= 0:
        return False

    if user["limit"] > 0:
        if (user["balance"] + amount) <= user["limit"]:
            user["balance"] += amount
            return True
        else:
            return False
    else:       # Если лимит не задан
        user["balance"] += amount
        return True


# Функции управления приложением
def op_account_create(user):
    print("     -Создание аккаунта-")
    user["fio"] = input("Введите ФИО: ")
    user["balance"] = 0
    if (year := get_number("Введите год рождения (ГГГГ): ")) is None:
        return False

    user["birth_year"] = year
    print(f"Создан аккаунт: {user['fio']} ({2024 - user['birth_year']} лет)")
    user["pwd"] = input("Создайте пароль: ")
    print("Аккаунт успешно зарегистрирован!")
    print()
    return True


def op_balance_deposit(user):
    print("     -Пополнение баланса-")
    if (amount := get_number("Введите сумму пополнения: ")) is None:
        return False

    if user_increase_balance(user, amount):
        print("Счет успешно пополнен на", amount, "!")
        return True

    print("Счет не может быть пополнен на такую сумму (", amount, ")")
    return False


def op_balance_withdraw(user):
    print("     -Снятие денег-")
    pwd = input("Введите пароль: ")
    if pwd != user["pwd"]:
        print("Пароль неверен!")
        return False
    print(f"Ваш баланс: {user['balance']} руб.")
    if (amount := get_number("Введите сумму для снятия: ")) is None:
        return False
    if amount <= 0:
        return False

    if user["balance"] >= amount:
        user["balance"] -= amount
        print(f"Снятие успешно завершено! Ваш баланс: {user['balance']} руб.")
        return True

    print("На счете недостаточно средств")
    return False


def op_balance_show(user):
    print("   -Отображение баланса-")
    pwd = input("Введите пароль: ")
    if pwd == user["pwd"]:
        print(f"Ваш баланс: {user['balance']} руб.")
        return True

    print("Пароль неверен!")
    return False


def op_transactions_add(user):
    print("  -Выставление ожидаемого пополнения-\n")
    if (amount := get_number("Сумма будущего пополнения: ")) is None:
        return False
    if amount <= 0:
        return False

    comment = input("Назначение: ")
    user["transactions"].append({
        "amount": amount,
        "comment": comment
    })
    print("Пополнение поставлено в очередь.\n")
    print("Ожидаемых пополнений в очереди: ", len(user["transactions"]))
    return True


def op_set_limit(user):
    print("     -Выставление лимита-\n")
    print(f"Текущее значение лимита: {user['limit']} руб.")
    if (new_limit := get_number("Введите новое значение лимита: ")) is None:
        return False
    if new_limit < 0:
        print("Лимит не может быть меньше нуля!")
        return False
    user["limit"] = new_limit
    if new_limit == 0:
        print("Лимит снят.")
    else:
        print("Лимит изменен.")
    return True


def op_transactons_apply(user):
    print("     -Применение транзакций-\n")
    rejected = []
    for record in user["transactions"]:
        print(f"Транзакция \"{record['comment']}\" на сумму {record['amount']} руб. ", end="")
        if user_increase_balance(user, record["amount"]):
            print("успешно применена.")
        else:
            print("не может быть применена.")
            rejected.append(record)
    user["transactions"] = rejected
    print('_' * 30)


def op_transaction_stats(user):
    stats = {}
    for record in user["transactions"]:
        stats[record["amount"]] = stats.get(record["amount"], 0) + 1

    print("   -Статистика ожидаемых пополнений-\n")
    for amount, count in stats.items():
        print(" " * (7 - len(str(amount))), f"{amount} руб:\t {count} платеж(а)")
    print('_' * 30)


def transactions_by_filter(user, min_amount=0):
    for record in user["transactions"]:
        if record["amount"] >= min_amount:
            yield record


def op_transactions_show(user):
    print(" -Просмотр ожидаемых пополнений по фильтру-\n")
    min_amount = get_number('Введите минимальный размер (ENTER - не фильтровать): ', 0)
    if min_amount == 0: print('Фильтр отключен')
    print()
    for record in transactions_by_filter(user, min_amount):
        print(" " * (7 - len(str(record['amount']))), f"{record['amount']} руб:\t \"{record['comment']}\"")
    print('_' * 30)


def op_user_restore(user, file_name):
    print("Введите \"да\", чтобы восстановить данные из файла: ", end="")
    answer = input().lower()
    to_restore = ((answer == "да") or (answer == "lf"))
    if not to_restore:
        print("Вы отказались от восстановления данных")
        return

    print("Начато восстановление данных...")
    if user_restore_from_file(user, file_name):
        print("Данные восстановлены")
    else:
        print("Не удалось восстановить данные (файл пуст или не существует)")
        print("Программа не может продолжать работу(. До свидания")
        exit()


def get_number(prompt, default=None):
    # returns integer, or default otherwise
    try:
        return int(input(prompt))
    except ValueError:
        # Если значение по умолчанию не предусмотрено, значит ошибка ввода
        if default is None:
            print(" -! Ожидался ввод числа. Операция прервана !- ")
    return default


# Основная часть программы
if __name__ == "__main__":

    user = {
        "fio": "",
        "birth_year": 1900,
        "pwd": "",
        "balance": 0,
        "limit": 100_000,
        "transactions": []
    }

    print()
    print("\t\t\tВиртуалБанк")
    print("Добро пожаловать в наше консольное \"приложение\"!\n")

    op_user_restore(user, 'bank_data.txt')

    while True:
        print()
        print("Пожалуйста, выберите одну из доступных операций:\n")

        print("1. Создать аккаунт")
        print("2. Положить деньги")
        print("3. Снять деньги")
        print("4. Вывести баланс на экран")
        print("5. Выставление ожидаемого пополнения")
        print("6. Установить лимит на счет")
        print("7. Применить транзакции")
        print("8. Статистика по ожидаемым пополнениям")
        print("9. Просмотр отложенных пополнений (filtered)")
        print("0. Выйти из \"приложения\"")
        print()
        if (op := get_number(f"Какая операция Вас интересует? : ")) is None:
            continue
        print()

        if op not in range(10):
            print("Вы ввели номер несуществующей операции")
            continue

        if op == 1:
            op_account_create(user)
        elif op == 2:
            op_balance_deposit(user)
        elif op == 3:
            op_balance_withdraw(user)
        elif op == 4:
            op_balance_show(user)
        elif op == 5:
            op_transactions_add(user)
        elif op == 6:
            op_set_limit(user)
        elif op == 7:
            op_transactons_apply(user)
        elif op == 8:
            op_transaction_stats(user)
        elif op == 9:
            op_transactions_show(user)
        elif op == 0:
            print("Спасибо за пользование нашим \"приложением\"! До свидания!")
            break

        # if last_succeed:
        user_save_to_file(user, 'bank_data.txt')
        print("(Данные сохранены)")
