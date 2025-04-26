from microbit import *
import random

# Tetris for Micro:bit
# Use buttons A and B to move and rotate falling blocks

# Game variables
lives = 10
last_rotation_time = 0
rotation_cooldown = 500  # milliseconds
rotation_slowdown_duration = 2000  # 2 seconds slowdown after rotation
fall_speed = 1000  # base falling speed
slow_fall_speed = 2000  # slowed down speed during slowdown period
last_slowdown_end_time = 0  # time when slowdown ends
is_rotating = False  # flag for rotation state
board = [[0 for _ in range(5)] for _ in range(5)]  # 5x5 grid for the game
current_piece = None
piece_x = 0
piece_y = 0

# Define Tetris pieces (L, I, and Square shapes)
pieces = [
    [[1, 1, 1], [0, 0, 1]],  # L shape
    [[1, 1, 1, 1]],           # I shape
    [[1, 1], [1, 1]]          # Square shape
]

def spawn_piece():
    global current_piece, piece_x, piece_y
    r = random.random()
    if r < 0.05:
        current_piece = [[1, 1, 1, 1]]  # I shape with 5% probability
    elif r < 0.30:
        current_piece = [[0, 1, 0], [1, 1, 1]]  # T shape with 25% probability
    elif r < 0.55:
        current_piece = [[0, 1, 1], [1, 1, 0]]  # S shape with 25% probability
    elif r < 0.775:
        current_piece = [[1, 1, 1], [0, 0, 1]]  # L shape with 22.5% probability
    else:
        current_piece = [[1, 1], [1, 1]]  # Square shape with 22.5% probability
    piece_x = max(0, min(2, 5 - len(current_piece[0])))  # Adjusted starting position
    piece_y = 0
    if check_collision(piece_x, piece_y, current_piece):
        return False
    return True

def check_collision(x, y, piece):
    piece_height = len(piece)
    piece_width = len(piece[0])
    for py in range(piece_height):
        for px in range(piece_width):
            if piece[py][px]:
                new_x = x + px
                new_y = y + py
                if new_x < 0 or new_x >= 5 or new_y >= 5:
                    return True
                if new_y >= 0 and board[new_y][new_x]:
                    return True
    return False

def rotate_piece(piece):
    return [list(row) for row in zip(*piece[::-1])]

def merge_piece():
    global current_piece, piece_x, piece_y
    piece_height = len(current_piece)
    piece_width = len(current_piece[0])
    for py in range(piece_height):
        for px in range(piece_width):
            if current_piece[py][px]:
                board[piece_y + py][piece_x + px] = 1
    current_piece = None

def clear_lines():
    global board
    new_board = []
    for row in board:
        if not all(row):  # If row is not completely filled
            new_board.append(row)
    while len(new_board) < 5:
        new_board.insert(0, [0, 0, 0, 0, 0])  # Add empty rows at the top
    board = new_board

def update_display():
    board_brightness = 4  # Always dim for placed pieces
    piece_brightness = max(1, int((lives / 10.0) * 9))  # Brightness for current piece based on lives
    display.clear()
    if is_rotating:
        # Show border by lighting edge pixels
        for x in range(5):
            display.set_pixel(x, 0, 9)  # Top row
            display.set_pixel(x, 4, 9)  # Bottom row
        for y in range(5):
            display.set_pixel(0, y, 9)  # Left column
            display.set_pixel(4, y, 9)  # Right column
        # Avoid overwriting corners by setting them once
    # Show the board with fixed dim brightness
    for y in range(5):
        for x in range(5):
            if board[y][x]:
                display.set_pixel(x, y, board_brightness)
    # Show the current falling piece with lives-based brightness
    if current_piece:
        piece_height = len(current_piece)
        piece_width = len(current_piece[0])
        for py in range(piece_height):
            for px in range(piece_width):
                if current_piece[py][px]:
                    px_pos = piece_x + px
                    py_pos = piece_y + py
                    if 0 <= px_pos < 5 and 0 <= py_pos < 5:
                        display.set_pixel(px_pos, py_pos, piece_brightness)

# Initialize first piece
spawn_piece()

last_move = running_time()

while True:
    current_time = running_time()
    # Handle slowdown after rotation
    if current_time - last_slowdown_end_time < rotation_slowdown_duration:
        current_fall_speed = slow_fall_speed
    else:
        current_fall_speed = fall_speed
    if current_time - last_move > current_fall_speed:
        if current_piece:
            if not check_collision(piece_x, piece_y + 1, current_piece):
                piece_y += 1
            else:
                merge_piece()
                clear_lines()
                if not spawn_piece():
                    lives -= 1
                    if lives > 0:
                        # Flash the screen when losing a life
                        display.clear()
                        for y in range(5):
                            for x in range(5):
                                display.set_pixel(x, y, 9)  # Flash bright for 200ms
                        sleep(200)
                        display.clear()
                        # Reset board and spawn new piece
                        board = [[0 for _ in range(5)] for _ in range(5)]
                        spawn_piece()
                    else:
                        # Game over, show sad face and reset after a delay
                        display.show(Image.SAD)
                        sleep(2000)  # Wait 2 seconds
                        lives = 10  # Reset lives
                        board = [[0 for _ in range(5)] for _ in range(5)]
                        spawn_piece()
        last_move = current_time
    # Control piece using buttons A and B, rotate on both pressed with slowdown and border
    if button_a.was_pressed() and current_piece and not check_collision(piece_x - 1, piece_y, current_piece):
        piece_x -= 1
    if button_b.was_pressed() and current_piece and not check_collision(piece_x + 1, piece_y, current_piece):
        piece_x += 1
    if button_a.is_pressed() and button_b.is_pressed() and current_piece:
        if current_time - last_rotation_time > rotation_cooldown:
            rotated_piece = rotate_piece(current_piece)
            if not check_collision(piece_x, piece_y, rotated_piece):
                current_piece = rotated_piece
                last_rotation_time = current_time
                last_slowdown_end_time = current_time + rotation_slowdown_duration  # Set slowdown end time
                is_rotating = True  # Set rotation flag
            else:
                is_rotating = False  # Reset if rotation not possible
        else:
            is_rotating = False
    else:
        is_rotating = False  # Reset flag if buttons not pressed
    if is_rotating:
        # Keep border on during the rotation action, but since it's checked in update_display, no need for delay here
        pass
    update_display()
    sleep(50)  # Small delay to prevent flickering
