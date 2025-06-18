import random
import time
from collections import deque

def clear_lines(board):
    lines_cleared = 0
    new_board = []
    for row in board:
        if '.' not in row:
            lines_cleared += 1
        else:
            new_board.append(row)

    # Добавляем новые пустые строки сверху
    for _ in range(lines_cleared):
        new_board.insert(0, ['.' for _ in range(len(board[0]))])

    return new_board, lines_cleared

def rotate_shape(shape):
    # Поворот фигуры на 90 градусов по часовой стрелке относительно центра (приближенно)
    # Находим минимальные координаты для нормализации
    min_x = min([x for y, x in shape])
    min_y = min([y for y, x in shape])

    # Нормализуем координаты (сдвигаем к (0,0))
    normalized_shape = [(y - min_y, x - min_x) for y, x in shape]

    # Находим максимальную координату для определения размера bounding box
    max_dim = max(max([y for y, x in normalized_shape]), max([x for y, x in normalized_shape]))

    # Поворачиваем: новые_y = старые_x, новые_x = max_dim - старые_y
    rotated_shape = [(x, max_dim - y) for y, x in normalized_shape]

    # Находим новые минимальные координаты после поворота
    min_x_rotated = min([x for y, x in rotated_shape])
    min_y_rotated = min([y for y, x in rotated_shape])

    # Сдвигаем обратно, чтобы верхний левый угол bounding box был в (0,0)
    # Это упрощенный подход, который может потребовать доработки для идеального поворота
    final_rotated_shape = [(y - min_y_rotated, x - min_x_rotated) for y, x in rotated_shape]

    return final_rotated_shape

def lock_shape(board, shape, position):
    for y, x in shape:
        board_y = position[0] + y
        board_x = position[1] + x
        if 0 <= board_y < len(board) and 0 <= board_x < len(board[0]):
            board[board_y][board_x] = '#' # Помечаем клетку как занятую

def check_collision(board, shape, position):
    for y, x in shape:
        board_y = position[0] + y
        board_x = position[1] + x
        # Проверка границ и занятых клеток
        if board_y < 0 or board_y >= len(board) or board_x < 0 or board_x >= len(board[0]) or board[board_y][board_x] != '.':
            return True
    return False

def draw_board(board, shape, position):
    display_board = [row[:] for row in board] # Создаем копию поля для отрисовки
    for y, x in shape:
        board_y = position[0] + y
        board_x = position[1] + x
        if 0 <= board_y < len(display_board) and 0 <= board_x < len(display_board[0]):
            display_board[board_y][board_x] = '#'

    for row in display_board:
        print(" ".join(row))
    print("-" * (len(board[0]) * 2 - 1))


# Define Tetris game logic here
def play_tetris():
    print("Запуск Тетриса...")

    # Настройки игры
    board_width = 10
    board_height = 15 # Уменьшаем высоту поля
    board = [['.' for _ in range(board_width)] for _ in range(board_height)]

    # Формы тетромино (упрощенное представление)
    shapes = {
        'I': [(0,0), (0,1), (0,2), (0,3)],
        'J': [(0,0), (1,0), (1,1), (1,2)],
        'L': [(0,2), (1,0), (1,1), (1,2)],
        'O': [(0,0), (0,1), (1,0), (1,1)],
        'S': [(0,1), (0,2), (1,0), (1,1)],
        'T': [(0,1), (1,0), (1,1), (1,2)],
        'Z': [(0,0), (0,1), (1,1), (1,2)],
    }

    # Инициализация первой фигуры
    current_shape_name = random.choice(list(shapes.keys()))
    current_shape = shapes[current_shape_name]
    current_position = [0, board_width // 2 - 2] # Начальная позиция вверху по центру

    score = 0 # Инициализация счета

    game_over = False

    while not game_over:
        # Отрисовка поля перед ходом
        draw_board(board, current_shape, current_position)
        print(f"Счет: {score}") # Вывод счета

        # Обработка ввода (движение, поворот)
        command = input("Введите команду (a: влево, d: вправо, w: повернуть, exit: выйти): ")

        if command == 'exit':
            game_over = True
            continue # Выходим из текущей итерации, чтобы завершить игру

        moved_or_rotated = False
        if command == 'a':
            potential_position = [current_position[0], current_position[1] - 1]
            if not check_collision(board, current_shape, potential_position):
                current_position = potential_position
                moved_or_rotated = True
        elif command == 'd':
            potential_position = [current_position[0], current_position[1] + 1]
            if not check_collision(board, current_shape, potential_position):
                current_position = potential_position
                moved_or_rotated = True
        elif command == 'w':
            rotated = rotate_shape(current_shape)
            if not check_collision(board, rotated, current_position):
                current_shape = rotated
                moved_or_rotated = True

        # Автоматическое движение фигуры вниз после любого действия пользователя
        # Происходит только если пользователь ввел допустимую команду
        if moved_or_rotated:
            new_position_down = [current_position[0] + 1, current_position[1]]

            # Проверка на столкновения после автоматического движения вниз
            if check_collision(board, current_shape, new_position_down):
                # Если есть столкновение, фигура считается приземлившейся
                lock_shape(board, current_shape, current_position) # Закрепляем фигуру на текущей позиции

                # Проверка на очистку линий
                board, cleared = clear_lines(board)
                score += cleared * 100 # Обновление счета

                # Спавним новую фигуру
                current_shape_name = random.choice(list(shapes.keys()))
                current_shape = shapes[current_shape_name]
                current_position = [0, board_width // 2 - 2] # Начальная позиция вверху по центру

                # Проверяем на столкование сразу после спавна (для определения конца игры)
                if check_collision(board, current_shape, current_position):
                    game_over = True
            else:
                current_position = new_position_down # Если нет столкновения, обновляем позицию

        # Простая задержка (можно регулировать скорость игры)
        time.sleep(0.1) # Небольшая задержка между ходами

    print("Игра окончена!")
    print(f"Финальный счет: {score}") # Вывод финального счета


def draw_snake_board(board, snake, food):
    display_board = [row[:] for row in board] # Создаем копию поля для отрисовки
    # Отрисовка змейки
    for segment_y, segment_x in snake:
        if 0 <= segment_y < len(display_board) and 0 <= segment_x < len(display_board[0]):
            display_board[segment_y][segment_x] = 'S' # 'S' для сегмента змейки
    # Отрисовка еды
    if food:
        if 0 <= food[0] < len(display_board) and 0 <= food[1] < len(display_board[0]):
            display_board[food[0]][food[1]] = 'F' # 'F' для еды

    for row in display_board:
        print(" ".join(row))
    print("-" * (len(board[0]) * 2 - 1))


def place_food(board, snake):
    while True:
        food_y = random.randint(0, len(board) - 1)
        food_x = random.randint(0, len(board[0]) - 1)
        # Проверяем, что еда не появилась на теле змейки
        if [food_y, food_x] not in snake:
            return [food_y, food_x]

def play_snake():
    print("Запуск Змейки...")

    # Настройки игры
    board_width = 20
    board_height = 10
    board = [['.' for _ in range(board_width)] for _ in range(board_height)]

    # Инициализация змейки (список координат [y, x])
    snake = [[board_height // 2, board_width // 2]]
    snake_direction = [0, 1] # Начальное направление: вправо [dy, dx]

    # Инициализация еды
    food_position = place_food(board, snake)

    score = 0 # Инициализация счета

    game_over = False
    while not game_over:
        # Отрисовка поля
        draw_snake_board(board, snake, food_position)
        print(f"Счет: {score}") # Вывод счета

        # Обработка ввода
        command = input("Введите команду (w: вверх, a: влево, s: вниз, d: вправо, exit: выйти): ")

        if command == 'exit':
            game_over = True
            continue # Выходим из текущей итерации, чтобы завершить игру

        if command == 'w' and snake_direction != [1, 0]:
            snake_direction = [-1, 0] # Вверх
        elif command == 'a' and snake_direction != [0, 1]:
            snake_direction = [0, -1] # Влево
        elif command == 's' and snake_direction != [-1, 0]:
            snake_direction = [1, 0] # Вниз
        elif command == 'd' and snake_direction != [0, -1]:
            snake_direction = [0, 1] # Вправо

        # Движение змейки
        head_y, head_x = snake[0]
        new_head = [head_y + snake_direction[0], head_x + snake_direction[1]]

        # Проверка столкновений (со стенами и самим собой)
        if (new_head[0] < 0 or new_head[0] >= board_height or
            new_head[1] < 0 or new_head[1] >= board_width or
            new_head in snake):
            game_over = True
            continue # Выходим из текущей итерации, так как игра окончена

        snake.insert(0, new_head)

        # Поедание еды
        if new_head == food_position:
            score += 10 # Увеличиваем счет
            food_position = place_food(board, snake) # Размещаем новую еду
        else:
            snake.pop() # Удаляем хвост, если еда не была съедена

        # Простая задержка
        time.sleep(0.3) # Регулировка скорости игры

    print("Игра Змейка окончена!")
    print(f"Финальный счет: {score}") # Вывод финального счета


def run_game_center():
    print("--- Game Center ---")
    print("Выберите игру:")
    print("1. Тетрис")
    print("2. Змейка")
    print("3. Назад")

    while True:
        choice = input("Ваш выбор: ")

        if choice == "1":
            play_tetris() # Вызов функции Тетриса
        elif choice == "2":
            play_snake() # Вызов функции Змейки
        elif choice == "3":
            print("Возврат в главное меню...")
            break
        else:
            print("Неверный ввод.")
