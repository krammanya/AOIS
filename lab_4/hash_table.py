from dataclasses import dataclass
from typing import Optional


# Русский алфавит: А=0, Б=1, ..., Я=32
ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"

TABLE_SIZE = 23
B = 0


@dataclass
class HashRecord:
    ID: str = ""
    C: int = 0
    U: int = 0
    T: int = 1
    L: int = 0
    D: int = 0
    Po: Optional[int] = None
    Pi: str = ""
    V: Optional[int] = None
    h: Optional[int] = None
    h2: Optional[int] = None


class DoubleHashTable:
    def __init__(self, size: int = TABLE_SIZE):
        self.size = size
        self.table = [HashRecord() for _ in range(size)]
        self.collisions = 0

    def normalize_key(self, key: str) -> str:
        return key.upper().strip()

    def calculate_v(self, key: str) -> int:
        key = self.normalize_key(key)

        if len(key) < 2:
            raise ValueError("Ключ должен содержать минимум 2 буквы")

        first = key[0]
        second = key[1]

        if first not in ALPHABET or second not in ALPHABET:
            raise ValueError("Первые две буквы ключа должны быть русскими")

        first_index = ALPHABET.index(first)
        second_index = ALPHABET.index(second)

        return first_index * 33 + second_index

    def hash1(self, V: int) -> int:
        return (V % self.size) + B

    def hash2(self, V: int) -> int:
        return 1 + (V % (self.size - 1))

    def probe(self, h1: int, h2: int, i: int) -> int:
        return (h1 + i * h2) % self.size

    def _find_index(self, key: str) -> Optional[int]:
        V = self.calculate_v(key)
        h1 = self.hash1(V)
        h2 = self.hash2(V)

        for i in range(self.size):
            index = self.probe(h1, h2, i)
            record = self.table[index]

            if record.U == 0:
                return None

            if record.D == 0 and record.ID.lower() == key.lower().strip():
                return index

        return None

    def _find_slot_for_insert(self, key: str) -> tuple[Optional[int], bool, int, int, int]:
        V = self.calculate_v(key)
        h1 = self.hash1(V)
        h2 = self.hash2(V)
        first_deleted = None
        has_collision = False

        for i in range(self.size):
            index = self.probe(h1, h2, i)
            record = self.table[index]

            if record.U == 1 and record.D == 0 and record.ID.lower() == key.lower().strip():
                return None, has_collision, V, h1, h2

            if record.U == 1 and record.D == 1 and first_deleted is None:
                first_deleted = index

            if record.U == 0:
                return first_deleted if first_deleted is not None else index, has_collision, V, h1, h2

            has_collision = True

        return first_deleted, has_collision, V, h1, h2

    def _active_indexes(self):
        return [i for i, record in enumerate(self.table) if record.U == 1 and record.D == 0]

    def _rebuild_collision_flags(self):
        for index, record in enumerate(self.table):
            if record.U == 1 and record.D == 0:
                record.C = 0
                record.T = 1
                record.L = 0
                record.Po = index
            elif record.U == 0:
                self.table[index] = HashRecord()

        for index in self._active_indexes():
            record = self.table[index]
            previous_index = None

            for i in range(self.size):
                probe_index = self.probe(record.h, record.h2, i)

                if probe_index == index:
                    if previous_index is not None:
                        previous = self.table[previous_index]
                        previous.C = 1
                        previous.T = 0
                        previous.Po = index
                        record.C = 1
                        record.T = 1
                        record.Po = index
                    break

                previous = self.table[probe_index]
                if previous.U == 1 and previous.D == 0:
                    previous_index = probe_index

    def create(self, key: str, data: str) -> bool:
        if self._find_index(key) is not None:
            print(f"Ошибка: ключ '{key}' уже существует")
            return False

        slot, has_collision, V, h1, h2 = self._find_slot_for_insert(key)

        if slot is None:
            print("Таблица заполнена")
            return False

        if has_collision:
            self.collisions += 1

        self.table[slot] = HashRecord(
            ID=key.strip(),
            C=1 if has_collision else 0,
            U=1,
            T=1,
            L=0,
            D=0,
            Po=slot,
            Pi=data,
            V=V,
            h=h1,
            h2=h2,
        )
        self._rebuild_collision_flags()

        print(f"Добавлено: {key} | V={V}, h={h1}, h2={h2}, строка={slot}")
        return True

    def read(self, key: str, silent: bool = False) -> Optional[int]:
        index = self._find_index(key)

        if index is None:
            if not silent:
                print(f"Не найдено: {key}")
            return None

        record = self.table[index]
        if not silent:
            print(f"Найдено: строка={index}, ID={record.ID}, Pi={record.Pi}")
        return index

    def update(self, key: str, new_data: str) -> bool:
        index = self._find_index(key)

        if index is None:
            print(f"Не найдено: {key}")
            return False

        self.table[index].Pi = new_data
        print(f"Обновлено: {key}")
        return True

    def delete(self, key: str) -> bool:
        index = self._find_index(key)

        if index is None:
            print(f"Не найдено: {key}")
            return False

        self.table[index].D = 1
        self._rebuild_collision_flags()
        print(f"Удалено: {key}")
        return True

    def fill_factor(self) -> float:
        occupied = len(self._active_indexes())
        return occupied / self.size

    def print_values(self):
        print("\nВЫЧИСЛЕННЫЕ ЗНАЧЕНИЯ V(K), h(V), h2:")
        print(f"{'ID':<15} {'V':>5} {'h':>4} {'h2':>4}")
        for record in self.table:
            if record.U == 1 and record.D == 0:
                print(f"{record.ID:<15} {record.V:>5} {record.h:>4} {record.h2:>4}")

    def print_table(self):
        print("\nХЕШ-ТАБЛИЦА:")
        print(
            f"{'N':>2} {'ID':<15} {'C':>2} {'U':>2} {'T':>2} {'L':>2} "
            f"{'D':>2} {'Po':>4} {'V':>5} {'h':>4} {'h2':>4} Pi"
        )
        for i, record in enumerate(self.table):
            po = "-" if record.Po is None else record.Po
            V = "-" if record.V is None else record.V
            h = "-" if record.h is None else record.h
            h2 = "-" if record.h2 is None else record.h2
            print(
                f"{i:>2} {record.ID:<15} {record.C:>2} {record.U:>2} "
                f"{record.T:>2} {record.L:>2} {record.D:>2} {po:>4} "
                f"{V:>5} {h:>4} {h2:>4} {record.Pi}"
            )

        print(f"\nКоличество коллизий: {self.collisions}")
        print(f"Коэффициент заполнения: {self.fill_factor():.2f}")
