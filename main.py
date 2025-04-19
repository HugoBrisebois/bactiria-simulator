import pygame
import sys
import random
import numpy as np
from other_file import run_specific_code  # Import the function from the other file

# Initialize Pygame
pygame.init()

# Set up the screen dimensions
screen_width = 800
screen_height = 600

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Bacteria Simulation")

# Define colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Define bacteria, food, water, and obstacles
bacteria = [{"position": [400, 300], "branches": []}]  # Start with one bacteria
bacteria_tracks = []  # List to store the positions of the tracks
food_sources = [{"position": [random.randint(50, 750), random.randint(50, 550)]}]
water_sources = [{"position": [random.randint(50, 750), random.randint(50, 550)]}]
obstacles = []  # Obstacles will now be lines (start and end points)

# Define movement speed
speed = 2
branch_length = 10  # Length of each bacteria expansion step

# Define buttons
buttons = {
    "edit_food": pygame.Rect(650, 50, 150, 50),
    "edit_water": pygame.Rect(650, 120, 150, 50),
    "edit_bacteria": pygame.Rect(650, 190, 150, 50),
    "edit_obstacles": pygame.Rect(650, 260, 150, 50),
    "run_ml": pygame.Rect(650, 330, 150, 50),
    "reset": pygame.Rect(650, 400, 150, 50),  # Reset button
    "stop": pygame.Rect(650, 470, 150, 50),  # Stop button
}

# Current mode
current_mode = None  # Modes: "food", "water", "bacteria", "obstacles", "run_ml"

# Temporary variables for drawing lines
drawing_line = False
line_start = None

# Function to check if a position is valid (not colliding with obstacles)
def is_valid_position(position):
    for start, end in obstacles:
        obstacle_line = pygame.draw.line(screen, BLACK, start, end, 2)
        if obstacle_line.collidepoint(position):
            return False
    return 0 <= position[0] < screen_width and 0 <= position[1] < screen_height

# Function to check if there is more food or water
def check_food_water():
    if not food_sources and not water_sources:
        print("No more food or water left!")
        return False
    return True

# Function to check if a position is off the display
def is_within_screen(position):
    return 0 <= position[0] < screen_width and 0 <= position[1] < screen_height

# Function to draw the environment
def draw_environment():
    # Draw food
    for food in food_sources:
        pygame.draw.circle(screen, GREEN, food["position"], 10)  # Food

    # Draw water
    for water in water_sources:
        pygame.draw.circle(screen, BLUE, water["position"], 10)  # Water

    # Draw bacteria
    for bacterium in bacteria:
        pygame.draw.circle(screen, RED, bacterium["position"], 10)  # Bacteria
        for branch in bacterium["branches"]:
            pygame.draw.line(screen, RED, bacterium["position"], branch["position"], 2)  # Bacteria branches

    # Draw bacteria tracks
    for track in bacteria_tracks:
        pygame.draw.circle(screen, RED, track, 3)  # Small circles for tracks

    # Draw obstacles
    for start, end in obstacles:
        pygame.draw.line(screen, BLACK, start, end, 2)  # Obstacles as lines

# Function to draw buttons
def draw_buttons():
    for mode, rect in buttons.items():
        pygame.draw.rect(screen, GRAY, rect)  # Draw button background
        text = mode.replace("_", " ").title()  # Format button text
        font = pygame.font.Font(None, 24)  # Set font size
        text_surface = font.render(text, True, BLACK)  # Render text
        text_rect = text_surface.get_rect(center=rect.center)  # Center text in button
        screen.blit(text_surface, text_rect)  # Draw text on button

# Function to expand bacteria
def expand_bacteria():
    new_branches = []
    for bacterium in bacteria:
        for branch in bacterium["branches"]:
            # Expand the branch by a small step
            dx, dy = branch["direction"]
            new_pos = [branch["position"][0] + dx * branch_length, branch["position"][1] + dy * branch_length]
            
            # Check if the new position is valid and within the screen
            if is_valid_position(new_pos) and is_within_screen(new_pos):
                # Add the new position to the branch
                branch["position"] = new_pos
                # Add the new position to the tracks
                bacteria_tracks.append(new_pos[:])
                # Occasionally create a new branch
                if random.random() < 0.1:  # 10% chance to branch
                    new_direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])  # Random direction
                    new_branches.append({"position": new_pos[:], "direction": new_direction})
            else:
                # Change direction if the new position is invalid
                branch["direction"] = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])

            # Check if the bacteria found food or water
            for food in food_sources:
                if np.linalg.norm(np.array(new_pos) - np.array(food["position"])) < 10:
                    print("Food found!")
                    food_sources.remove(food)  # Remove the food source
                    break
            for water in water_sources:
                if np.linalg.norm(np.array(new_pos) - np.array(water["position"])) < 10:
                    print("Water found!")
                    water_sources.remove(water)  # Remove the water source
                    break

            # Update the screen to show progress
            screen.fill(WHITE)  # Clear the screen
            draw_environment()  # Redraw all elements (food, water, obstacles, bacteria)
            pygame.display.flip()  # Update the display
            pygame.time.delay(50)  # Add a small delay (50ms)

    # Add new branches to the bacteria
    for bacterium in bacteria:
        bacterium["branches"].extend(new_branches)

    # Check if there is more food or water
    if not check_food_water():
        print("Stopping expansion: No more food or water.")
        global searching
        searching = False  # Stop the expansion

# Function to reset the environment
def reset_environment():
    global bacteria, bacteria_tracks, food_sources, water_sources, obstacles, searching
    bacteria = [{"position": [400, 300], "branches": []}]  # Reset to one bacteria
    bacteria_tracks = []  # Clear tracks
    food_sources = []  # Clear food sources
    water_sources = []  # Clear water sources
    obstacles = []  # Clear obstacles
    searching = False  # Stop searching
    print("Environment reset.")

# Function to stop the simulation
def stop_simulation():
    global searching
    searching = False
    print("Simulation stopped.")

# Main game loop
running = True
searching = False  # Flag to indicate if the bacteria are searching
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a button is clicked
            for mode, rect in buttons.items():
                if rect.collidepoint(event.pos):
                    current_mode = mode
                    if current_mode == "run_ml":
                        searching = True  # Start searching when "Run ML" is clicked
                        # Initialize branches for each bacterium
                        for bacterium in bacteria:
                            if not bacterium["branches"]:  # Only initialize if no branches exist
                                bacterium["branches"].append({
                                    "position": bacterium["position"][:],  # Start at the bacterium's position
                                    "direction": random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])  # Random direction
                                })
                    elif current_mode == "reset":
                        reset_environment()  # Reset the environment
                    elif current_mode == "stop":
                        stop_simulation()  # Stop the simulation
                    break
            else:
                # Add new entities based on the current mode
                if current_mode == "edit_food":
                    food_sources.append({"position": list(event.pos)})
                elif current_mode == "edit_water":
                    water_sources.append({"position": list(event.pos)})
                elif current_mode == "edit_bacteria":
                    bacteria.append({"position": list(event.pos), "branches": []})
                elif current_mode == "edit_obstacles":
                    drawing_line = True
                    line_start = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            # Finish drawing a line in "edit_obstacles" mode
            if current_mode == "edit_obstacles" and drawing_line:
                line_end = event.pos
                obstacles.append((line_start, line_end))
                drawing_line = False
                line_start = None

    # Fill the screen with a neutral background color
    screen.fill(WHITE)

    # Draw the environment
    draw_environment()

    # Draw the buttons
    draw_buttons()

    # Expand bacteria if searching is active
    if searching:
        expand_bacteria()

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()

