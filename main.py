import asyncio
import curses
import random
import itertools

SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

def load_textures():
    """Подгрузка файлов корабля."""
    file_name = "./rocket_frames/"
    with open(file_name + "rocket_frame_1.txt") as f1:
        texture_1 = f1.read()
    with open(file_name + "rocket_frame_2.txt") as f2:
        texture_2 = f2.read()
    return [texture_1, texture_2]

def read_controls(canvas):
    """Чтение нажатии клавиш"""
    rows_direction = columns_direction = 0
    space_pressed = False

    key = canvas.getch()

    if key == UP_KEY_CODE:
        rows_direction = -1
    elif key == DOWN_KEY_CODE:
        rows_direction = 1
    elif key == RIGHT_KEY_CODE:
        columns_direction = 1
    elif key == LEFT_KEY_CODE:
        columns_direction = -1
    elif key == SPACE_KEY_CODE:
        space_pressed = True

    return rows_direction, columns_direction, space_pressed

def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Отрисовка/Стирание символов на холсте."""
    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0 or row >= rows_number:
            continue

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0 or column >= columns_number or symbol == ' ':
                continue

            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)

async def blink(canvas, row, column, symbol):
    """Моргание звёздочки."""
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(random.uniform(0.1, 1.0))

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(random.uniform(0.1, 1.0))

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(random.uniform(0.1, 1.0))

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(random.uniform(0.1, 1.0))

async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Анимация выстрела."""
    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'
    max_row, max_column = canvas.getmaxyx()
    curses.beep()

    while 1 < row < max_row - 1 and 1 < column < max_column - 1:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0.02)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed

import itertools

async def animate_spaceship(canvas, start_row, start_column, textures):
    """Анимация корабля с управлением и стрельбой."""
    canvas.nodelay(True)
    max_rows, max_columns = canvas.getmaxyx()
    SPEED = 10

    current_row, current_column = start_row, start_column
    frames = itertools.cycle(textures)

    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)

        frame = next(frames)
        frame_height = len(frame.splitlines())
        frame_width = max(len(line) for line in frame.splitlines())

        min_row = 1
        min_col = 1
        max_row = max_rows - frame_height - 1
        max_col = max_columns - frame_width - 1

        current_row = max(min_row, min(max_row, current_row + rows_direction * SPEED))
        current_column = max(min_col, min(max_col, current_column + columns_direction * SPEED))

        # информация для отладки
        # canvas.addstr(0, 0, f"row={current_row}, col={current_column}   ")
        # canvas.addstr(1, 0, f"screen={max_rows}x{max_columns}   ")

        draw_frame(canvas, current_row, current_column, frame)
        canvas.refresh()
        await asyncio.sleep(0.1)
        draw_frame(canvas, current_row, current_column, frame, negative=True)
        canvas.refresh()

        if space_pressed:
            asyncio.create_task(fire(canvas, current_row, current_column + frame_width // 2))

async def draw(canvas):
    """Отрисовка звёздочек и анимация корабля."""
    curses.curs_set(False)
    canvas.nodelay(True)
    canvas.border()

    symbols = ["*", ":", ".", "+"]
    max_rows, max_columns = canvas.getmaxyx()

    stars = [
        (random.randint(1, max_rows - 2), random.randint(1, max_columns - 2), random.choice(symbols))
        for _ in range(100)
    ]

    blink_coroutines = [blink(canvas, row, column, symbol) for row, column, symbol in stars]

    textures = load_textures()
    spaceship = animate_spaceship(canvas, max_rows // 2, max_columns // 2, textures)

    await asyncio.gather(*blink_coroutines, spaceship)

def main(canvas):
    asyncio.run(draw(canvas))

if __name__ == "__main__":
    curses.wrapper(main)
