from src.arithmetic.direct_code_divider import DirectCodeDivider
from src.arithmetic.direct_code_multiplier import DirectCodeMultiplier
from src.arithmetic.twos_complement_adder import TwosComplementAdder
from src.arithmetic.twos_complement_subtractor import TwosComplementSubtractor
from src.bcd.bcd2421_adder import Bcd2421Adder
from src.bcd.bcd2421_codec import Bcd2421Codec
from src.conversions.direct_code_encoder import DirectCodeEncoder
from src.conversions.ones_complement_encoder import OnesComplementEncoder
from src.conversions.twos_complement_encoder import TwosComplementEncoder
from src.floating_point.binary32_arithmetic import Binary32Arithmetic
from src.floating_point.binary32_codec import Binary32Codec


def show_menu() -> None:
    print()
    print("Выберите операцию:")
    print("1. Перевести число в прямой, обратный и дополнительный коды")
    print("2. Сложить два числа в дополнительном коде")
    print("3. Вычесть два числа в дополнительном коде")
    print("4. Умножить два числа в прямом коде")
    print("5. Разделить два числа в прямом коде")
    print("6. Сложить два числа с плавающей точкой (IEEE-754)")
    print("7. Вычесть два числа с плавающей точкой (IEEE-754)")
    print("8. Умножить два числа с плавающей точкой (IEEE-754)")
    print("9. Разделить два числа с плавающей точкой (IEEE-754)")
    print("10. Сложить два числа в коде 2421 BCD")
    print("0. Выход")


def read_integer(prompt: str) -> int:
    while True:
        user_input = input(prompt)

        try:
            return int(user_input)
        except ValueError:
            print("Ошибка: введите целое число.")


def read_decimal_string(prompt: str) -> str:
    while True:
        user_input = input(prompt)

        try:
            Binary32Codec().from_decimal_string(user_input)
            return user_input
        except ValueError:
            print("Ошибка: введите корректное число с плавающей точкой.")


def read_bcd_decimal_string(prompt: str) -> str:
    while True:
        user_input = input(prompt)

        try:
            Bcd2421Codec().encode(user_input)
            return user_input
        except ValueError:
            print("Ошибка: введите неотрицательное целое число.")


def handle_number_conversion() -> None:
    value = read_integer("Введите целое число: ")

    direct_encoder = DirectCodeEncoder()
    ones_encoder = OnesComplementEncoder()
    twos_encoder = TwosComplementEncoder()

    try:
        direct_code = direct_encoder.encode(value)
        ones_code = ones_encoder.encode(value)
        twos_code = twos_encoder.encode(value)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    print()
    print(f"Десятичное число:   {value}")
    print(f"Прямой код:         {direct_code.to_string()}")
    print(f"Обратный код:       {ones_code.to_string()}")
    print(f"Дополнительный код: {twos_code.to_string()}")


def handle_twos_complement_addition() -> None:
    left_value = read_integer("Введите первое целое число: ")
    right_value = read_integer("Введите второе целое число: ")

    adder = TwosComplementAdder()
    encoder = TwosComplementEncoder()

    try:
        left_word = encoder.encode(left_value)
        right_word = encoder.encode(right_value)
        result_word, result_value, overflow = adder.add(left_value, right_value)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    print()
    print(f"Первое число (10):  {left_value}")
    print(f"Первое число (2):   {left_word.to_string()}")
    print(f"Второе число (10):  {right_value}")
    print(f"Второе число (2):   {right_word.to_string()}")
    print(f"Результат (2):      {result_word.to_string()}")
    print(f"Результат (10):     {result_value}")
    print(f"Переполнение:       {'Да' if overflow else 'Нет'}")


def handle_twos_complement_subtraction() -> None:
    minuend = read_integer("Введите уменьшаемое: ")
    subtrahend = read_integer("Введите вычитаемое: ")

    subtractor = TwosComplementSubtractor()
    encoder = TwosComplementEncoder()

    try:
        minuend_word = encoder.encode(minuend)
        subtrahend_word = encoder.encode(subtrahend)
        negated_subtrahend_word = subtractor.negate(subtrahend)
        result_word, result_value, overflow = subtractor.subtract(
            minuend,
            subtrahend,
        )
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    print()
    print(f"Уменьшаемое (10):           {minuend}")
    print(f"Уменьшаемое (2):            {minuend_word.to_string()}")
    print(f"Вычитаемое (10):            {subtrahend}")
    print(f"Вычитаемое (2):             {subtrahend_word.to_string()}")
    print(f"Отрицание вычитаемого (2):  {negated_subtrahend_word.to_string()}")
    print(f"Результат (2):              {result_word.to_string()}")
    print(f"Результат (10):             {result_value}")
    print(f"Переполнение:               {'Да' if overflow else 'Нет'}")


def handle_direct_code_multiplication() -> None:
    left_value = read_integer("Введите первое целое число: ")
    right_value = read_integer("Введите второе целое число: ")

    encoder = DirectCodeEncoder()
    multiplier = DirectCodeMultiplier()

    try:
        left_word = encoder.encode(left_value)
        right_word = encoder.encode(right_value)
        result_word, result_value = multiplier.multiply(left_value, right_value)
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    print()
    print(f"Первое число (10):  {left_value}")
    print(f"Первое число (2):   {left_word.to_string()}")
    print(f"Второе число (10):  {right_value}")
    print(f"Второе число (2):   {right_word.to_string()}")
    print(f"Результат (2):      {result_word.to_string()}")
    print(f"Результат (10):     {result_value}")


def handle_direct_code_division() -> None:
    dividend = read_integer("Введите делимое: ")
    divisor = read_integer("Введите делитель: ")

    encoder = DirectCodeEncoder()
    divider = DirectCodeDivider()

    try:
        dividend_word = encoder.encode(dividend)
        divisor_word = encoder.encode(divisor)
        quotient_word, binary_result, decimal_result = divider.divide(
            dividend,
            divisor,
        )
    except ValueError as error:
        print(f"Ошибка: {error}")
        return

    print()
    print(f"Делимое (10):                         {dividend}")
    print(f"Делимое в прямом коде:                {dividend_word.to_string()}")
    print(f"Делитель (10):                        {divisor}")
    print(f"Делитель в прямом коде:               {divisor_word.to_string()}")
    print(f"Целая часть частного в прямом коде:   {quotient_word.to_string()}")
    print(f"Результат деления в двоичном виде:    {binary_result}")
    print(f"Результат деления в десятичном виде:  {decimal_result}")


def handle_binary32_operation(operation_name: str) -> None:
    left_value = read_decimal_string("Введите первое число с плавающей точкой: ")
    right_value = read_decimal_string("Введите второе число с плавающей точкой: ")

    codec = Binary32Codec()
    arithmetic = Binary32Arithmetic()

    left_word = codec.from_decimal_string(left_value)
    right_word = codec.from_decimal_string(right_value)

    if operation_name == "add":
        result_word = arithmetic.add(left_word, right_word)
    elif operation_name == "subtract":
        result_word = arithmetic.subtract(left_word, right_word)
    elif operation_name == "multiply":
        result_word = arithmetic.multiply(left_word, right_word)
    else:
        result_word = arithmetic.divide(left_word, right_word)

    rounded_left = codec.to_decimal_string(left_word)
    rounded_right = codec.to_decimal_string(right_word)
    result_value = codec.to_decimal_string(result_word)

    print()
    print(f"Первое число (10):  {rounded_left}")
    print(f"Первое число (2):   {left_word.to_string()}")
    print(f"Второе число (10):  {rounded_right}")
    print(f"Второе число (2):   {right_word.to_string()}")
    print(f"Результат (2):      {result_word.to_string()}")
    print(f"Результат (10):     {result_value}")


def handle_bcd2421_addition() -> None:
    left_value = read_bcd_decimal_string("Введите первое неотрицательное число: ")
    right_value = read_bcd_decimal_string("Введите второе неотрицательное число: ")

    codec = Bcd2421Codec()
    adder = Bcd2421Adder()

    left_number = codec.encode(left_value)
    right_number = codec.encode(right_value)
    result_number, result_decimal = adder.add(left_value, right_value)

    print()
    print(f"Первое число (10):   {left_value}")
    print(f"Первое число (2421): {left_number.to_string()}")
    print(f"Второе число (10):   {right_value}")
    print(f"Второе число (2421): {right_number.to_string()}")
    print(f"Результат (2421):    {result_number.to_string()}")
    print(f"Результат (10):      {result_decimal}")


def main() -> None:
    while True:
        show_menu()
        choice = input("Введите номер пункта: ")

        if choice == "1":
            handle_number_conversion()
        elif choice == "2":
            handle_twos_complement_addition()
        elif choice == "3":
            handle_twos_complement_subtraction()
        elif choice == "4":
            handle_direct_code_multiplication()
        elif choice == "5":
            handle_direct_code_division()
        elif choice == "6":
            handle_binary32_operation("add")
        elif choice == "7":
            handle_binary32_operation("subtract")
        elif choice == "8":
            handle_binary32_operation("multiply")
        elif choice == "9":
            handle_binary32_operation("divide")
        elif choice == "10":
            handle_bcd2421_addition()
        elif choice == "0":
            print("Завершение программы.")
            break
        else:
            print("Ошибка: выберите число от 0 до 10.")


if __name__ == "__main__":
    main()
