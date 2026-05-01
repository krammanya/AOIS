from hash_table import DoubleHashTable


INITIAL_SPORTS = [
    ("Футбол", "Командный вид спорта с мячом"),
    ("Хоккей", "Игра на льду с шайбой"),
    ("Теннис", "Игра с ракеткой и мячом"),
    ("Бокс", "Контактный вид спорта"),
    ("Плавание", "Водный вид спорта"),
    ("Баскетбол", "Командная игра с мячом"),
    ("Волейбол", "Игра через сетку"),
    ("Лыжи", "Зимний вид спорта"),
    ("Гимнастика", "Спорт с акробатическими элементами"),
    ("Бег", "Дисциплина легкой атлетики"),
    ("Фехтование", "Спорт с холодным оружием"),
    ("Регби", "Контактная командная игра с овальным мячом"),
    ("Поло", "Командная игра с мячом верхом на лошадях"),
    ("Гандбол", "Командная игра с передачами мяча руками"),
]


def fill_initial_table(table: DoubleHashTable):
    print("=== НАЧАЛЬНОЕ ФОРМИРОВАНИЕ ХЕШ-ТАБЛИЦЫ ===")
    for key, data in INITIAL_SPORTS:
        table.create(key, data)


def print_menu():
    print("\n=== МЕНЮ ===")
    print("1. Добавить запись")
    print("2. Найти запись по ключевому слову")
    print("3. Обновить данные записи")
    print("4. Удалить запись")
    print("5. Вывести хеш-таблицу")
    print("6. Вывести V(K), h(V), h2")
    print("7. Вывести коэффициент заполнения")
    print("0. Завершить программу")


def input_key() -> str:
    return input("Введите ключевое слово ID: ").strip()


def input_data() -> str:
    return input("Введите данные Pi: ").strip()


def handle_action(table: DoubleHashTable, choice: str) -> bool:
    try:
        if choice == "1":
            table.create(input_key(), input_data())
        elif choice == "2":
            table.read(input_key())
        elif choice == "3":
            table.update(input_key(), input_data())
        elif choice == "4":
            table.delete(input_key())
        elif choice == "5":
            table.print_table()
        elif choice == "6":
            table.print_values()
        elif choice == "7":
            print(f"Коэффициент заполнения: {table.fill_factor():.2f}")
        elif choice == "0":
            print("Работа программы завершена")
            return False
        else:
            print("Ошибка: выберите пункт меню от 0 до 7")
    except ValueError as error:
        print(f"Ошибка: {error}")

    return True


def main():
    table = DoubleHashTable()
    fill_initial_table(table)

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if not handle_action(table, choice):
            break


if __name__ == "__main__":
    main()
