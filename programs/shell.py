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
    with open(path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    if not lines or lines[0] != 'shell script':
        print('Ошибка: первая строка должна быть "shell script"')
        return
    for line in lines[1:]:
        parts = line.split()
        if not parts:
            continue
        cmd, *args = parts
        if cmd == 'echo':
            print(' '.join(args))
        elif cmd == 'add' and len(args) == 2:
            print(float(args[0]) + float(args[1]))
        elif cmd == 'sub' and len(args) == 2:
            print(float(args[0]) - float(args[1]))
        elif cmd == 'mul' and len(args) == 2:
            print(float(args[0]) * float(args[1]))
        elif cmd == 'div' and len(args) == 2:
            try:
                print(float(args[0]) / float(args[1]))
            except ZeroDivisionError:
                print('Ошибка: деление на ноль')
        elif cmd == 'shell' and args and args[0] == 'wiki':
            print_wiki()
        else:
            print(f'Неизвестная команда: {line}')

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
