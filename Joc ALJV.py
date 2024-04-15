import pygame
import sys
from transformers import pipeline
import math

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Top-Down Game")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player attributes
player_radius = 25
player_x = SCREEN_WIDTH // 2
player_y = SCREEN_HEIGHT // 2
player_speed = 0.1  # Player movement speed

# NPC attributes
npc_radius = 25
npc1_x = 100
npc1_y = 100
npc2_x = 300
npc2_y = 400
npc3_x = 600
npc3_y = 200

# Font
font = pygame.font.SysFont(None, 30)

# Load the question answering pipeline
qa_pipeline = pipeline("question-answering")

# Dictionary to hold contexts for different NPCs
npc_contexts = {
    "NPC1": "Context for NPC1. This NPC knows that the bathroom is downstairs. It also knows that the library is located south of the hospital.",
    "NPC2": "Context for NPC2. This NPC Knows that the food is found in the kitchen.",
    "NPC3": "Context for NPC3. This NPC knows that the book is on the top shelf.",
    # Add more NPCs and their contexts as needed
}

# Function to display text on the screen
def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Main game loop
def main():
    global player_x, player_y  # Declare global variables

    running = True
    in_dialogue = False
    question = ""
    answer = ""
    current_npc = None

    while running:
        screen.fill(WHITE)

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
                            if current_npc:
                                answer, _ = get_answer_for_npc(current_npc, question)
                            else:
                                answer = "Please interact with an NPC first."
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
        player_x += player_dx
        player_y += player_dy

        # Draw player (hexagon)
        player_points = calculate_hexagon_points(player_x, player_y, player_radius)
        pygame.draw.polygon(screen, RED, player_points)

        # Draw NPCs (circle and triangle)
        pygame.draw.circle(screen, GREEN, (npc1_x, npc1_y), npc_radius)
        pygame.draw.polygon(screen, BLUE, [(npc2_x, npc2_y - npc_radius), 
                                            (npc2_x + npc_radius * math.sqrt(3), npc2_y + npc_radius), 
                                            (npc2_x - npc_radius * math.sqrt(3), npc2_y + npc_radius)])
        pygame.draw.circle(screen, RED, (npc3_x, npc3_y), npc_radius)

        # Check for interaction with NPCs
        if distance(player_x, player_y, npc1_x, npc1_y) <= player_radius + npc_radius:
            draw_text("Press E to interact", RED, npc1_x - 50, npc1_y - 30)
            if keys[pygame.K_e]:
                in_dialogue = True
                current_npc = "NPC1"
        elif distance(player_x, player_y, npc2_x, npc2_y) <= player_radius + npc_radius:
            draw_text("Press E to interact", RED, npc2_x - 50, npc2_y - 30)
            if keys[pygame.K_e]:
                in_dialogue = True
                current_npc = "NPC2"
        elif distance(player_x, player_y, npc3_x, npc3_y) <= player_radius + npc_radius:
            draw_text("Press E to interact", RED, npc3_x - 50, npc3_y - 30)
            if keys[pygame.K_e]:
                in_dialogue = True
                current_npc = "NPC3"
        else:
            current_npc = None

        # Display interaction window
        if in_dialogue:
            pygame.draw.rect(screen, WHITE, (10, 10, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            if current_npc:
                draw_text(f"{current_npc}: Hello! What do you want to know?", RED, 20, 20)
            draw_text("Your question: " + question, RED, 20, 50)
            if answer:
                draw_text(f"{current_npc}: " + answer, RED, 20, 80)

        pygame.display.flip()

# Function to calculate the points of a regular hexagon
def calculate_hexagon_points(x, y, radius):
    points = []
    for i in range(6):
        angle_deg = 60 * i
        angle_rad = math.radians(angle_deg)
        point_x = x + radius * math.cos(angle_rad)
        point_y = y + radius * math.sin(angle_rad)
        points.append((point_x, point_y))
    return points

# Function to calculate distance between two points
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Function to simulate asking the NPC a question and getting an answer
def get_answer_for_npc(npc_name, question):
    context = npc_contexts.get(npc_name, "")
    if not context:
        return "NPC not found.", None
    
    answer = qa_pipeline(question=question, context=context)
    return answer["answer"], context

if __name__ == "__main__":
    main()
