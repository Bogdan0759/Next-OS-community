import time

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
