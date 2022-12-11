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


def get_square_from_coords(x, y):
    return int(y/square_size), int(x/square_size)


def click_on_canvas(event):
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)

    square_coords = get_square_from_coords(x, y)
    print("clicked square ", square_coords)

    global in_game
    if not in_game:
        in_game = True
        start_round(square_coords)


def start_round(square_coords):
    init_matrix_state()
    generate_bombs(square_coords)
    clear_terrain(square_coords)


def init_matrix_state():
    global matrix_states
    matrix_states = []
    board_size = size[current_difficulty][3]

    for i in range(board_size):
        row_states = []
        for j in range(board_size):
            row_states.append(0)
        matrix_states.extend(row_states)


def get_new_safe_neighbours(q, current_coords):
    return []


def clear_squares(list_of_squares):
    pass


def clear_terrain(square_coords):
    q = [square_coords]
    index = 0

    while len(q) > 0:
        current_coords = q[index]
        neighbors = get_new_safe_neighbours(q, current_coords)
        q.extend(neighbors)
        index += 1

    clear_squares(q)


def generate_bombs(square_coords):
    global bombs
    board_size = size[current_difficulty][3]
    all_possible_positions = [(i, j) for i in range(board_size) for j in range(board_size)]
    all_possible_positions.remove(square_coords)
    number_of_bombs = size[current_difficulty][4]
    bombs = random.choices(all_possible_positions, k=number_of_bombs)
    print(bombs)


def init_values(difficulty):
    window_width = size[difficulty][0]
    window_height = size[difficulty][1]

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    window.title('Minesweeper')
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    window.resizable(False, False)
    window.configure(bg='#6e8583')


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

    for i in range(number_of_squares):
        for j in range(number_of_squares):
            if (i + j) % 2 == 0:
                canvas.create_rectangle(i*square_size, j*square_size,
                                        (i+1)*square_size, (j+1)*square_size, fill="#006D64")
            else:
                canvas.create_rectangle(i*square_size, j*square_size,
                                        (i+1)*square_size, (j+1)*square_size, fill="#004943")


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

    return easy_button, medium_button, hard_button, difficulty_label


def start_game():
    initial_difficulty = 'easy'
    init_values(initial_difficulty)

    easy_button, medium_button, hard_button, difficulty_label = init_header()
    init_board()

    window.mainloop()


start_game()
