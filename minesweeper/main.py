from tkinter import *

current_difficulty = 'easy'
board_size = 10
number_of_squares = 8
square_size = 20


def init_values(window, difficulty):
    size = {'easy': (300, 300, 0), 'medium': (400, 400, 1), 'hard': (600, 600, 2)}

    window_width = size[difficulty][0]
    window_height = size[difficulty][1]

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    window.title('Minesweeper')
    window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    window.resizable(False, False)
    window.configure(bg='#2ca4a8')

    global board_size
    board_size = (size[difficulty][2] + 1) * number_of_squares

    init_board(window)


def init_board(window):
    size = board_size * square_size
    canvas = Canvas(window, width=size, height=size)
    canvas.create_rectangle(0, 0, 100, 100, fill="blue", outline='blue')


def init_difficulty(difficulty):
    if difficulty == 'easy':
        return None
    elif difficulty == 'medium':
        return None
    else:
        return None


def update_difficulty(window, difficulty, difficulty_label):
    global current_difficulty
    current_difficulty = difficulty
    difficulty_label.config(text=difficulty)
    init_values(window, difficulty)


# noinspection PyTypeChecker
def init_header(window):
    difficulty_label = Label(window, text="Current difficulty: " + current_difficulty)
    difficulty_label.grid(row=0, column=3, sticky=W, pady=2)

    easy_button = Button(window, text='Easy', command=lambda: update_difficulty(window, 'easy', difficulty_label))
    easy_button.grid(row=0, column=0, sticky=W, pady=2)

    medium_button = Button(window, text='Medium', command=lambda: update_difficulty(window, 'medium', difficulty_label))
    medium_button.grid(row=0, column=1, sticky=W, pady=2)

    hard_button = Button(window, text='Hard', command=lambda: update_difficulty(window, 'hard', difficulty_label))
    hard_button.grid(row=0, column=2, sticky=W, pady=2)

    return easy_button, medium_button, hard_button, difficulty_label


def start_game():
    window = Tk()

    initial_difficulty = 'easy'
    init_difficulty(initial_difficulty)
    init_values(window, initial_difficulty)

    easy_button, medium_button, hard_button, difficulty_label = init_header(window)

    window.mainloop()


start_game()
