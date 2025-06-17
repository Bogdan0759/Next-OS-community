import os

def run_notebook():
    print("\n--- Блокнот ---")
    print("Введите текст построчно. Команды: 'save' для сохранения, 'exit' для выхода.")
    lines = []
    save_dir = "saves"
    save_file = os.path.join(save_dir, "notebook.txt")

    while True:
        line = input("> ")

        if line.lower() == 'exit':
            break
        elif line.lower() == 'save':
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            with open(save_file, "w", encoding="utf-8") as f:
                for l in lines:
                    f.write(l + "\n")
            print(f"Содержимое сохранено в {save_file}")
        else:
            lines.append(line)

    print("\nСодержимое блокнота:")
    for line in lines:
        print(line)
    print("-------------------\n")
