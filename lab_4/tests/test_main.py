import builtins

import pytest

import main
from hash_table import DoubleHashTable


def test_fill_initial_table_adds_sport_records(capsys):
    table = DoubleHashTable()

    main.fill_initial_table(table)

    assert len(table._active_indexes()) == len(main.INITIAL_SPORTS)
    assert table.collisions >= 2
    assert "НАЧАЛЬНОЕ ФОРМИРОВАНИЕ" in capsys.readouterr().out


def test_print_menu_contains_all_actions(capsys):
    main.print_menu()

    output = capsys.readouterr().out
    assert "1. Добавить запись" in output
    assert "2. Найти запись" in output
    assert "3. Обновить" in output
    assert "4. Удалить" in output
    assert "5. Вывести хеш-таблицу" in output
    assert "6. Вывести V(K)" in output
    assert "7. Вывести коэффициент" in output
    assert "0. Завершить" in output


def test_input_helpers_strip_user_text(monkeypatch):
    answers = iter(["  Футбол  ", "  Командный спорт  "])
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    assert main.input_key() == "Футбол"
    assert main.input_data() == "Командный спорт"


def test_handle_action_create_read_update_delete(monkeypatch, capsys):
    table = DoubleHashTable()
    answers = iter(
        [
            "Футбол",
            "Командный спорт",
            "Футбол",
            "Футбол",
            "Новые данные",
            "Футбол",
        ]
    )
    monkeypatch.setattr(builtins, "input", lambda _: next(answers))

    assert main.handle_action(table, "1") is True
    assert main.handle_action(table, "2") is True
    assert main.handle_action(table, "3") is True
    assert main.handle_action(table, "4") is True

    output = capsys.readouterr().out
    assert "Добавлено: Футбол" in output
    assert "Найдено" in output
    assert "Обновлено: Футбол" in output
    assert "Удалено: Футбол" in output


@pytest.mark.parametrize("choice, expected", [("5", "ХЕШ-ТАБЛИЦА"), ("6", "ВЫЧИСЛЕННЫЕ"), ("7", "Коэффициент")])
def test_handle_action_output_choices(choice, expected, capsys):
    table = DoubleHashTable()
    table.create("Футбол", "Командный спорт")

    assert main.handle_action(table, choice) is True
    assert expected in capsys.readouterr().out


def test_handle_action_invalid_choice_and_value_error(monkeypatch, capsys):
    table = DoubleHashTable()
    monkeypatch.setattr(builtins, "input", lambda _: "A1")

    assert main.handle_action(table, "bad") is True
    assert main.handle_action(table, "2") is True

    output = capsys.readouterr().out
    assert "выберите пункт меню" in output
    assert "Первые две буквы ключа должны быть русскими" in output


def test_handle_action_exit_returns_false(capsys):
    table = DoubleHashTable()

    assert main.handle_action(table, "0") is False
    assert "Работа программы завершена" in capsys.readouterr().out

