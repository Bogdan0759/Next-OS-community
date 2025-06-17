# Shell script interpreter for NextOS Community Edition
# Поддержка: первая строка должна быть 'shell script', команда 'shell wiki' выводит справку

def print_wiki():
    print("""
NextOS Shell Script Documentation
===============================

- Первая строка скрипта: shell script
- Поддерживаемые команды:
    echo <text>      — вывести текст
    add <a> <b>      — сложить два числа
    sub <a> <b>      — вычесть b из a
    mul <a> <b>      — умножить два числа
    div <a> <b>      — разделить a на b
    shell wiki       — показать эту справку

Пример скрипта:
shell script
echo Hello, world!
add 2 3
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
        elif cmd == 'shell' and args and args[0] == 'wiki':
            print_wiki()
        else:
            print(f'Неизвестная команда: {line}')
        i += 1

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
