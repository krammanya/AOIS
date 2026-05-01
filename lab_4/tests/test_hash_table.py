import pytest

from hash_table import ALPHABET, DoubleHashTable, HashRecord


def test_hash_record_defaults_match_empty_row():
    row = HashRecord()

    assert row.ID == ""
    assert row.C == 0
    assert row.U == 0
    assert row.T == 1
    assert row.L == 0
    assert row.D == 0
    assert row.Po is None
    assert row.Pi == ""
    assert row.V is None
    assert row.h is None
    assert row.h2 is None


def test_hash_functions_use_first_two_russian_letters():
    table = DoubleHashTable(size=23)

    v = table.calculate_v("Футбол")

    assert table.normalize_key("  футбол ") == "ФУТБОЛ"
    assert v == ALPHABET.index("Ф") * 33 + ALPHABET.index("У")
    assert table.hash1(v) == v % 23
    assert table.hash2(v) == 1 + (v % 22)
    assert table.probe(3, 4, 5) == (3 + 5 * 4) % 23


@pytest.mark.parametrize("key", ["А", "A1", "1Ф"])
def test_calculate_v_rejects_invalid_keys(key):
    table = DoubleHashTable()

    with pytest.raises(ValueError):
        table.calculate_v(key)


def test_create_and_read_record(capsys):
    table = DoubleHashTable()

    assert table.create("Футбол", "Командный спорт") is True
    index = table.read("футбол")

    assert index == 0
    assert table.table[index].ID == "Футбол"
    assert table.table[index].Pi == "Командный спорт"
    assert table.table[index].U == 1
    assert table.table[index].D == 0
    assert "Найдено" in capsys.readouterr().out


def test_duplicate_key_is_not_inserted(capsys):
    table = DoubleHashTable()

    assert table.create("Футбол", "Первое значение") is True
    assert table.create("Футбол", "Повтор") is False

    assert table.fill_factor() == pytest.approx(1 / 23)
    assert table.table[0].Pi == "Первое значение"
    assert "уже существует" in capsys.readouterr().out


def test_update_existing_record_and_fail_for_missing(capsys):
    table = DoubleHashTable()
    table.create("Футбол", "Старое значение")

    assert table.update("Футбол", "Новое значение") is True
    assert table.table[0].Pi == "Новое значение"

    assert table.update("Хоккей", "Ледовая игра") is False
    assert "Не найдено: Хоккей" in capsys.readouterr().out


def test_delete_marks_record_and_excludes_from_search_and_load_factor(capsys):
    table = DoubleHashTable()
    table.create("Футбол", "Командный спорт")

    assert table.delete("Футбол") is True
    assert table.read("Футбол") is None
    assert table.fill_factor() == 0
    assert table.table[0].D == 1

    assert table.delete("Футбол") is False
    output = capsys.readouterr().out
    assert "Удалено: Футбол" in output
    assert "Не найдено: Футбол" in output


def test_deleted_slot_can_be_reused():
    table = DoubleHashTable()
    table.create("Футбол", "Командный спорт")
    table.delete("Футбол")

    assert table.create("Футбол", "Повторное добавление") is True
    index = table.read("Футбол", silent=True)

    assert index == 0
    assert table.table[index].D == 0
    assert table.table[index].Pi == "Повторное добавление"


def test_double_hashing_resolves_collision_and_sets_flags():
    table = DoubleHashTable()

    table.create("Теннис", "Игра с ракеткой")
    table.create("Плавание", "Водный спорт")

    tennis_index = table.read("Теннис", silent=True)
    swimming_index = table.read("Плавание", silent=True)

    assert tennis_index == 11
    assert swimming_index == 1
    assert table.collisions == 1
    assert table.table[tennis_index].C == 1
    assert table.table[tennis_index].T == 0
    assert table.table[tennis_index].Po == swimming_index
    assert table.table[swimming_index].C == 1
    assert table.table[swimming_index].T == 1


def test_insert_reports_full_table_when_no_slot_is_available(capsys):
    table = DoubleHashTable(size=2)
    table.create("АА", "Первая запись")
    table.create("ББ", "Вторая запись")

    assert table.create("ВВ", "Третья запись") is False
    assert "Таблица заполнена" in capsys.readouterr().out


def test_print_methods_show_required_fields(capsys):
    table = DoubleHashTable()
    table.create("Футбол", "Командный спорт")

    table.print_values()
    table.print_table()

    output = capsys.readouterr().out
    assert "ВЫЧИСЛЕННЫЕ ЗНАЧЕНИЯ" in output
    assert "ХЕШ-ТАБЛИЦА" in output
    assert "ID" in output
    assert "C" in output
    assert "U" in output
    assert "T" in output
    assert "L" in output
    assert "D" in output
    assert "Po" in output
    assert "Pi" in output
    assert "Коэффициент заполнения" in output
