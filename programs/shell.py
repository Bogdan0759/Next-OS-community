# Shell script interpreter for NextOS Community Edition
# Поддержка: первая строка должна быть 'shell script', команда 'shell wiki' выводит справку

import os

def print_wiki():
    print("""
NextOS Shell Script Documentation
===============================

- Первая строка скрипта: shell script
- Поддерживаемые команды:
    echo <text|var>      — вывести текст или значение переменной
    set <var> <value>    — создать/задать переменную
    input <var>          — запросить ввод пользователя и сохранить в переменную
    add/sub/mul/div <a> <b> — арифметика (можно использовать переменные)
    if <var> == <value>  — условие, блок до endif
    while <var> != <value> — цикл, блок до endwhile
    shell wiki           — показать эту справку
    shell enable <компонент>  — включить компонент ОС (notebook, timer, calculator)
    shell disable <компонент> — отключить компонент ОС
    file create <путь>   — создать файл (например, метку вируса)
    file delete <путь>   — удалить файл
    file exists <путь> <var> — записать 1/0 в переменную, если файл есть/нет

Пример вируса:
shell script
file create saves/virus.flag
shell disable notebook
echo ОС заражена!

Пример антивируса:
shell script
file exists saves/virus.flag infected
if infected == 1
  file delete saves/virus.flag
  shell enable notebook
  echo Вирус удалён!
endif
""")

def run_shell_script(path):
    variables = {}
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    if not lines or lines[0] != 'shell script':
        print('Ошибка: первая строка должна быть "shell script"')
        return
    i = 1
    while i < len(lines):
        line = lines[i]
        parts = line.split()
        if not parts:
            i += 1
            continue
        cmd, *args = parts
        # Переменные: set var value
        if cmd == 'set' and len(args) >= 2:
            var = args[0]
            value = ' '.join(args[1:])
            if value in variables:
                value = variables[value]
            variables[var] = value
        # Ввод: input var
        elif cmd == 'input' and len(args) == 1:
            var = args[0]
            variables[var] = input(f'Введите значение для {var}: ')
        # Условия: if var == value ... endif
        elif cmd == 'if' and len(args) == 3 and args[1] == '==':
            var, _, value = args
            block = []
            i += 1
            while i < len(lines) and lines[i] != 'endif':
                block.append(lines[i])
                i += 1
            if variables.get(var) == value:
                for bline in block:
                    lines.insert(i+1, bline)
            # endif пропускаем
        # Цикл: while var != value ... endwhile
        elif cmd == 'while' and len(args) == 3 and args[1] == '!=' and args[0] in variables:
            var, _, value = args
            block_start = i + 1
            block = []
            while i+1 < len(lines) and lines[i+1] != 'endwhile':
                block.append(lines[i+1])
                i += 1
            while variables.get(var) != value:
                for bline in block:
                    # Вставляем блок после endwhile для повторного выполнения
                    lines.insert(i+2, bline)
                # Обновляем переменную (может быть изменена внутри блока)
                # break если бесконечный цикл
                if variables.get(var) == value:
                    break
            # endwhile пропускаем
        # echo с переменными
        elif cmd == 'echo':
            out = []
            for arg in args:
                out.append(variables.get(arg, arg))
            print(' '.join(out))
        # Арифметика с переменными
        elif cmd in ('add', 'sub', 'mul', 'div') and len(args) == 2:
            a = variables.get(args[0], args[0])
            b = variables.get(args[1], args[1])
            try:
                a, b = float(a), float(b)
                if cmd == 'add':
                    print(a + b)
                elif cmd == 'sub':
                    print(a - b)
                elif cmd == 'mul':
                    print(a * b)
                elif cmd == 'div':
                    print(a / b)
            except Exception:
                print('Ошибка арифметики')
        elif cmd == 'shell' and len(args) == 3 and args[1] in ('enable', 'disable'):
            component = args[2]
            state = args[1] == 'enable'
            set_component_state(component, state)
        elif cmd == 'shell' and args and args[0] == 'wiki':
            print_wiki()
        # Создать файл: file create <путь>
        elif cmd == 'file' and len(args) == 2 and args[0] == 'create':
            try:
                with open(args[1], 'w', encoding='utf-8') as f:
                    f.write('virus')
                print(f'Файл {args[1]} создан.')
            except Exception as e:
                print(f'Ошибка создания файла: {e}')
        # Удалить файл: file delete <путь>
        elif cmd == 'file' and len(args) == 2 and args[0] == 'delete':
            try:
                if os.path.exists(args[1]):
                    os.remove(args[1])
                    print(f'Файл {args[1]} удалён.')
                else:
                    print(f'Файл {args[1]} не найден.')
            except Exception as e:
                print(f'Ошибка удаления файла: {e}')
        # Проверить файл: file exists <путь> <var>
        elif cmd == 'file' and len(args) == 3 and args[0] == 'exists':
            variables[args[2]] = '1' if os.path.exists(args[1]) else '0'
        else:
            print(f'Неизвестная команда: {line}')
        i += 1

def set_component_state(component, state):
    import json
    CONFIG_PATH = 'programs/config.json'
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = json.load(f)
        if component in config:
            config[component] = state
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f'Компонент {component} теперь {"включён" if state else "отключён"}.')
        else:
            print(f'Нет такого компонента: {component}')
    except Exception as e:
        print(f'Ошибка изменения компонента: {e}')

def main():
    import sys
    if len(sys.argv) < 2:
        print('Использование: python shell.py <путь_к_скрипту>')
        return
    if sys.argv[1] == 'wiki':
        print_wiki()
    else:
        run_shell_script(sys.argv[1])

if __name__ == '__main__':
    main()
