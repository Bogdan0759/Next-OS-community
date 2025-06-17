import time
import subprocess
from programs.notebook import run_notebook
from programs.timer import run_timer
from programs.calculator import run_calculator

# Основной цикл псевдо-ОС

def show_info():
    print("\n--- Информация о Next OS ---")
    print("Версия: 1.2.0")
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
        # Новые команды: run shell <путь> и shell wiki
        if choice.startswith("run shell"):
            parts = choice.split(maxsplit=2)
            if len(parts) == 3:
                script_path = parts[2]
                try:
                    subprocess.run(["python", "programs/shell.py", script_path], check=False)
                except Exception as e:
                    print(f"Ошибка запуска shell-скрипта: {e}")
            else:
                print("Использование: run shell <путь_к_скрипту>")
        elif choice.strip() == "shell wiki":
            try:
                subprocess.run(["python", "programs/shell.py", "wiki"], check=False)
            except Exception as e:
                print(f"Ошибка вывода справки: {e}")
        else:
            print("Неверный ввод.")

print("Next ОС завершила работу.")