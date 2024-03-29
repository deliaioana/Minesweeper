"""This module starts a game of minesweeper with customizable rows, columns,
bombs and time in a tkinter window.
"""

import time as t
import random
from tkinter import *
from threading import Thread, Event
from time import perf_counter

WINDOW = Tk()
CANVAS = Canvas(WINDOW)
TIMER_ENTRY = Entry()
TIMER_THREAD = Thread()
TIME_LEFT = 0
TIME_TO_WAIT = 0
TIME_LABEL = Label()
THREAD_STOP = Event()
THREAD_STOP.clear()
REMAINING_FLAGS_LABEL = Label()

BOMBS = []
MATRIX_OF_STATES = []
NUMBERS = []
IN_GAME = False
GAME_FINISHED = False

COLORS = {'bg': '#6e8583', 'blocked-square-even': '#006D64', 'blocked-square-odd': '#004943',
          'open-square-odd': '#6db09f', 'open-square-even': '#70cfbd'}

CONSTANTS = {'number_of_rows': 8, 'number_of_columns': 8, 'number_of_bombs': 10, 'flag': '🚩', 'bomb': '💣',
             'question_mark': '?',
             'canvas_padding': 100, 'square_size': 20, 'header_height': 40, 'number_of_placed_flags': 0,
             'popup_height': 70, 'popup_width': 300, 'entry_width': 4, 'maximum_board_size': 30,
             'minimum_board_size': 4, 'maximum_number_of_seconds': 1000}

STATES = {'blocked': 0, 'unblocked': 1, 'flagged': 2, 'marked': 3}


def stop_thread():
    """Stops the global timer thread called TIMER_THREAD."""

    global THREAD_STOP
    THREAD_STOP.set()
    if TIMER_THREAD.is_alive():
        TIMER_THREAD.join()


def update_seconds():
    """Updates the second inside the global label for seconds called TIME_LABEL
    in a loop while the thread is still running."""

    global TIME_LEFT, THREAD_STOP
    start_time = perf_counter()

    while not THREAD_STOP.is_set():
        current_time = perf_counter()
        difference = int(current_time - start_time)
        TIME_LEFT = TIME_TO_WAIT - difference
        refresh_time_label()
        if TIME_LEFT <= 0:
            show_time_over_popup()
            break
        t.sleep(1)


def start_timer(time):
    """Starts a timer on a new thread for 'time' seconds.

    Parameters
    ----------
    time : int
        Time in seconds
    """

    global TIMER_THREAD, TIME_TO_WAIT, THREAD_STOP

    THREAD_STOP.clear()

    TIME_TO_WAIT = time
    TIMER_THREAD = Thread(target=update_seconds, daemon=True)
    TIMER_THREAD.start()


def update_custom_difficulty_and_restart(rows, columns, number_of_bombs):
    """Resets the game with 'rows' rows, 'columns' columns and
    'number_of_bombs' bombs and interrupts the current running game.
    Also starts the timer if required.

    Parameters
    ----------
    rows : str
        A string given as input intended to represent the number of rows
    columns : str
        A string given as input intended to represent the number of columns
    number_of_bombs : str
        A string given as input intended to represent the number of bombs
    """

    global IN_GAME

    stop_thread()

    if IN_GAME:
        reset_game()

        time = 0
        if is_valid_time(TIMER_ENTRY.get()):
            time = get_number(TIMER_ENTRY.get())
        if time != 0:
            start_timer(time)

    else:
        time = 0
        if is_valid_number_of_rows_or_columns(rows) and is_valid_number_of_rows_or_columns(columns):
            row_number = get_number(rows)
            column_number = get_number(columns)

            if is_valid_time(TIMER_ENTRY.get()):
                time = get_number(TIMER_ENTRY.get())

            if is_valid_number_of_bombs(number_of_bombs, row_number, column_number):
                IN_GAME = False

                init_values(row_number, column_number, get_number(number_of_bombs))
                update_board()

                if time != 0:
                    start_timer(time)


def get_square_from_coords(x, y):
    """Gets square coordinates in matrix from screen coordinates.

    Parameters
    ----------
    x : int
        Coordinate on Ox axis from a click on the board
    y : int
        Coordinate on Oy axis from a click on the board
    """

    square_size = CONSTANTS['square_size']
    return int(y/square_size), int(x/square_size)


def click_on_canvas(event):
    """Handles board left-clicks. They either start a new round or get handles
    in another function, if that square is not flagged as a bomb.

    Parameters
    ----------
    event : Event
        The click event on the board
    """

    x = CANVAS.canvasx(event.x)
    y = CANVAS.canvasy(event.y)

    square_coords = get_square_from_coords(x, y)

    global IN_GAME, GAME_FINISHED

    if not GAME_FINISHED:
        if not IN_GAME:
            IN_GAME = True
            GAME_FINISHED = False
            start_round(square_coords)
        elif MATRIX_OF_STATES[square_coords[0]][square_coords[1]] != STATES['flagged']:
            click_square(square_coords)


def place_flag(event):
    """Calls the function to place or remove flag on the computed square from
    the given coordinates.

    Parameters
    ----------
    event : Event
        The click event on the board
    """

    x = CANVAS.canvasx(event.x)
    y = CANVAS.canvasy(event.y)

    square_coords = get_square_from_coords(x, y)

    global IN_GAME
    if IN_GAME:
        IN_GAME = True
        place_or_erase_flag_on_square(square_coords)


def place_question_mark(event):
    """Calls the function to place or remove question mark on the computed
    square from the given coordinates.

    Parameters
    ----------
    event : Event
        The click event on the board
    """

    x = CANVAS.canvasx(event.x)
    y = CANVAS.canvasy(event.y)

    square_coords = get_square_from_coords(x, y)

    global IN_GAME
    if IN_GAME:
        IN_GAME = True
        place_or_erase_question_mark_on_square(square_coords)


def place_or_erase_question_mark_on_square(square_coords):
    """Places or removes an already placed question mark on a specific square.

    Parameters
    ----------
    square_coords : tuple
        Tuple that represents the coordinates of the square on the board
    """

    row, column = square_coords
    global CONSTANTS

    if MATRIX_OF_STATES[row][column] == STATES['blocked']:
        paint_text_inside_square(CONSTANTS['question_mark'], row, column)
        MATRIX_OF_STATES[row][column] = STATES['marked']

    elif MATRIX_OF_STATES[row][column] == STATES['marked']:
        erase_mark(row, column)
        MATRIX_OF_STATES[row][column] = STATES['blocked']


def place_or_erase_flag_on_square(square_coords):
    """Places or removes an already placed flag on a specific square.

    Parameters
    ----------
    square_coords : tuple
        Tuple that represents the coordinates of the square on the board
    """

    row, column = square_coords
    global CONSTANTS

    if MATRIX_OF_STATES[row][column] == STATES['blocked']:
        paint_text_inside_square(CONSTANTS['flag'], row, column)
        MATRIX_OF_STATES[row][column] = STATES['flagged']
        CONSTANTS['number_of_placed_flags'] += 1

    elif MATRIX_OF_STATES[row][column] == STATES['flagged']:
        CONSTANTS['number_of_placed_flags'] -= 1
        erase_mark(row, column)
        MATRIX_OF_STATES[row][column] = STATES['blocked']

    refresh_flag_label()


def count_flags():
    """Counts placed flags.

    Returns
    ----------
    int
        An integer that represents the number of flags that are currently on
        the board
    """

    count = 0
    for row in MATRIX_OF_STATES:
        for state in row:
            if state == STATES['flagged']:
                count += 1
    return count


def refresh_flag_label():
    """Refreshes flag label according to the current placed flags."""

    global CONSTANTS, REMAINING_FLAGS_LABEL
    CONSTANTS['number_of_placed_flags'] = count_flags()
    number_of_remaining_flags = CONSTANTS['number_of_bombs'] - CONSTANTS['number_of_placed_flags']
    flags = CONSTANTS['flag']
    REMAINING_FLAGS_LABEL.config(text=flags + ": " + str(number_of_remaining_flags))


def erase_mark(row, column):
    """Erases any mark from a blocked square.

    Parameters
    ----------
    row : int
        The row of a square inside the board
    column : int
        The column of a square inside the board
    """

    even_color = COLORS['blocked-square-even']
    odd_color = COLORS['blocked-square-odd']

    paint_square(row, column, even_color, odd_color)


def show_all_bombs():
    """Paints all bombs on top."""

    for bomb in BOMBS:
        row, column = bomb
        erase_mark(row, column)
        paint_text_inside_square(CONSTANTS['bomb'], row, column)


def click_square(square_coords):
    """Handles square left-clicks, and game completion in case of winning or
    losing by clicking a bomb.

    Parameters
    ----------
    square_coords : tuple
        Tuple that represents the coordinates of the square on the board
    """

    if square_coords in BOMBS:
        show_all_bombs()
        show_game_over_popup()
    else:
        clear_terrain(square_coords)
        if is_game_completed():
            show_all_bombs()
            show_winning_popup()


def is_game_completed():
    """Checks if the game is won by counting blocked position.

    Returns
    ----------
    bool
        A bool representing the state of the game
        (True = complete, False = incomplete)
    """

    number_of_unopened_squares = 0
    for i in range(len(MATRIX_OF_STATES)):
        for j in range(len(MATRIX_OF_STATES[0])):
            if MATRIX_OF_STATES[i][j] in [STATES['blocked'], STATES['flagged']]:
                number_of_unopened_squares += 1
    if number_of_unopened_squares == len(BOMBS):
        return True
    return False


def center_window(win, height, width):
    """Centers a window.

    Parameters
    ----------
    win : Window
        A window
    height : int
        The height of the window
    width : int
        The width of the window
    """

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()

    center_x = int(screen_width / 2 - width / 2)
    center_y = int(screen_height / 2 - height / 2)

    win.geometry(f'{width}x{height}+{center_x}+{center_y}')


def show_winning_popup():
    """Calls the popup loader with the appropriate message after winning the
    game."""

    show_popup("YOU WIN!")


def show_popup(finishing_message):
    """Displays a popup window showing that the game was finished and allowing
    the player to restart the game.

    Parameters
    ----------
    finishing_message : str
        The message that will be displayed on the popup window
    """

    global GAME_FINISHED
    GAME_FINISHED = True

    win = Toplevel(WINDOW)
    geometry = str(CONSTANTS['popup_height']) + 'x' + str(CONSTANTS['popup_width'])
    win.geometry(geometry)
    win.title("The end")

    center_window(win, CONSTANTS['popup_height'], CONSTANTS['popup_width'])

    label = Label(win, text=finishing_message)
    label.place(relx=0.5, rely=0.5, anchor=CENTER)

    restart = Button(win, text='Restart', command=lambda: reset_and_close_window(win))
    restart.pack(side="bottom")


def show_game_over_popup():
    """Calls the popup loader with the appropriate message after losing the
    game."""

    show_popup("GAME OVER!")


def reset_and_close_window(win):
    """Resets the current window and resets game values.

    Parameters
    ----------
    win : Window
        The window that will de refreshed
    """

    win.destroy()
    reset_game()


def reset_game():
    """Resets game values and updates the board."""

    global IN_GAME, GAME_FINISHED
    IN_GAME = False
    GAME_FINISHED = False

    init_values(CONSTANTS['number_of_rows'], CONSTANTS['number_of_columns'], CONSTANTS['number_of_bombs'])
    update_board()


def start_round(square_coords):
    """Initializes the round values, generates bombs and square numbers, clears terrain from clicked square.

    Parameters
    ----------
    square_coords : tuple
        Tuple that represents the coordinates of the square on the board
    """

    init_matrix_state()
    generate_bombs(square_coords)
    generate_numbers()
    clear_terrain(square_coords)


def generate_numbers():
    """Computes the number of bombs neighbouring each square and stores them
    globally."""

    global NUMBERS
    NUMBERS = []
    rows = CONSTANTS['number_of_rows']
    columns = CONSTANTS['number_of_columns']

    for i in range(rows):
        row_of_numbers = []
        for j in range(columns):
            number_of_bombs = get_number_of_bombs_next_to_coords(i, j)
            if (i, j) in BOMBS:
                row_of_numbers.append('X')
            else:
                row_of_numbers.append(number_of_bombs)
        NUMBERS.append(row_of_numbers)


def get_number_of_bombs_next_to_coords(row, column):
    """Computes the number of bombs next to a given square.

    Parameters
    ----------
    row : int
        The row of a square inside the board
    column : int
        The column of a square inside the board

    Returns
    ----------
    int
        An integer that represents the number of bombs adjacent to the given
        square
    """

    number_of_bombs = 0
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            neighbour_coords = row + i, column + j
            if is_inside_matrix(neighbour_coords) and neighbour_coords in BOMBS:
                number_of_bombs += 1
    return number_of_bombs


def init_matrix_state():
    """Initializes all matrix square states to 'blocked'."""

    global MATRIX_OF_STATES
    MATRIX_OF_STATES = []
    rows = CONSTANTS['number_of_rows']
    columns = CONSTANTS['number_of_columns']

    for i in range(rows):
        row_states = []
        for j in range(columns):
            row_states.append(STATES['blocked'])
        MATRIX_OF_STATES.append(row_states)


def is_inside_matrix(coords):
    """Checks if coordinates are not out of matrix bounds.

    Parameters
    ----------
    coords : tuple
        Tuple that represents the coordinates a square that may be on the
        board

    Returns
    ----------
    bool
        A bool showing if the given square coordinates are inside the board
        (True = inside the board, False = invalid square)
    """

    rows = CONSTANTS['number_of_rows']
    columns = CONSTANTS['number_of_columns']

    row, column = coords
    if row < 0 or column < 0 or row > rows-1 or column > columns-1:
        return False
    return True


def get_neighbours(coords):
    """Returns neighbouring squares for a given square.

    Parameters
    ----------
    coords : tuple
        Tuple that represents the coordinates of the square on the board

    Returns
    ----------
    list
        A list of tuples representing coordinates of squares that are
        adjacent to the given square
    """

    neighbours = []
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            neighbour = (coords[0] + i, coords[1] + j)
            if is_inside_matrix(neighbour):
                neighbours.append(neighbour)
    return neighbours


def get_new_empty_neighbours(visited, current_coords):
    """Returns unvisited horizontally or vertically linked squares with zero
    bombs as neighbours to a given one.

    Parameters
    ----------
    visited : list
        A list of already checked squares
    current_coords : tuple
        A tuple that represents the coordinates of the square on the board

    Return
    ----------
    list
        A list of tuples representing coordinates of squares that are adjacent
        to zero bombs, are not found inside the visited list, and are also
        adjacent to the given square
    """

    empty_neighbours = []
    for i, j in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        neighbour_coords = current_coords[0] + i, current_coords[1] + j
        if is_inside_matrix(neighbour_coords):
            if neighbour_coords not in BOMBS and neighbour_coords not in visited and \
                    NUMBERS[neighbour_coords[0]][neighbour_coords[1]] == 0:
                empty_neighbours.append(neighbour_coords)

    return empty_neighbours


def paint_square(row, column, even_color, odd_color):
    """Paints a square by matrix indexes with one of the two colors,
    resembling a chessboard.

    Parameters
    ----------
    row : int
        The row of a square inside the board
    column : int
        The column of a square inside the board
    even_color : str
        A string representing the color for the squares with even sum of
        indexes
    odd_color : str
        A string representing the color for the squares with odd sum of
        indexes
    """

    square_size = CONSTANTS['square_size']
    if (row + column) % 2 == 0:
        CANVAS.create_rectangle(column * square_size, row * square_size,
                                (column + 1) * square_size, (row + 1) * square_size, fill=even_color)
    else:
        CANVAS.create_rectangle(column * square_size, row * square_size,
                                (column + 1) * square_size, (row + 1) * square_size, fill=odd_color)


def get_square_number(row, column):
    """Returns the number of bomb neighbours for a given square.

    Parameters
    ----------
    row : int
        The row of a square inside the board
    column : int
        The column of a square inside the board

    Returns
    ---------
    int
        An integer representing the number of bombs adjacent to the given
        square
    """

    return NUMBERS[row][column]


def paint_text_inside_square(text, row, column):
    """Paints the given text inside a square given by index.

    Parameters
    ----------
    text : int
        The text that will be painted inside the given square
    row : int
        The row of a square inside the board
    column : int
        The column of a square inside the board

    Returns
    ---------
    int
        An integer representing the number of bombs adjacent to the given
        square
    """

    square_size = CONSTANTS['square_size']
    CANVAS.create_text(column * square_size + square_size / 2, row * square_size + square_size / 2, text=str(text))


def mark_open_states(list_of_squares):
    """Marks a list of squares as 'open' in the matrix of states.

    Parameters
    ----------
    list_of_squares : list
        The list of squares that will be unblocked logically
    """

    for row, column in list_of_squares:
        MATRIX_OF_STATES[row][column] = STATES['unblocked']


def clear_squares(list_of_squares):
    """Clears a list of squares visually and in the matrix of states.

    Parameters
    ----------
    list_of_squares : list
        The list of squares that will be unblocked visually and logically
    """

    mark_open_states(list_of_squares)

    even_color = COLORS['open-square-even']
    odd_color = COLORS['open-square-odd']

    for square in list_of_squares:
        row, column = square
        paint_square(row, column, even_color, odd_color)
        number = get_square_number(row, column)
        if number != 0:
            paint_text_inside_square(number, row, column)


def get_adjacent_empty_terrain(coords):
    """Returns terrain with zero bombs as neighbours, that is adjacent to the
    given square.

    Parameters
    ----------
    coords : tuple
        Tuple that represents the coordinates of the square on the board

    Returns
    ----------
    list
        A list of tuples representing coordinates of squares that are adjacent
        to zero bombs and are linked to the given square
    """

    q = [coords]
    index = 0

    while index < len(q):
        current_coords = q[index]
        neighbors = get_new_empty_neighbours(q, current_coords)
        q.extend(neighbors)
        index += 1

    return q


def get_adjacent_numbers(terrain):
    """Returns the list of squares that represents the outline with numbers of
    an empty terrain.

    Parameters
    ----------
    terrain : list
        A list of tuples representing coordinates of squares linked to each
        other and having zero bombs adjacent to them

    Returns
    ----------
    list
        A list of tuples representing coordinates of squares that are adjacent
        to the terrain, and to minimum one bomb, and that are not bombs
    """

    adjacent_squares = []
    rows = CONSTANTS['number_of_rows']
    columns = CONSTANTS['number_of_columns']

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

            if is_adjacent and (row, column) not in BOMBS:
                if is_only_diagonally_linked(row, column, terrain) and is_number(row, column):
                    adjacent_squares.append((row, column))

    return adjacent_squares


def is_only_diagonally_linked(row, column, terrain):
    """Checks if a given square is only diagonally linked to a terrain or not.

    Parameters
    ----------
    row : int
        The row of a square inside the board
    column : int
        The column of a square inside the board
    terrain : list
        A list of tuples representing coordinates of squares linked to each
        other and having zero bombs adjacent to them

    Returns
    ----------
    bool
        A bool that represents if a given square is only diagonally linked to
        the given terrain
    """

    for i, j in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
        coords = (row + i, column + j)
        if coords not in terrain:
            return True
    return False


def is_number(row, column):
    """Checks if a given square as a number of adjacent bombs, that is grater
    that 0.

    Parameters
    ----------
    row : int
        The row of a square inside the board
    column : int
        The column of a square inside the board

    Returns
    ----------
    bool
        A bool that represents if the given square is adjacent to minimum one
        bomb
        (True = is adjacent to minimum one bomb, False = is adjacent to zero bombs)
    """

    return NUMBERS[row][column] in range(1, 9)


def clear_terrain(square_coords):
    """Clears the given square, the empty terrain adjacent to it, and the
    outline that contains numbers.

    Parameters
    ----------
    square_coords : tuple
        Tuple that represents the coordinates of the square on the board
    """

    terrain_to_clear = [square_coords]

    if NUMBERS[square_coords[0]][square_coords[1]] == 0:
        empty_terrain = get_adjacent_empty_terrain(square_coords)
        adjacent_numbers = get_adjacent_numbers(empty_terrain)

        terrain_to_clear.extend(empty_terrain)
        terrain_to_clear.extend(adjacent_numbers)

    clear_squares(terrain_to_clear)
    refresh_flag_label()


def generate_bombs(square_coords):
    """Generates bombs random inside the matrix, but not on the given square
    or its neighbours.

    Parameters
    ----------
    square_coords : tuple
        Tuple that represents the coordinates of the square on the board
    """

    global BOMBS
    rows = CONSTANTS['number_of_rows']
    columns = CONSTANTS['number_of_columns']
    all_possible_positions = [(i, j) for i in range(rows) for j in range(columns)]
    all_possible_positions.remove(square_coords)

    row, column = square_coords
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            coords = row + i, column + j
            if coords in all_possible_positions:
                all_possible_positions.remove(coords)

    number_of_bombs = CONSTANTS['number_of_bombs']
    BOMBS = random.sample(list(set(all_possible_positions)), k=number_of_bombs)


def init_values(rows, columns, number_of_bombs):
    """Initializes board and window constants according to the given
    parameters.

    Parameters
    ----------
    rows : int
        The number of rows that the board will be updated to show
    columns : int
        The number of rows that the board will be updated to show
    number_of_bombs : int
        The number of bombs that the round will be updated to have
    """

    global CONSTANTS

    CONSTANTS['number_of_rows'] = rows
    CONSTANTS['number_of_columns'] = columns
    CONSTANTS['number_of_bombs'] = number_of_bombs

    window_width = CONSTANTS['square_size'] * columns + CONSTANTS['canvas_padding'] * 2
    window_height = CONSTANTS['square_size'] * rows + CONSTANTS['canvas_padding'] * 2
    WINDOW.title('Minesweeper')

    center_window(WINDOW, window_height, window_width)

    WINDOW.resizable(False, False)
    bg_color = COLORS['bg']
    WINDOW.configure(bg=bg_color)

    refresh_flag_label()


def init_board():
    """Initializes board sizes according to the constants, and attaches
    buttons to the board."""

    canvas_width = CONSTANTS['number_of_columns'] * CONSTANTS['square_size']
    canvas_height = CONSTANTS['number_of_rows'] * CONSTANTS['square_size']
    CANVAS.config(width=canvas_width, height=canvas_height)

    CANVAS.grid(row=1, column=0)
    CANVAS.place(relx=0.5, rely=0.5, anchor=CENTER)
    CANVAS.bind("<Button-1>", click_on_canvas)
    CANVAS.bind("<Button-2>", place_question_mark)
    CANVAS.bind("<Button-3>", place_flag)

    paint_squares()


def paint_squares():
    """Paints all the squares as blocked with tho colors, in a chessboard
    pattern."""

    rows = CONSTANTS['number_of_rows']
    columns = CONSTANTS['number_of_columns']
    even_color = COLORS['blocked-square-even']
    odd_color = COLORS['blocked-square-odd']

    for i in range(rows):
        for j in range(columns):
            paint_square(i, j, even_color, odd_color)


def update_board():
    """Resizes the board."""

    canvas_width = CONSTANTS['number_of_columns'] * CONSTANTS['square_size']
    canvas_height = CONSTANTS['number_of_rows'] * CONSTANTS['square_size']
    CANVAS.config(width=canvas_width, height=canvas_height)
    CANVAS.delete("all")
    paint_squares()


def is_valid_number_of_rows_or_columns(string):
    """Checks if the given string can be converted to a valid number of rows
    or columns for a functional board.

    Parameters
    ----------
    string : str
        A string given as input intended to represent the number of rows or
        columns

    Return
    ----------
    bool
        A bool that represents if the given string is a valid number of rows
        or columns for a round
        (True = valid, False = invalid)
    """

    try:
        number = int(string)
        if number in range(CONSTANTS['minimum_board_size'], CONSTANTS['maximum_board_size']):
            return True
        return False

    except ValueError:
        return False


def is_valid_number_of_bombs(number_of_bombs, rows, columns):
    """Checks if the given number of bombs is valid according to the board
    sizes.

    Parameters
    ----------
    number_of_bombs : str
        A string given as input intended to represent the number of bombs
    rows : int
        The number of rows that the board will be updated to show
    columns : int
        The number of rows that the board will be updated to show
    """

    try:
        number = int(number_of_bombs)
        if number in range(1, int(rows * columns / 2)):
            return True
        return False

    except ValueError:
        return False


def get_number(string):
    """Returns the number from a validated string.

    Parameters
    ----------
    string : str
        A string representing a number, given to be converted to int

    Return
    ----------
    int
        An integer representing the value expressed in the string
    """

    return int(string)


def is_valid_time(time):
    """Checks if the given time is a valid integer representing the number of
    seconds given to play a game.

    Parameters
    ----------
    time : str
        A string given as input intended to represent the number of seconds
        for the next round

    Return
    ----------
    bool
        A bool that represents if the given string expresses a valid number
        of seconds
    """

    try:
        number = int(time)
        if number in range(CONSTANTS['maximum_number_of_seconds']):
            return True
        return False

    except ValueError:
        return False


def refresh_time_label():
    """Refreshes the text inside the time label."""

    TIME_LABEL.config(text=str(TIME_LEFT))


def show_time_over_popup():
    """Calls the popup loader with the appropriate message after time has
    expired."""

    show_popup("TIME OVER! GAME OVER!")


def init_header():
    """Initializes the visual header with buttons, labels and entries."""

    global REMAINING_FLAGS_LABEL

    header_height = CONSTANTS['header_height']
    header = Canvas(WINDOW, width=WINDOW.winfo_screenwidth(), height=header_height)
    header.grid(row=0, column=0)

    rows_label = Label(header, text="Rows:")
    rows_entry = Entry(header, width=CONSTANTS['entry_width'])
    columns_label = Label(header, text="Columns:")
    columns_entry = Entry(header, width=CONSTANTS['entry_width'])
    bombs_label = Label(header, text="Bombs:")
    bombs_entry = Entry(header, width=CONSTANTS['entry_width'])
    number_of_remaining_flags = len(BOMBS) - CONSTANTS['number_of_placed_flags']
    flags = CONSTANTS['flag']
    REMAINING_FLAGS_LABEL = Label(header, text=flags + ": " + str(number_of_remaining_flags))

    start_button = Button(header, text='Start',
                          command=lambda: update_custom_difficulty_and_restart(
                              rows_entry.get(), columns_entry.get(), bombs_entry.get()))

    rows_label.pack(side=LEFT)
    rows_entry.pack(side=LEFT)
    columns_label.pack(side=LEFT)
    columns_entry.pack(side=LEFT)
    bombs_label.pack(side=LEFT)
    bombs_entry.pack(side=LEFT)
    REMAINING_FLAGS_LABEL.pack(side=LEFT)
    start_button.pack(side=LEFT)


def init_timer_section():
    """Initializes the visual row that contains the timer."""

    section_height = CONSTANTS['header_height']
    section = Canvas(WINDOW, width=WINDOW.winfo_screenwidth(), height=section_height)
    section.grid(row=1, column=0)

    global TIMER_ENTRY, TIME_LABEL
    timer_label = Label(section, text="Timer:")
    TIMER_ENTRY = Entry(section, width=CONSTANTS['entry_width'])
    TIME_LABEL = Label(section, text="Left: " + str(TIME_LEFT))

    timer_label.pack(side=LEFT)
    TIMER_ENTRY.pack(side=LEFT)
    TIME_LABEL.pack(side=LEFT)


def start_game():
    """Initializes the main game elements, both visual and logical."""

    init_values(CONSTANTS['number_of_rows'], CONSTANTS['number_of_columns'], CONSTANTS['number_of_bombs'])

    init_header()
    init_timer_section()
    init_board()

    WINDOW.mainloop()


start_game()
