from microbit import *
import random

# Upward Scrolling Racing Game for Micro:bit

# Game variables
player_x = 2  # Player starts in the middle column
score = 0
game_speed = 500  # ms between obstacle moves
last_move = running_time()

# Create obstacles - each is [x, y]
obstacles = []

# Start with one obstacle
obstacles.append([random.randint(0, 4), 0])

def show_game_over():
    display.show(Image.SAD)
    sleep(500)
    display.scroll('Score: ' + str(score))

def reset_game():
    global player_x, score, game_speed, obstacles
    player_x = 2
    score = 0
    game_speed = 500
    obstacles = [[random.randint(0, 4), 0]]  # Reset with one obstacle

while True:
    # Clear the display
    display.clear()
    
    # Draw the player (always at y=4, bottom row)
    display.set_pixel(player_x, 4, 9)  # Bright player
    
    # Draw all obstacles
    for obs in obstacles:
        display.set_pixel(obs[0], obs[1], 5)  # Medium brightness obstacles
    
    # Handle controls
    if button_a.is_pressed() and player_x > 0:
        player_x -= 1  # Move left
        sleep(150)  # Prevent too fast movement
    if button_b.is_pressed() and player_x < 4:
        player_x += 1  # Move right
        sleep(150)  # Prevent too fast movement
    
    # Move obstacles every game_speed ms
    if running_time() - last_move > game_speed:
        # Move all obstacles up
        for i in range(len(obstacles)):
            obstacles[i][1] += 1
        
        # Check if we need to add a new obstacle
        if random.randint(0, 2) == 0:  # 1/3 chance of new obstacle
            obstacles.append([random.randint(0, 4), 0])
        
        # Remove obstacles that went off screen
        obstacles = [obs for obs in obstacles if obs[1] <= 4]
        
        # Increase score
        score += 1
        
        # Speed up the game slightly
        if score % 5 == 0 and game_speed > 200:
            game_speed -= 20
        
        last_move = running_time()
    
    # Check for collisions
    for obs in obstacles:
        if obs[0] == player_x and obs[1] == 4:
            show_game_over()
            reset_game()
            break
    
    sleep(50)  # Small delay for display refresh
