import pygame
import sys
import os
from transformers import pipeline
import math
import random
import tempfile

# Set the working directory to the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Initialize Pygame
pygame.init()

# Set up the screen for Full HD resolution
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Load background image
background_image = pygame.image.load("grass.png").convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load and scale player and NPC sprites
player_sprite_original = pygame.image.load("player.png").convert_alpha()
npc_sprite_original = pygame.image.load("npc.png").convert_alpha()

# Scale sprites down
player_sprite = pygame.transform.scale(player_sprite_original, (100, 100))  # Adjust size as needed
npc_sprite = pygame.transform.scale(npc_sprite_original, (100, 100))  # Adjust size as needed

# Player attributes
player_rect = player_sprite.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
player_speed = 1  # Player movement speed

# NPC attributes (fixed in the center of the screen)
npc_rect = npc_sprite.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

# Font
font = pygame.font.SysFont(None, 30)

# Load the question answering pipeline
qa_pipeline = pipeline("question-answering")

# Context for the single NPC
npc_context = "context for the NPC"

# Function to display text on the screen
def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Function to calculate distance between two points
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to simulate asking the NPC a question and getting an answer
def get_answer_for_npc(question):
    answer = qa_pipeline(question=question, context=npc_context)
    return answer["answer"]

# Class for additional sprites
class SpecificSprite(pygame.sprite.Sprite):
    def __init__(self, name, image, x, y):
        super().__init__()
        self.name = name
        self.image = pygame.transform.scale(image, (300, 300))  # Scale down sprite
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

# Function to spawn specific sprites in predefined grid spots
def spawn_specific_sprites(sprite_info_list, grid_spots):
    sprites = []
    random.shuffle(grid_spots)  # Randomize the order of grid spots

    for idx, (name, image_path) in enumerate(sprite_info_list):
        if idx < len(grid_spots):
            x, y = grid_spots[idx]
            image = pygame.image.load(image_path).convert_alpha()
            sprite = SpecificSprite(name, image, x, y)
            sprites.append(sprite)

    return sprites

# Predefined grid spots around the screen dimensions
sprite_size = 300  # Size of the sprites
half_sprite_size = sprite_size // 2

grid_spots = [
    (0, 0),  # LEFT-UP
    (SCREEN_WIDTH // 2 - half_sprite_size, 0),  # CENTER-UP
    (SCREEN_WIDTH - sprite_size, 0),  # RIGHT-UP
    (0, SCREEN_HEIGHT // 2 - half_sprite_size),  # CENTER-LEFT
    (SCREEN_WIDTH - sprite_size, SCREEN_HEIGHT // 2 - half_sprite_size),  # CENTER-RIGHT
    (0, SCREEN_HEIGHT - sprite_size),  # LEFT-DOWN
    (SCREEN_WIDTH // 2 - half_sprite_size, SCREEN_HEIGHT - sprite_size),  # CENTER-DOWN
    (SCREEN_WIDTH - sprite_size, SCREEN_HEIGHT - sprite_size)  # RIGHT-DOWN
]

# List of specific sprites with names and image paths (excluding the fountain)
sprite_info_list = [
    ("Pyramid", "pyramid.png"),
    ("Palace", "palace.png"),
    ("Stadium", "stadium.png"),
    ("Japanese Palace", "japanese.png"),
    ("Tower", "tower.png"),
    ("Hospital", "hospital.png"),
    ("Train Station", "trainstation.png"),
    ("Hotel", "hotel.png"),
    # Add more sprites as needed
]

# Spawn specific sprites
specific_sprites = spawn_specific_sprites(sprite_info_list, grid_spots)

# Create a sprite group for easy drawing and updating
all_sprites = pygame.sprite.Group()
all_sprites.add(specific_sprites)

# Function to write neighboring sprite information to a temporary file
def write_neighboring_sprite_info(sprites):
    temp_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
    with temp_file as file:
        for sprite in sprites:
            neighbors = {
                "left": None,
                "right": None,
                "up": None,
                "down": None
            }
            sprite_center = sprite.rect.center

            for other in sprites:
                if other == sprite:
                    continue
                other_center = other.rect.center

                if other_center[0] < sprite_center[0] and abs(other_center[1] - sprite_center[1]) < sprite_size:
                    neighbors["left"] = other.name
                if other_center[0] > sprite_center[0] and abs(other_center[1] - sprite_center[1]) < sprite_size:
                    neighbors["right"] = other.name
                if other_center[1] < sprite_center[1] and abs(other_center[0] - sprite_center[0]) < sprite_size:
                    neighbors["up"] = other.name
                if other_center[1] > sprite_center[1] and abs(other_center[0] - sprite_center[0]) < sprite_size:
                    neighbors["down"] = other.name

            file.write(f"Sprite: {sprite.name}\n")
            file.write(f"Position: {sprite.rect.topleft}\n")
            file.write(f"Neighbors: {neighbors}\n\n")

    print(f"Neighboring sprite information written to: {temp_file.name}")

# Call the function to write neighboring sprite information
write_neighboring_sprite_info(specific_sprites)

# Main game loop
def main():
    global player_rect  # Declare global variables

    running = True
    in_dialogue = False
    question = ""
    answer = ""
    current_npc = False

    while running:
        # Draw background image
        screen.blit(background_image, (0, 0))

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if in_dialogue:
                    if event.key == pygame.K_BACKSPACE:
                        question = question[:-1]
                    elif event.key == pygame.K_RETURN:
                        if question.strip():  # Check if the question is not empty
                            answer = get_answer_for_npc(question)
                        question = ""  # Clear the question
                    else:
                        question += event.unicode

        # Player movement
        keys = pygame.key.get_pressed()
        player_dx = 0
        player_dy = 0
        if keys[pygame.K_LEFT]:
            player_dx -= player_speed
        if keys[pygame.K_RIGHT]:
            player_dx += player_speed
        if keys[pygame.K_UP]:
            player_dy -= player_speed
        if keys[pygame.K_DOWN]:
            player_dy += player_speed
        player_rect.x += player_dx
        player_rect.y += player_dy

        # Ensure player stays within screen bounds
        player_rect.x = max(0, min(player_rect.x, SCREEN_WIDTH - player_rect.width))
        player_rect.y = max(0, min(player_rect.y, SCREEN_HEIGHT - player_rect.height))

        # Draw player sprite
        screen.blit(player_sprite, player_rect.topleft)

        # Draw NPC sprite
        screen.blit(npc_sprite, npc_rect.topleft)

        # Draw all specific sprites
        all_sprites.draw(screen)

        # Check for interaction with NPC
        if player_rect.colliderect(npc_rect):
            draw_text("Press E to interact", RED, npc_rect.x - 50, npc_rect.y - 30)
            if keys[pygame.K_e]:
                in_dialogue = True
                current_npc = True
        else:
            current_npc = False

        # Display interaction window
        if in_dialogue:
            pygame.draw.rect(screen, WHITE, (10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            if current_npc:
                draw_text("NPC: Hello! What do you want to know?", RED, 20, 20)
            draw_text("Your question: " + question, RED, 20, 50)
            if answer:
                draw_text("NPC: " + answer, RED, 20, 80)

        pygame.display.flip()

if __name__ == "__main__":
    main()
