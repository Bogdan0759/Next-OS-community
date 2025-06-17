def run_calculator():
    print("\n--- Калькулятор ---")
    print("Введите математическое выражение (например, 2+2*3) или 'exit' для выхода.")
    while True:
        expression = input("> ")
        if expression.lower() == 'exit':
            break
        try:
            result = eval(expression)
            print(f"Результат: {result}")
        except Exception as e:
            print(f"Ошибка при вычислении: {e}")
    print("---------------------\n")
