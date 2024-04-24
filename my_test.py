import main

def test_increase_balance_limit_zero():
    user = {
        "balance": 0,
        "limit": 0          # Лимит не задан
    }

    success = main.user_increase_balance(user, 0)    # На amount <= 0 пополнять нельзя
    assert user["balance"] == 0
    assert not success

    success = main.user_increase_balance(user, -1)
    assert user["balance"] == 0
    assert not success

    success = main.user_increase_balance(user, -999_999_999)
    assert user["balance"] == 0
    assert not success

    success = main.user_increase_balance(user, 999_999_999)
    assert user["balance"] == 999_999_999
    assert success

    success = main.user_increase_balance(user, 1)
    assert user["balance"] == 1_000_000_000
    assert success


def test_increase_balance_limit_nonzero():
    user = {
        "balance": 999_999_998,
        "limit": 999_999_999
    }

    success = main.user_increase_balance(user, 0)
    assert user["balance"] == 999_999_998
    assert not success

    success = main.user_increase_balance(user, -1)
    assert user["balance"] == 999_999_998
    assert not success

    success = main.user_increase_balance(user, 2)
    assert user["balance"] == 999_999_998
    assert not success

    success = main.user_increase_balance(user, -999_999_999)
    assert user["balance"] == 999_999_998
    assert not success

    success = main.user_increase_balance(user, 1)
    assert user["balance"] == 999_999_999
    assert success


def test_transactions_apply_list_nonempty():
    user = {
        "balance": 10001,
        "limit": 19999,
        "transactions": [
            {
                "comment": "1st",
                "amount": 8000
            },
            {
                "comment": "2nd",
                "amount": 1999
            },
            {
                "comment": "3rd",
                "amount": 1200
            },
            {
                "comment": "4th",
                "amount": -201
            },
        ]
    }

    main.op_transactons_apply(user)

    assert user["balance"] == 19201
    assert user["transactions"] == [
        {
            "comment": "2nd",
            "amount": 1999
        },
        {
            "comment": "4th",
            "amount": -201
        },
    ]


def test_transactions_apply_list_empty():
    user = {
        "balance": 0,
        "limit": 0,
        "transactions": []
    }

    main.op_transactons_apply(user)

    assert user["balance"] == 0
    assert user["transactions"] == []


def test_transactions_by_filter_list_nonempty():
    user = {
        "transactions": [
            {
                "comment": "1st",
                "amount": 8000
            },
            {
                "comment": "2nd",
                "amount": 1999
            },
            {
                "comment": "3rd",
                "amount": 1200
            },
            {
                "comment": "4th",
                "amount": 2001
            },
        ]
    }

    count = 0
    for t in main.transactions_by_filter(user, 2000):
        count += 1
        assert t["amount"] >= 2000
    assert count == 2

    count = 0
    for t in main.transactions_by_filter(user):
        count += 1
    assert count == 4


# Тесты на функции с input
def test_op_account_create():
    outputs = {
        "Введите ФИО: ": "Some Name",
        "Введите год рождения (ГГГГ): ": "1999",
        "Создайте пароль: ": "secret"
    }
    def fake_input(prompt):
        return outputs[prompt]

    main.input = fake_input

    user = {}
    assert main.op_account_create(user)

    outputs["Введите год рождения (ГГГГ): "] = "2000г н.э."
    assert not main.op_account_create(user)
    assert user == {
        "fio": "Some Name",
        "birth_year": 1999,
        "pwd": "secret",
        "balance": 0,
    }

    main.input = input


def test_op_balance_deposit():
    main.input = lambda _: input_case["amount"]

    input_cases = [
        {"amount": "0", "will_succeed": False},      # нельзя пополнить на 0
        {"amount": "90000", "will_succeed": True},
        {"amount": "10001", "will_succeed": False},  # превышение лимита
        {"amount": "9999", "will_succeed": True},
        {"amount": "-1", "will_succeed": False},     # нельзя пополнить на отриц кол-во
        {"amount": "1", "will_succeed": True},
        {"amount": "я не знаю", "will_succeed": False},
        {"amount": "", "will_succeed": False},
    ]
    user = {
        "balance": 0,
        "limit": 100_000
    }

    for input_case in input_cases:
        assert main.op_balance_deposit(user) == input_case["will_succeed"]

    assert user == {
        "balance": 100_000,
        "limit": 100_000
    }

    main.input = input


def test_op_balance_withdraw():
    def fake_input(prompt):
        _outputs = {
            "Введите пароль: ": input_case["pwd"],
            "Введите сумму для снятия: ": input_case["amount"]
        }
        return _outputs[prompt]

    main.input = fake_input

    input_cases = [
        {"pwd": "secret", "amount": "0", "will_succeed": False},
        {"pwd": "mypass", "amount": "100", "will_succeed": False},
        {"pwd": "", "amount": "1", "will_succeed": False},
        {"pwd": "secret", "amount": "99000", "will_succeed": True},
        {"pwd": "secret", "amount": "1000", "will_succeed": True},
        {"pwd": "secret", "amount": "999999999", "will_succeed": False},
        {"pwd": "secret", "amount": "-100000", "will_succeed": False},
        {"pwd": "secret", "amount": "$2000", "will_succeed": False},
        {"pwd": "secret", "amount": "", "will_succeed": False},
        {"pwd": "", "amount": "", "will_succeed": False},
    ]
    user = {
        "balance": 100_000,
        "limit": 100_000,
        "pwd": "secret"
    }

    for input_case in input_cases:
        assert main.op_balance_withdraw(user) == input_case["will_succeed"]

    assert user == {
        "balance": 0,
        "limit": 100_000,
        "pwd": "secret"
    }

    main.input = input


def test_op_balance_show():
    main.input = lambda _: input_case["pwd"]

    input_cases = [
        {"pwd": "", "will_succeed": False},
        {"pwd": "mypass", "will_succeed": False},
        {"pwd": "я не знаю", "will_succeed": False},
        {"pwd": "забыл", "will_succeed": False},
        {"pwd": "secret_string_of_mysterious_symbols:!@96#&^29*($4#12;''*&(#\":", "will_succeed": True},
    ]
    user = {
        "balance": 0,
        "pwd": "secret_string_of_mysterious_symbols:!@96#&^29*($4#12;''*&(#\":"
    }
    for input_case in input_cases:
        assert main.op_balance_show(user) == input_case["will_succeed"]

    main.input = input


def test_op_transactions_add():
    def fake_input(prompt):
        _outputs = {
            "Сумма будущего пополнения: ": input_case["amount"],
            "Назначение: ": input_case["comment"]
        }
        return _outputs[prompt]

    main.input = fake_input

    input_cases = [
        {"amount": "0", "comment": "empty", "will_succeed": False},
        {"amount": "90000", "comment": "_", "will_succeed": True},
        {"amount": "10001", "comment": " ", "will_succeed": True},
        {"amount": "9999", "comment": "ok", "will_succeed": True},
        {"amount": "-1", "comment": "neg1", "will_succeed": False},
        {"amount": "1", "comment": "1один", "will_succeed": True},
        {"amount": "я не знаю", "comment": "", "will_succeed": False},
        {"amount": "", "comment": "failtoadd", "will_succeed": False},
    ]
    user = {
        "transactions": []
    }

    for input_case in input_cases:
        assert main.op_transactions_add(user) == input_case["will_succeed"]

    assert user["transactions"] == [
        {"amount": 90000, "comment": "_"},
        {"amount": 10001, "comment": " "},
        {"amount": 9999, "comment": "ok"},
        {"amount": 1, "comment": "1один"},
    ]
    main.input = input


def test_op_set_limit():
    main.input = lambda _: input_case["limit"]

    input_cases = [
        {"limit": "0", "will_succeed": True},
        {"limit": "-1", "will_succeed": False},
        {"limit": "999_999_999", "will_succeed": True},
        {"limit": "nolimit", "will_succeed": False},
        {"limit": "inf", "will_succeed": False},
        {"limit": "", "will_succeed": False},
    ]

    user = {
        "limit": 0
    }

    for input_case in input_cases:
        assert main.op_set_limit(user) == input_case["will_succeed"]

    assert user == {
        "limit": 999_999_999
    }

    main.input = input


def test_ob_transactions_stats():
    user1 = {
        "transactions": [
            {"amount": 10000, "comment": ""},
            {"amount": 10000, "comment": ""},
            {"amount": 0, "comment": ""},
        ]
    }
    user2 = {
        "transactions": [
            {"amount": 0, "comment": ""},
        ]
    }
    user3 = {
        "transactions": []
    }

    main.op_transaction_stats(user1)
    main.op_transaction_stats(user2)
    main.op_transaction_stats(user3)

    # op_transaction_stats - ok
    assert True     # Если тест дошел сюда, значит предыдущие вызовы не провалились


def test_op_transactions_show():
    main.input = lambda _: input_case

    input_cases = ["0", "-1", "999_999_999", "nomax", "inf", ""]

    user1 = {
        "transactions": [
            {"amount": 10000, "comment": ""},
            {"amount": 10000, "comment": ""},
            {"amount": 0, "comment": ""},
        ]
    }
    user2 = {
        "transactions": [
            {"amount": 0, "comment": ""},
        ]
    }
    user3 = {
        "transactions": []
    }

    for input_case in input_cases:
        main.op_transactions_show(user1)
        main.op_transactions_show(user2)
        main.op_transactions_show(user3)

    # op_transactions_show - ok
    assert True     # Если тест дошел сюда, значит предыдущие вызовы не провалились


def test_get_number():
    main.input = lambda _: input_case["num"]

    input_cases = [
        {"num": "", "will_succeed": False},
        {"num": "-1", "will_succeed": True},
        {"num": "-0", "will_succeed": True},
        {"num": "000_000", "will_succeed": True},
        {"num": "0_0", "will_succeed": True},
        {"num": "-1_", "will_succeed": False},
        {"num": "0", "will_succeed": True},
        {"num": "$1", "will_succeed": False},
        {"num": "\n", "will_succeed": False},
    ]

    for input_case in input_cases:
        assert (type(main.get_number("")) == int) == input_case["will_succeed"]
        assert type(main.get_number("", 0)) == int

