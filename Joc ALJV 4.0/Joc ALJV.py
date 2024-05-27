import os
import pygame
import sys
import math
import random
from transformers import pipeline

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

# Function to write neighboring sprite information
def get_neighboring_sprite_info(sprites):
    info = []
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

        info.append((sprite.name, neighbors))
    return info

# Generate the town lore directly
def generate_town_lore(sprites):
    buildings_info = get_neighboring_sprite_info(sprites)
    
    lore = "This town is so strange because it only has 8 buildings arranged in a square.\n\n"
    for name, neighbors in buildings_info:
        lore += f"The {name} is located "
        
        locations = []
        if neighbors['left']:
            locations.append(f"to the right of the {neighbors['left']}")
        if neighbors['right']:
            locations.append(f"to the left of the {neighbors['right']}")
        if neighbors['up']:
            locations.append(f"below the {neighbors['up']}")
        if neighbors['down']:
            locations.append(f"above the {neighbors['down']}")
        
        if locations:
            lore += " and ".join(locations) + ".\n"
        else:
            lore += "in an isolated spot.\n"

    return lore

def write_lore_to_file(lore, output_path):
    with open(output_path, 'w') as file:
        file.write(lore)

# Generate town lore and write to file
town_lore = generate_town_lore(specific_sprites)
output_path = "town_lore.txt"
write_lore_to_file(town_lore, output_path)

# Set the NPC context to the generated town lore
npc_context = town_lore

print("Lore has been written to town_lore.txt")

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
            # Draw semi-transparent black background
            pygame.draw.rect(screen, (0, 0, 0, 128), (10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            draw_text("You: " + question, WHITE, 20, SCREEN_HEIGHT - 1030)
            draw_text("NPC: This town is so strange it only has 8 building in a square!", WHITE, 20, 20)
            if answer:
                draw_text("NPC: " + answer, WHITE, 20, 80)

        # Close dialogue on pressing Esc
        if keys[pygame.K_ESCAPE]:
            in_dialogue = False
            question = ""
            answer = ""

        pygame.display.flip()

if __name__ == "__main__":
    main()