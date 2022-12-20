import time as t
import random
from tkinter import *
from threading import Timer, Thread, Event
from time import perf_counter

window = Tk()
canvas = Canvas(window)
timer_entry = Entry()
timer = Timer(0, int)
timer_thread = Thread()
time_left = 0
time_to_wait = 0
time_label = Label()
thread_running = Event()
remaining_flags_label = Label()

bombs = []
matrix_states = []
numbers = []
in_game = False
game_finished = False

colors = {'bg': '#6e8583', 'blocked-square-even': '#006D64', 'blocked-square-odd': '#004943',
          'open-square-odd': '#6db09f', 'open-square-even': '#70cfbd'}

constants = {'number_of_rows': 8, 'number_of_columns': 8, 'number_of_bombs': 10, 'flag': '🚩', 'bomb': '💣',
             'question_mark': '?',
             'canvas_padding': 100, 'square_size': 20, 'header_height': 40, 'number_of_placed_flags': 0,
             'popup_height': 70, 'popup_width': 300}

size = {'easy': (300, 300, 0, 8, 10), 'medium': (400, 400, 1, 15, 40), 'hard': (600, 600, 2, 20, 60)}


def get_square_from_coords(x, y):
    """Gets square coordinates in matrix from screen coordinates."""

    square_size = constants['square_size']
    return int(y/square_size), int(x/square_size)


def click_on_canvas(event):
    """Handles board left-clicks. They either start a new round or get handles in another function,
    if that square is not flagged as a bomb."""

    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)

    square_coords = get_square_from_coords(x, y)

    global in_game, game_finished

    if not game_finished:
        if not in_game:
            in_game = True
            game_finished = False
            start_round(square_coords)
        elif matrix_states[square_coords[0]][square_coords[1]] != 2:
            click_square(square_coords)


def place_flag(event):
    """Calls the function to place or remove flag on the computed square from the given coordinates."""

    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)

    square_coords = get_square_from_coords(x, y)

    global in_game
    if in_game:
        in_game = True
        place_or_erase_flag_on_square(square_coords)


def place_question_mark(event):
    """Calls the function to place or remove question mark on the computed square from the given coordinates."""

    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)

    square_coords = get_square_from_coords(x, y)

    global in_game
    if in_game:
        in_game = True
        place_or_erase_question_mark_on_square(square_coords)


def place_or_erase_question_mark_on_square(square_coords):
    """Places or removes an already placed question mark on a specific square."""

    row, column = square_coords
    global constants

    if matrix_states[row][column] == 0:
        paint_text_inside_square(constants['question_mark'], row, column)
        matrix_states[row][column] = 3

    elif matrix_states[row][column] == 3:
        erase_mark(row, column)
        matrix_states[row][column] = 0


def place_or_erase_flag_on_square(square_coords):
    """Places or removes an already placed flag on a specific square."""

    row, column = square_coords
    global constants

    if matrix_states[row][column] == 0:
        paint_text_inside_square(constants['flag'], row, column)
        matrix_states[row][column] = 2
        constants['number_of_placed_flags'] += 1

    elif matrix_states[row][column] == 2:
        constants['number_of_placed_flags'] -= 1
        erase_mark(row, column)
        matrix_states[row][column] = 0

    refresh_flag_label()


def count_flags():
    """Counts placed flags."""

    count = 0
    for row in matrix_states:
        for state in row:
            if state == 2:
                count += 1
    return count


def refresh_flag_label():
    """Refreshes flag label according to the current placed flags."""

    global constants, remaining_flags_label
    constants['number_of_placed_flags'] = count_flags()
    number_of_remaining_flags = constants['number_of_bombs'] - constants['number_of_placed_flags']
    flags = constants['flag']
    remaining_flags_label.config(text=flags + ": " + str(number_of_remaining_flags))


def erase_mark(row, column):
    """Erases any mark from a blocked square."""

    even_color = colors['blocked-square-even']
    odd_color = colors['blocked-square-odd']

    paint_square(row, column, even_color, odd_color)


def show_all_bombs():
    """Paints all bombs on top."""

    for bomb in bombs:
        row, column = bomb
        erase_mark(row, column)
        paint_text_inside_square(constants['bomb'], row, column)
    t.sleep(2)


def click_square(square_coords):
    """Handles square left-clicks, and game completion in case of winning or losing by clicking a bomb."""

    if square_coords in bombs:
        show_all_bombs()
        show_game_over_popup()
    else:
        clear_terrain(square_coords)
        if is_game_completed():
            show_all_bombs()
            show_winning_popup()

    print_matrix(matrix_states)


def is_game_completed():
    """Checks if the game is won by counting blocked position."""

    number_of_unopened_squares = 0
    for i in range(len(matrix_states)):
        for j in range(len(matrix_states[0])):
            if matrix_states[i][j] in [0, 2]:
                number_of_unopened_squares += 1
    if number_of_unopened_squares == len(bombs):
        return True
    return False


def center_window(win, height, width):
    """Centers a window."""

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    center_x = int(screen_width / 2 - width / 2)
    center_y = int(screen_height / 2 - height / 2)

    win.geometry(f'{width}x{height}+{center_x}+{center_y}')


def show_winning_popup():
    """Calls the popup loader with the appropriate message after winning the game."""

    show_popup("YOU WIN!")


def show_popup(finishing_message):
    """Displays a popup window showing that the game was finished and allowing the player to restart the game."""

    global game_finished, timer
    game_finished = True
    timer.cancel()

    win = Toplevel(window)
    geometry = str(constants['popup_height']) + 'x' + str(constants['popup_width'])
    win.geometry(geometry)
    win.title("The end")

    center_window(win, constants['popup_height'], constants['popup_width'])

    label = Label(win, text=finishing_message)
    label.place(relx=0.5, rely=0.5, anchor=CENTER)

    restart = Button(win, text='Restart', command=lambda: reset_and_close_window(win))
    restart.pack(side="bottom")


def show_game_over_popup():
    """Calls the popup loader with the appropriate message after losing the game."""

    show_popup("GAME OVER!")


def reset_and_close_window(win):
    """Resets the current window and resets game values."""

    win.destroy()
    reset_game()


def reset_game():
    """Resets game values and updates the board."""

    global in_game, game_finished
    in_game = False
    game_finished = False

    init_values(constants['number_of_rows'], constants['number_of_columns'], constants['number_of_bombs'])
    update_board()


def start_round(square_coords):
    """Initializes the round values, generates bombs and square numbers, clears terrain from clicked square."""

    init_matrix_state()
    generate_bombs(square_coords)
    generate_numbers()
    clear_terrain(square_coords)


def print_matrix(matrix):
    print("------------------------------------------")
    for row in matrix:
        print(row)


def generate_numbers():
    """Computes the number of bombs neighbouring each square and stores them globally."""

    global numbers
    numbers = []
    rows = constants['number_of_rows']
    columns = constants['number_of_columns']

    for i in range(rows):
        row_of_numbers = []
        for j in range(columns):
            number_of_bombs = get_number_of_bombs_next_to_coords(i, j)
            if (i, j) in bombs:
                row_of_numbers.append('X')
            else:
                row_of_numbers.append(number_of_bombs)
        numbers.append(row_of_numbers)


def get_number_of_bombs_next_to_coords(row, column):
    """Computes the number of bombs next to a given square."""

    number_of_bombs = 0
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            neighbour_coords = row + i, column + j
            if is_inside_matrix(neighbour_coords) and neighbour_coords in bombs:
                number_of_bombs += 1
    return number_of_bombs


def init_matrix_state():
    """Initializes all matrix square states to 'blocked'."""

    global matrix_states
    matrix_states = []
    rows = constants['number_of_rows']
    columns = constants['number_of_columns']

    for i in range(rows):
        row_states = []
        for j in range(columns):
            row_states.append(0)
        matrix_states.append(row_states)


def is_inside_matrix(coords):
    """Checks if coordinates are not out of matrix bounds."""

    rows = constants['number_of_rows']
    columns = constants['number_of_columns']

    row, column = coords
    if row < 0 or column < 0 or row > rows-1 or column > columns-1:
        return False
    return True


def get_neighbours(coords):
    """Returns neighbouring squares for a given square."""

    neighbours = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            neighbour = (coords[0] + i, coords[1] + j)
            if is_inside_matrix(neighbour):
                neighbours.append(neighbour)
    return neighbours


def get_new_empty_neighbours(visited, current_coords):
    """Returns unvisited horizontally or vertically linked squares with zero bombs as neighbours to a given one."""

    empty_neighbours = []
    for i, j in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        neighbour_coords = current_coords[0] + i, current_coords[1] + j
        if is_inside_matrix(neighbour_coords):
            if neighbour_coords not in bombs and neighbour_coords not in visited and \
                    numbers[neighbour_coords[0]][neighbour_coords[1]] == 0:
                empty_neighbours.append(neighbour_coords)

    return empty_neighbours


def paint_square(row, column, even_color, odd_color):
    """Paints a square by matrix indexes with one of the two colors, resembling a chessboard."""

    square_size = constants['square_size']
    if (row + column) % 2 == 0:
        canvas.create_rectangle(column * square_size, row * square_size,
                                (column + 1) * square_size, (row + 1) * square_size, fill=even_color)
    else:
        canvas.create_rectangle(column * square_size, row * square_size,
                                (column + 1) * square_size, (row + 1) * square_size, fill=odd_color)


def get_square_number(row, column):
    """Returns the number of bomb neighbours for a given square."""

    return numbers[row][column]


def paint_text_inside_square(number, row, column):
    """Paints the given text inside a square given by index."""

    square_size = constants['square_size']
    canvas.create_text(column * square_size + square_size / 2, row * square_size + square_size / 2, text=str(number))


def mark_open_states(list_of_squares):
    """Marks a list of squares as 'open' in the matrix of states."""

    for row, column in list_of_squares:
        matrix_states[row][column] = 1


def clear_squares(list_of_squares):
    """Clears a list of squares visually and in the matrix of states."""

    mark_open_states(list_of_squares)

    even_color = colors['open-square-even']
    odd_color = colors['open-square-odd']

    for square in list_of_squares:
        row, column = square
        paint_square(row, column, even_color, odd_color)
        number = get_square_number(row, column)
        if number != 0:
            paint_text_inside_square(number, row, column)


def get_adjacent_empty_terrain(coords):
    """Returns terrain with zero bombs as neighbours, that is adjacent to the given square."""

    q = [coords]
    index = 0

    while index < len(q):
        current_coords = q[index]
        neighbors = get_new_empty_neighbours(q, current_coords)
        q.extend(neighbors)
        index += 1

    return q


def get_adjacent_numbers(terrain):
    """Returns the list of squares that represents the outline with numbers of an empty terrain."""

    adjacent_squares = []
    rows = constants['number_of_rows']
    columns = constants['number_of_columns']

    for row in range(rows):
        for column in range(columns):
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
    """Checks if a given square is only diagonally linked to a terrain or not."""

    for i, j in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        coords = (row + i, column + j)
        if coords not in terrain:
            return True
    return False


def is_number(row, column):
    """Checks if a given square as a number of adjacent bombs, that is grater that 0."""

    return numbers[row][column] in range(1, 9)


def clear_terrain(square_coords):
    """Clears the given square, the empty terrain adjacent to it, and the outline that contains numbers."""

    terrain_to_clear = [square_coords]

    if numbers[square_coords[0]][square_coords[1]] == 0:
        empty_terrain = get_adjacent_empty_terrain(square_coords)
        adjacent_numbers = get_adjacent_numbers(empty_terrain)

        terrain_to_clear.extend(empty_terrain)
        terrain_to_clear.extend(adjacent_numbers)

    clear_squares(terrain_to_clear)
    refresh_flag_label()


def generate_bombs(square_coords):
    """Generates bombs random inside the matrix, but not on the given square or its neighbours."""

    global bombs
    rows = constants['number_of_rows']
    columns = constants['number_of_columns']
    all_possible_positions = [(i, j) for i in range(rows) for j in range(columns)]
    all_possible_positions.remove(square_coords)

    row, column = square_coords
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            coords = row + i, column + j
            if coords in all_possible_positions:
                all_possible_positions.remove(coords)

    number_of_bombs = constants['number_of_bombs']
    bombs = random.choices(all_possible_positions, k=number_of_bombs)


def init_values(rows, columns, number_of_bombs):
    """Initializes board and window constants according to the given parameters."""

    global constants

    constants['number_of_rows'] = rows
    constants['number_of_columns'] = columns
    constants['number_of_bombs'] = number_of_bombs

    window_width = constants['square_size'] * columns + constants['canvas_padding'] * 2
    window_height = constants['square_size'] * rows + constants['canvas_padding'] * 2
    window.title('Minesweeper')

    center_window(window, window_height, window_width)

    window.resizable(False, False)
    bg_color = colors['bg']
    window.configure(bg=bg_color)

    refresh_flag_label()


def init_board():
    """Initializes board sizes according to the constants, and attaches buttons to the board."""

    canvas_width = constants['number_of_columns'] * constants['square_size']
    canvas_height = constants['number_of_rows'] * constants['square_size']
    canvas.config(width=canvas_width, height=canvas_height)

    canvas.grid(row=1, column=0)
    canvas.place(relx=0.5, rely=0.5, anchor=CENTER)
    canvas.bind("<Button-1>", click_on_canvas)
    canvas.bind("<Button-2>", place_question_mark)
    canvas.bind("<Button-3>", place_flag)

    paint_squares()


def paint_squares():
    """Paints all the squares as blocked with tho colors, in a chessboard pattern."""

    rows = constants['number_of_rows']
    columns = constants['number_of_columns']
    even_color = colors['blocked-square-even']
    odd_color = colors['blocked-square-odd']

    for i in range(rows):
        for j in range(columns):
            paint_square(i, j, even_color, odd_color)


def update_board():
    """Resizes the board."""

    canvas_width = constants['number_of_columns'] * constants['square_size']
    canvas_height = constants['number_of_rows'] * constants['square_size']
    canvas.config(width=canvas_width, height=canvas_height)
    canvas.delete("all")
    paint_squares()


def is_valid_number(string):
    """Checks if the given string can be converted to a valid number of rows or columns for a functional board."""

    try:
        number = int(string)
        if number in range(4, 30):
            return True
        return False

    except ValueError:
        return False


def is_valid_number_of_bombs(number_of_bombs, rows, columns):
    """Checks if the given number of bombs is valid according to the board sizes."""

    try:
        number = int(number_of_bombs)
        if number in range(1, rows * columns):
            return True
        return False

    except ValueError:
        return False


def stop_thread():
    """Stops the time thread."""

    global thread_running

    print("thread running: ", thread_running)
    if thread_running:
        thread_running = False
        timer_thread.join()


def get_number(string):
    """Returns the number from a validated string."""

    return int(string)


def is_valid_time(time):
    """Checks if the given time is a valid integer representing the number of seconds given to play a game."""

    try:
        number = int(time)
        if number in range(1000):
            return True
        return False

    except ValueError:
        return False


def update_custom_difficulty_and_restart(rows, columns, number_of_bombs):
    """Resets the game according and interrupts the current running game. Also starts the timer if required."""

    global in_game

    stop_thread()

    if in_game:
        reset_game()
    else:
        time = 0
        if is_valid_number(rows) and is_valid_number(columns):
            row_number = get_number(rows)
            column_number = get_number(columns)

            if is_valid_time(timer_entry.get()):
                time = get_number(timer_entry.get())
                print("time: ", time)

            if is_valid_number_of_bombs(number_of_bombs, row_number, column_number):
                in_game = False

                init_values(row_number, column_number, get_number(number_of_bombs))
                update_board()

                if time != 0:
                    start_timer(time)


def refresh_time_label():
    """Refreshed the text inside the time label."""

    time_label.config(text=str(time_left))


def update_seconds():
    """Updates the second inside a label in a loop while the thread is still running."""

    global time_left
    start_time = perf_counter()

    while thread_running:
        if game_finished:
            break
        current_time = perf_counter()
        difference = int(current_time - start_time)
        time_left = time_to_wait - difference
        print("time left: ", time_left)
        refresh_time_label()


def start_timer(time):
    """Starts a timer on a new thread."""

    print("start timer")
    global timer, timer_thread, time_to_wait, thread_running
    thread_running = True
    time_to_wait = time
    timer = Timer(time, show_time_over_popup)
    timer_thread = Thread(target=update_seconds)
    timer_thread.start()

    timer.start()


def show_time_over_popup():
    """Calls the popup loader with the appropriate message after time has expired."""

    print("time over")
    show_popup("TIME OVER! GAME OVER!")


# noinspection PyTypeChecker
def init_header():
    """Initializes the visual header with buttons, labels and entries."""

    global remaining_flags_label

    header_height = constants['header_height']
    header = Canvas(window, width=window.winfo_screenwidth(), height=header_height)
    header.grid(row=0, column=0)

    rows_label = Label(header, text="Rows:")
    rows_entry = Entry(header, width=4)
    columns_label = Label(header, text="Columns:")
    columns_entry = Entry(header, width=4)
    bombs_label = Label(header, text="Bombs:")
    bombs_entry = Entry(header, width=4)
    number_of_remaining_flags = len(bombs) - constants['number_of_placed_flags']
    flags = constants['flag']
    remaining_flags_label = Label(header, text=flags + ": " + str(number_of_remaining_flags))

    start_button = Button(header, text='Start',
                          command=lambda: update_custom_difficulty_and_restart(
                              rows_entry.get(), columns_entry.get(), bombs_entry.get()))

    rows_label.pack(side=LEFT)
    rows_entry.pack(side=LEFT)
    columns_label.pack(side=LEFT)
    columns_entry.pack(side=LEFT)
    bombs_label.pack(side=LEFT)
    bombs_entry.pack(side=LEFT)
    remaining_flags_label.pack(side=LEFT)
    start_button.pack(side=LEFT)


def init_timer_section():
    """Initializes the visual row that contains the timer."""

    section_height = constants['header_height']
    section = Canvas(window, width=window.winfo_screenwidth(), height=section_height)
    section.grid(row=1, column=0)

    global timer_entry, time_label
    timer_label = Label(section, text="Timer:")
    timer_entry = Entry(section, width=4)
    time_label = Label(section, text="Left: " + str(time_left))

    timer_label.pack(side=LEFT)
    timer_entry.pack(side=LEFT)
    time_label.pack(side=LEFT)


def start_game():
    """Initializes the main game elements, both visual and logical."""

    init_values(constants['number_of_rows'], constants['number_of_columns'], constants['number_of_bombs'])

    init_header()
    init_timer_section()
    init_board()

    window.mainloop()


start_game()
