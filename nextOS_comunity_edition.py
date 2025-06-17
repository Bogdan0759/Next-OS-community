import time
import subprocess
import json
from programs.notebook import run_notebook
from programs.timer import run_timer
from programs.calculator import run_calculator
from programs import shell

# Загрузка конфигурации компонентов ОС
with open('programs/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Основной цикл псевдо-ОС

def show_info():
    print("\n--- Информация о Next OS ---")
    print("Версия: 1.3.8")
    print("Разработчик: official; https://t.me/Poilwarp / community; @Sixrainky (tg) ")
    print("Эта псевдо-ОС создана для демонстрационных целей.")
    print("---------------------------\n")

# Основной цикл псевдо-ОС
while True:
    # Вывод главного меню
    print("Next OS (community edition)")
    print("Главное меню")
    menu = []
    if config.get("notebook", True):
        print("1. Блокнот")
        menu.append("1")
    if config.get("timer", True):
        print("2. Таймер")
        menu.append("2")
    if config.get("calculator", True):
        print("3. Калькулятор")
        menu.append("3")
    print("4. Информация")
    print("5. Выключение")

    # Получение ввода пользователя
    choice = input("выбери действие: ")

    # Обработка выбора пользователя
    if choice == "1" and config.get("notebook", True):
        run_notebook()
    elif choice == "2" and config.get("timer", True):
        run_timer()
    elif choice == "3" and config.get("calculator", True):
        run_calculator()
    elif choice == "4":
        show_info()
    elif choice == "5":
        print("Выключение...")
        break # Выход из цикла для завершения программы
    else:
        # Новые команды: run shell <путь> и shell wiki
        if choice.strip() == "run shell":
            script_path = "saves/notebook.txt"
            try:
                subprocess.run(["python", "programs/shell.py", script_path], check=False)
            except Exception as e:
                print(f"Ошибка запуска shell-скрипта: {e}")
        elif choice.strip() == "shell wiki":
            try:
                subprocess.run(["python", "programs/shell.py", "wiki"], check=False)
            except Exception as e:
                print(f"Ошибка вывода справки: {e}")
        # Включение/отключение компонентов
        elif choice.startswith("enable "):
            comp = choice.split(" ", 1)[1]
            if comp in config:
                config[comp] = True
                with open('programs/config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"Компонент {comp} включён.")
            else:
                print("Нет такого компонента.")
        elif choice.startswith("disable "):
            comp = choice.split(" ", 1)[1]
            if comp in config:
                config[comp] = False
                with open('programs/config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
                print(f"Компонент {comp} отключён.")
            else:
                print("Нет такого компонента.")
        else:
            print("Неверный ввод.")

print("Next ОС завершила работу.")