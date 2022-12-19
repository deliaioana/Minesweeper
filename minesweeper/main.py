import time as t
import random
from tkinter import *

window = Tk()
current_difficulty = 'easy'
square_size = 20
row_height = 40
size = {'easy': (300, 300, 0, 8, 10), 'medium': (400, 400, 1, 15, 40), 'hard': (600, 600, 2, 20, 60)}
canvas = Canvas(window)
in_game = False
bombs = []
matrix_states = []
numbers = []
colors = {'bg': '#6e8583', 'blocked-square-even': '#006D64', 'blocked-square-odd': '#004943',
          'open-square-odd': '#6db09f', 'open-square-even': '#70cfbd'}


def get_square_from_coords(x, y):
    return int(y/square_size), int(x/square_size)


def click_on_canvas(event):
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)

    square_coords = get_square_from_coords(x, y)
    print("square clicked: ", square_coords)

    global in_game
    if not in_game:
        in_game = True
        start_round(square_coords)
    else:
        click_square(square_coords)


def show_all_bombs():
    for bomb in bombs:
        row, column = bomb
        paint_number_inside_square('X', row, column)
    t.sleep(2)


def click_square(square_coords):
    if square_coords in bombs:
        show_all_bombs()
        show_game_over_popup()
    else:
        clear_terrain(square_coords)
        if is_game_completed():
            show_all_bombs()
            show_winning_popup()


def is_game_completed():
    number_of_unopened_squares = 0
    for i in range(len(matrix_states)):
        for j in range(len(matrix_states[0])):
            if matrix_states[i][j] == 0:
                number_of_unopened_squares += 1
    if number_of_unopened_squares == len(bombs):
        return True
    return False


def center_window(win, height, width):
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    center_x = int(screen_width / 2 - width / 2)
    center_y = int(screen_height / 2 - height / 2)

    win.geometry(f'{width}x{height}+{center_x}+{center_y}')


def show_winning_popup():
    show_popup("YOU WIN!")


def show_popup(finishing_message):
    win = Toplevel(window)
    win.geometry("70x70")
    win.title("The end")

    center_window(win, 70, 70)

    label = Label(win, text=finishing_message)
    label.place(relx=0.5, rely=0.5, anchor=CENTER)

    restart = Button(win, text='Restart', command=lambda: reset_and_close_window(win))
    restart.pack(side="bottom")


def show_game_over_popup():
    show_popup("GAME OVER!")


def reset_and_close_window(win):
    win.destroy()
    reset_game()


def reset_game():
    global in_game
    in_game = False
    init_values(current_difficulty)
    update_board()


def start_round(square_coords):
    init_matrix_state()
    generate_bombs(square_coords)
    generate_numbers()
    clear_terrain(square_coords)


def generate_numbers():
    global numbers
    numbers = []
    board_size = size[current_difficulty][3]

    for i in range(board_size):
        row_of_numbers = []
        for j in range(board_size):
            number_of_bombs = get_number_of_bombs_next_to_coords(i, j)
            if (i, j) in bombs:
                row_of_numbers.append('X')
            else:
                row_of_numbers.append(number_of_bombs)
        numbers.append(row_of_numbers)


def get_number_of_bombs_next_to_coords(row, column):
    number_of_bombs = 0
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            neighbour_coords = row + i, column + j
            if is_inside_matrix(neighbour_coords) and neighbour_coords in bombs:
                number_of_bombs += 1
    return number_of_bombs


def init_matrix_state():
    global matrix_states
    matrix_states = []
    board_size = size[current_difficulty][3]

    for i in range(board_size):
        row_states = []
        for j in range(board_size):
            row_states.append(0)
        matrix_states.append(row_states)


def is_inside_matrix(coords):
    board_size = size[current_difficulty][3]
    row, column = coords
    if row < 0 or column < 0 or row > board_size-1 or column > board_size-1:
        return False
    return True


def get_neighbours(coords):
    neighbours = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            neighbour = (coords[0] + i, coords[1] + j)
            if is_inside_matrix(neighbour):
                neighbours.append(neighbour)
    return neighbours


def get_new_empty_neighbours(visited, current_coords):
    empty_neighbours = []
    for i, j in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        neighbour_coords = current_coords[0] + i, current_coords[1] + j
        if is_inside_matrix(neighbour_coords):
            if neighbour_coords not in bombs and neighbour_coords not in visited and \
                    numbers[neighbour_coords[0]][neighbour_coords[1]] == 0:
                empty_neighbours.append(neighbour_coords)

    return empty_neighbours


def paint_square(row, column, even_color, odd_color):
    if (row + column) % 2 == 0:
        canvas.create_rectangle(column * square_size, row * square_size,
                                (column + 1) * square_size, (row + 1) * square_size, fill=even_color)
    else:
        canvas.create_rectangle(column * square_size, row * square_size,
                                (column + 1) * square_size, (row + 1) * square_size, fill=odd_color)


def get_square_number(row, column):
    return numbers[row][column]


def paint_number_inside_square(number, row, column):
    canvas.create_text(column * square_size + square_size / 2, row * square_size + square_size / 2, text=str(number))


def mark_open_states(list_of_squares):
    for row, column in list_of_squares:
        matrix_states[row][column] = 1


def clear_squares(list_of_squares):
    mark_open_states(list_of_squares)

    even_color = colors['open-square-even']
    odd_color = colors['open-square-odd']

    for square in list_of_squares:
        row, column = square
        paint_square(row, column, even_color, odd_color)
        number = get_square_number(row, column)
        if number != 0:
            paint_number_inside_square(number, row, column)


def get_adjacent_empty_terrain(coords):
    q = [coords]
    index = 0

    while index < len(q):
        current_coords = q[index]
        neighbors = get_new_empty_neighbours(q, current_coords)
        q.extend(neighbors)
        index += 1

    return q


def get_adjacent_numbers(terrain):
    adjacent_squares = []
    board_size = size[current_difficulty][3]
    for row in range(board_size):
        for column in range(board_size):
            is_adjacent = False
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    coords = row + i, column + j
                    if coords in terrain and (row, column) not in terrain:
                        is_adjacent = True
                        break
                if is_adjacent:
                    break

            if is_adjacent and (row, column) not in bombs:
                if is_only_diagonally_linked(row, column, terrain) and is_number(row, column):
                    adjacent_squares.append((row, column))

    return adjacent_squares


def is_only_diagonally_linked(row, column, terrain):
    for i, j in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        coords = (row + i, column + j)
        if coords not in terrain:
            return True
    return False


def is_number(row, column):
    return numbers[row][column] in range(1, 9)


def clear_terrain(square_coords):
    terrain_to_clear = [square_coords]

    if numbers[square_coords[0]][square_coords[1]] == 0:
        empty_terrain = get_adjacent_empty_terrain(square_coords)
        adjacent_numbers = get_adjacent_numbers(empty_terrain)

        terrain_to_clear.extend(empty_terrain)
        terrain_to_clear.extend(adjacent_numbers)

    clear_squares(terrain_to_clear)


def generate_bombs(square_coords):
    global bombs
    board_size = size[current_difficulty][3]
    all_possible_positions = [(i, j) for i in range(board_size) for j in range(board_size)]
    all_possible_positions.remove(square_coords)

    row, column = square_coords
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            coords = row + i, column + j
            if coords in all_possible_positions:
                all_possible_positions.remove(coords)

    number_of_bombs = size[current_difficulty][4]
    bombs = random.choices(all_possible_positions, k=number_of_bombs)


def init_values(difficulty):
    window_width = size[difficulty][0]
    window_height = size[difficulty][1]
    window.title('Minesweeper')

    center_window(window, window_height, window_width)

    window.resizable(False, False)
    bg_color = colors['bg']
    window.configure(bg=bg_color)


def init_board():
    board_size = size[current_difficulty][3]
    canvas_size = board_size * square_size
    canvas.config(width=canvas_size, height=canvas_size)
    canvas.grid(row=1, column=0)
    canvas.place(relx=0.5, rely=0.5, anchor=CENTER)
    canvas.bind("<Button-1>", click_on_canvas)

    paint_squares()


def paint_squares():
    number_of_squares = size[current_difficulty][3]
    even_color = colors['blocked-square-even']
    odd_color = colors['blocked-square-odd']

    for i in range(number_of_squares):
        for j in range(number_of_squares):
            paint_square(i, j, even_color, odd_color)


def update_board():
    board_size = size[current_difficulty][3]
    canvas_size = board_size * square_size
    canvas.config(width=canvas_size, height=canvas_size)
    canvas.delete("all")
    paint_squares()


def update_difficulty(difficulty, difficulty_label):
    global current_difficulty, in_game
    in_game = False
    current_difficulty = difficulty
    difficulty_label.config(text="Current difficulty: " + difficulty)
    init_values(difficulty)
    update_board()


# noinspection PyTypeChecker
def init_header():
    header = Canvas(window, width=window.winfo_screenwidth(), height=row_height)
    header.grid(row=0, column=0)

    difficulty_label = Label(header, text="Current difficulty: " + current_difficulty)
    difficulty_label.grid(row=0, column=3, pady=2)

    easy_button = Button(header, text='Easy', command=lambda: update_difficulty('easy', difficulty_label))
    easy_button.grid(row=0, column=0, pady=2)

    medium_button = Button(header, text='Medium', command=lambda: update_difficulty('medium', difficulty_label))
    medium_button.grid(row=0, column=1, pady=2)

    hard_button = Button(header, text='Hard', command=lambda: update_difficulty('hard', difficulty_label))
    hard_button.grid(row=0, column=2, pady=2)


def start_game():
    initial_difficulty = 'easy'
    init_values(initial_difficulty)

    init_header()
    init_board()

    window.mainloop()


start_game()
