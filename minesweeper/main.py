from tkinter import *

current_difficulty = 'easy'
iteration = 0


def init_values(window, difficulty):
    size = {'easy': (300, 300), 'medium': (400, 400), 'hard': (600, 600)}

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


def init_difficulty(difficulty):
    if difficulty == 'easy':
        return None
    elif difficulty == 'medium':
        return None
    else:
        return None


def update_difficulty(difficulty, difficulty_label):
    global iteration
    if iteration == 3:
        ok = 0

    global current_difficulty
    current_difficulty = difficulty
    difficulty_label.config(text=difficulty)
    iteration += 1


# noinspection PyTypeChecker
def init_header(window):
    difficulty_label = Label(window, text="Current difficulty: " + current_difficulty)
    difficulty_label.grid(row=0, column=3, sticky=W, pady=2)

    easy_button = Button(window, text='Easy', command=update_difficulty('easy', difficulty_label))
    easy_button.grid(row=0, column=0, sticky=W, pady=2)

    medium_button = Button(window, text='Medium', command=update_difficulty('medium', difficulty_label))
    medium_button.grid(row=0, column=1, sticky=W, pady=2)

    hard_button = Button(window, text='Hard', command=update_difficulty('hard', difficulty_label))
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
