def run_calculator():
    print("\n--- Калькулятор ---")
    expression = input("Введите математическое выражение (например, 2+2*3): ")
    try:
        result = eval(expression)
        print(f"Результат: {result}")
    except Exception as e:
        print(f"Ошибка при вычислении: {e}")
    print("---------------------\n")
