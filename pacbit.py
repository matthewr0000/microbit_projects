from microbit import *
import random

# PacBit - A Pac-Man style game for Micro:bit
# Use accelerometer to move Pac-Man and eat dots

# Game variables
pac_x = 2  # Pac-Man starts in the middle
pac_y = 2
score = 0

# Ghosts are [x, y]
ghosts = [[0, 0], [4, 4]]  # Two ghosts start at corners

# Dots to eat are [x, y]
dots = [
    [1, 1], [1, 2], [1, 3],
    [2, 1],         [2, 3],
    [3, 1], [3, 2], [3, 3]
]

def show_game_over():
    display.show(Image.SAD)
    sleep(500)
    display.scroll(str(score))

def reset_game():
    global pac_x, pac_y, score, ghosts, dots
    pac_x = 2
    pac_y = 2
    score = 0
    ghosts = [[0, 0], [4, 4]]
    dots = [
        [1, 1], [1, 2], [1, 3],
        [2, 1],         [2, 3],
        [3, 1], [3, 2], [3, 3]
    ]

while True:
    display.clear()
    
    # Draw Pac-Man
    display.set_pixel(pac_x, pac_y, 9)  # Bright Pac-Man
    
    # Draw ghosts (blink to make them spooky)
    if running_time() % 500 < 250:  # Blink every half second
        for ghost in ghosts:
            display.set_pixel(ghost[0], ghost[1], 5)
    
    # Draw dots
    for dot in dots:
        display.set_pixel(dot[0], dot[1], 3)  # Dim dots
    
    # Use accelerometer to move Pac-Man
    x_tilt = accelerometer.get_x()
    y_tilt = accelerometer.get_y()
    
    # Move Pac-Man based on tilt (higher threshold for movement)
    if x_tilt > 300 and pac_x < 4:
        pac_x += 1
    elif x_tilt < -300 and pac_x > 0:
        pac_x -= 1
    if y_tilt > 300 and pac_y < 4:
        pac_y += 1
    elif y_tilt < -300 and pac_y > 0:
        pac_y -= 1
    
    # Move ghosts randomly every second
    if running_time() % 1000 < 100:
        for ghost in ghosts:
            move = random.randint(0, 3)  # 0=up, 1=down, 2=left, 3=right
            if move == 0 and ghost[1] > 0:
                ghost[1] -= 1
            elif move == 1 and ghost[1] < 4:
                ghost[1] += 1
            elif move == 2 and ghost[0] > 0:
                ghost[0] -= 1
            elif move == 3 and ghost[0] < 4:
                ghost[0] += 1
    
    # Check for eating dots
    for dot in dots[:]:
        if dot[0] == pac_x and dot[1] == pac_y:
            dots.remove(dot)
            score += 1
            display.show(Image.HAPPY)
            sleep(200)
    
    # Check for ghost collision
    for ghost in ghosts:
        if ghost[0] == pac_x and ghost[1] == pac_y:
            show_game_over()
            reset_game()
            break
    
    # Check if all dots are eaten (win condition)
    if not dots:
        display.show(Image.HAPPY)
        sleep(500)
        display.scroll(str(score))
        reset_game()
    
    sleep(100)  # Refresh rate
