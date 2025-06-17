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
