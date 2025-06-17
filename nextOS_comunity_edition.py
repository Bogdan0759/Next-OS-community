import time

# Основной цикл псевдо-ОС

def run_notebook():
    print("\n--- Блокнот ---")
    print("Введите текст построчно. Для выхода введите пустую строку.")
    lines = []
    while True:
        line = input("> ")
        if not line:
            break
        lines.append(line)
    print("\nСодержимое блокнота:")
    for line in lines:
        print(line)
    print("-------------------\n")

def run_timer():
    print("\n--- Таймер ---")
    try:
        seconds = int(input("Введите количество секунд: "))
        if seconds < 0:
            print("Время не может быть отрицательным.")
            return
        print(f"Таймер запущен на {seconds} секунд...")
        time.sleep(seconds)
        print("Время вышло!")
    except ValueError:
        print("Неверный ввод. Пожалуйста, введите целое число секунд.")
    print("-------------------\n")

def run_calculator():
    print("\n--- Калькулятор ---")
    expression = input("Введите математическое выражение (например, 2+2*3): ")
    try:
        result = eval(expression)
        print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка при вычислении: {e}")
    print("---------------------\n")

def show_info():
    print("\n--- Информация о Next OS ---")
    print("Версия: 1.1")
    print("Разработчик: official; https://t.me/Poilwarp / community; @Sixrainky (tg) ")
    print("Эта псевдо-ОС создана для демонстрационных целей.")
    print("---------------------------\n")

# Основной цикл псевдо-ОС
while True:
    # Вывод главного меню
    print("Next OS (community edition)")
    print("Главное меню")
    print("1. Блокнот")
    print("2. Таймер")
    print("3. Калькулятор")
    print("4. Информация")
    print("5. Выключение")

    # Получение ввода пользователя
    choice = input("выбери действие: ")

    # Обработка выбора пользователя
    if choice == "1":
        run_notebook()
    elif choice == "2":
        run_timer()
    elif choice == "3":
        run_calculator()
    elif choice == "4":
        show_info()
    elif choice == "5":
        print("Выключение...")
        break # Выход из цикла для завершения программы
    else:
        print("Неверный ввод.")

print("Next ОС завершила работу.")