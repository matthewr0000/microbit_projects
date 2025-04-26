from microbit import *
import random

# Tetris for Micro:bit
# Use buttons A and B to move and rotate falling blocks

# Game variables
lives = 10
last_rotation_time = 0
rotation_cooldown = 500  # milliseconds
level = 1  # Starts at level 1
lines_cleared_total = 0  # Total lines cleared to track level
fall_speed_base = 1000  # base falling speed in ms
board = [[0 for _ in range(5)] for _ in range(7)]  # 7 rows with 2 hidden above
current_piece = None
piece_x = 0
piece_y = 0
last_move = running_time()

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
                if new_x < 0 or new_x >= 5 or new_y >= 7:  # Updated y bound to 7 for larger board
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
    global board, lines_cleared_total, level
    lines_cleared_this_call = 0
    new_board = []
    for row in board:
        if not all(row):  # If not completely filled
            new_board.append(row)
        else:
            lines_cleared_this_call += 1
    lines_cleared_total += lines_cleared_this_call
    # Update level every 5 lines cleared
    if lines_cleared_total // 5 >= level:
        level += 1
    while len(new_board) < 7:  # Ensure board has 7 rows
        new_board.insert(0, [0, 0, 0, 0, 0])
    board = new_board
    return lines_cleared_this_call  # Return for potential future use, but not needed here

def update_display():
    current_time = running_time()
    board_brightness = 4  # Always dim for placed pieces
    piece_brightness = max(1, int((lives / 10.0) * 9))  # Normal brightness based on lives
    display.clear()
    # Show only visible rows (game y=2 to 6), mapped to display y=0 to 4
    for display_y in range(5):
        game_y = display_y + 2  # Map display y to game y
        for x in range(5):
            if board[game_y][x]:
                display.set_pixel(x, display_y, board_brightness)
    # Show the current falling piece with appropriate brightness, only if in visible range
    if current_piece:
        piece_height = len(current_piece)
        piece_width = len(current_piece[0])
        for py in range(piece_height):
            for px in range(piece_width):
                if current_piece[py][px]:
                    px_pos = piece_x + px
                    py_pos = piece_y + py
                    if 0 <= px_pos < 5 and 0 <= py_pos < 7 and 2 <= py_pos <= 6:  # Check full bounds and visible range
                        display_x = px_pos
                        display_y = py_pos - 2  # Map game y to display y
                        display.set_pixel(display_x, display_y, piece_brightness)

# Initialize first piece
spawn_piece()

while True:
    current_time = running_time()
    # Calculate fall speed based on level
    current_fall_speed = max(200, fall_speed_base - 200 * (level - 1))  # Min 200ms to avoid too fast
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
                        # Reset board and spawn new piece with 7 rows
                        board = [[0 for _ in range(5)] for _ in range(7)]
                        spawn_piece()
                    else:
                        # Game over, show sad face and reset after a delay
                        display.show(Image.SAD)
                        sleep(2000)  # Wait 2 seconds
                        lives = 10  # Reset lives
                        level = 1  # Reset level
                        lines_cleared_total = 0  # Reset lines cleared
                        board = [[0 for _ in range(5)] for _ in range(7)]  # Reset to 7 rows
                        spawn_piece()
        last_move = current_time
    # Control piece using buttons A and B, rotate on both pressed
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
            else:
                # Try kicking left by one
                if not check_collision(piece_x - 1, piece_y, rotated_piece):
                    piece_x -= 1
                    current_piece = rotated_piece
                    last_rotation_time = current_time
                # Try kicking right by one
                elif not check_collision(piece_x + 1, piece_y, rotated_piece):
                    piece_x += 1
                    current_piece = rotated_piece
                    last_rotation_time = current_time
                # If still collision, no rotation
    update_display()
    sleep(50)  # Small delay to prevent flickering
