COLORS = [
    '\033[38;5;1m',   # Red
    '\033[38;5;2m',   # Green
    '\033[38;5;3m',   # Yellow
    '\033[38;5;4m',   # Blue
    '\033[38;5;5m',   # Magenta
    '\033[38;5;6m',   # Cyan
    '\033[38;5;7m',   # Light Gray
    '\033[38;5;8m',   # Dark Gray
    '\033[38;5;9m',   # Bright Red
    '\033[38;5;10m',  # Bright Green
    '\033[38;5;11m',  # Bright Yellow
    '\033[38;5;12m',  # Bright Blue
    '\033[38;5;13m',  # Bright Magenta
    '\033[38;5;14m',  # Bright Cyan
    '\033[38;5;15m',  # White
    '\033[38;5;220m', # Golden Yellow
    '\033[38;5;25m',  # Dodger Blue
    '\033[38;5;23m',  # Deep Sky Blue
]




def pprint(problem, assignment):
    import math

    # Constants
    SPACER = 3 + math.floor(math.log10(max(cage.target for cage in problem)))
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz@#$^&~;]"

    # Create quick lookup tables
    cell_to_cage = {cell: cage for cage in problem.cages for cell in cage.cells}

    operator_cell = {
        cage: sorted(cage.cells, key=lambda cell: (cell[0], cell[1]))[0]
        for cage in problem.cages
    }

    # Print the board
    for row in range(problem.N):
        for col in range(problem.N):
            cage = cell_to_cage[(row, col)]
            digit = assignment[cage][cage.cells.index((row,col))]
            op = cage.op
            color = COLORS[cage.id % len(COLORS)]  # Use a color from the COLORS palette
            print(f'{color}', end='')  # Apply color to output

            if (row, col) == operator_cell[cage]:
                target = str(cage.target)
                print(f'{target + op:<{SPACER}}', end='')  # Print target and operator
            else:
                print(' ' * SPACER, end='')  # Spacer for alignment
            print(f'{digit} \033[0m', end='  ')  # Reset color after digit
        print(' ' * SPACER, end = '')
        for col in range(problem.N):
            cage = cell_to_cage[(row, col)]
            color = COLORS[cage.id % len(COLORS)]
            letter = ALPHABET[cage.id % len(ALPHABET)]
            print(f'{color}{letter}', end = ' ')
        print()  # Newline after each row

    # Reset terminal color at the end
    print('\033[0m'); print('\033[49m')