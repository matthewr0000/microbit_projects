from microbit import *
import random

# FlappyBit - A Flappy Bird style game for Micro:bit
# EASY VERSION - Slower and easier to play!

# Game variables
player_y = 2  # Bird height (0 is top, 4 is bottom)
gravity = 0.1  # Faster gravity
flap_strength = -0.5  # Stronger flap
player_velocity = 0
score = 0
last_wall_move = 0
wall_move_delay = 1000  # Move walls every 1 second

# Walls are [x, gap_y] where x is position and gap_y is the center of the gap
walls = []

# Start with a wall on the right
walls.append([4, random.randint(1, 3)])

def show_game_over():
    display.show(Image.SAD)
    sleep(10)
    display.scroll(str(score))

def reset_game():
    global player_y, player_velocity, score, walls, last_wall_move
    player_y = 2
    player_velocity = 0
    score = 0
    walls = [[4, random.randint(1, 3)]]
    last_wall_move = running_time()
    #display.scroll('Press A to flap!')

# Show instructions at start

while True:
    # Clear the display
    display.clear()
    
    # Draw the bird (always at x=1)
    bird_y = min(4, max(0, int(player_y)))
    display.set_pixel(1, bird_y, 9)  # Bright bird
    
    # Draw all walls
    for wall in walls:
        # Draw the wall with a gap
        for y in range(5):
            # Skip drawing at the gap (gap_y and one pixel above/below)
            if y < wall[1] - 1 or y > wall[1] + 1:
                display.set_pixel(wall[0], y, 5)
    
    # Handle controls - flap when A is pressed
    if button_a.was_pressed():  # Only flap once per button press
        player_velocity = flap_strength
    
    # Apply gravity and update bird position
    player_velocity += gravity
    player_y += player_velocity
    
    # Check if bird hit the top or bottom
    if player_y < 0 or player_y > 4:
        show_game_over()
        reset_game()
        continue
    
    # Move walls every wall_move_delay milliseconds
    current_time = running_time()
    if current_time - last_wall_move > wall_move_delay:
        last_wall_move = current_time
        
        # Move walls and check for collisions
        for i in range(len(walls)):
            # Move wall left
            walls[i][0] -= 1
            
            # Check if bird passed through a wall
            if walls[i][0] == 1:
                # Check if bird is within the gap
                if abs(int(player_y) - walls[i][1]) <= 1:
                    # Bird is in the gap - add a point!
                    score += 1
                    display.show(Image.HAPPY)
                    sleep(500)  # Longer pause when scoring
                else:
                    # Bird hit the wall
                    show_game_over()
                    reset_game()
                    break
        
        # Remove walls that went off screen
        walls = [wall for wall in walls if wall[0] >= 0]
        
        # Add new walls
        if len(walls) == 0 or walls[-1][0] < 3:
            walls.append([4, random.randint(1, 3)])
    
    # Longer delay to slow down the game
    sleep(200)
