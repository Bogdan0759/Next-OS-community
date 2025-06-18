import time
import subprocess
import json
import os
from programs.notebook import run_notebook
from programs.timer import run_timer
from programs.calculator import run_calculator
from programs.game_center import run_game_center
from programs import shell

# Загрузка конфигурации компонентов ОС
config_path = os.path.join(os.path.dirname(__file__), 'programs', 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

current_user = "guest" 

# Основной цикл

def show_info():
    print("\n--- Информация о Next OS ---")
    print("Версия: 1.4.1")
    print("Разработчик: official; https://t.me/Poilwarp / community; @Sixrainky (tg) ")
    print("Эта псевдо-ОС создана для демонстрационных целей.")
    print("---------------------------\n")

while True:
    # Вывод главного меню
    print(f"Next OS (community edition) — пользователь: {current_user}")
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
    # Добавляем Game Center в меню под номером 4
    if config.get("game_center", True):
        print("4. Игровой центр")
        menu.append("4")

    print("5. Информация") # Информация теперь под номером 5
    print("6. Выключение") # Выключение теперь под номером 6

    # Получение ввода пользователя
    choice = input("выбери действие: ")

    # Обработка выбора
    if choice == "1" and config.get("notebook", True):
        run_notebook()
    elif choice == "2" and config.get("timer", True):
        run_timer()
    elif choice == "3" and config.get("calculator", True):
        run_calculator()
    elif choice == "4" and config.get("game_center", True): # Обработка выбора Game Center теперь по номеру 4
        run_game_center()
    elif choice == "5": # Обработка выбора Информации теперь по номеру 5
        show_info()
    elif choice == "6": # Обработка выбора Выключения теперь по номеру 6
        print("Выключение...")
        break # Выход из цикла
    else:
        
        if choice.strip() == "run shell":
            script_path = f"saves/{current_user}/notebook.txt"
            try:
                subprocess.run(["python", "programs/shell.py", script_path], check=False)
            except Exception as e:
                print(f"Ошибка запуска shell-скрипта: {e}")
        elif choice.strip() == "shell wiki":
            try:
                subprocess.run(["python", "programs/shell.py", "wiki"], check=False)
            except Exception as e:
                print(f"Ошибка вывода справки: {e}")
        
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