import pygame
import sys
import json

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Draw Rectangles and Circles")

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)

# Variables
drawing = False
start_pos = None
shape = "rectangle"  # default shape
shapes = []  # store drawn shapes
counter = 1

# Input field variables
input_active = False
input_text = ""
save_message = ""
save_message_timer = 0

font = pygame.font.Font(None, 24)
small_font = pygame.font.Font(None, 18)

# UI elements
save_button_rect = pygame.Rect(WIDTH - 100, 10, 80, 30)
input_rect = pygame.Rect(WIDTH - 300, 50, 200, 30)
confirm_button_rect = pygame.Rect(WIDTH - 90, 50, 80, 30)


def save_shapes_to_file(filename="shapes.json"):
    try:
        serializable_shapes = []

        for s in shapes:
            if s['type'] == 'rectangle':
                serializable_shapes.append({
                    'type': 'rectangle',
                    'x': s['rect'].x,
                    'y': s['rect'].y,
                    'width': s['rect'].width,
                    'height': s['rect'].height,
                    'label': s['label'],
                    'bounds': (s['rect'].x, s['rect'].x + s['rect'].width, s['rect'].y, s['rect'].y + s['rect'].height,
                               0, 1)
                })
            elif s['type'] == 'circle':
                serializable_shapes.append({
                    'type': 'circle',
                    'center_x': s['center'][0],
                    'center_y': s['center'][1],
                    'radius': s['radius'],
                    'label': s['label']
                })

        with open(filename, "w") as f:
            json.dump(serializable_shapes, f, indent=4)

        return True, f"Saved {len(serializable_shapes)} shapes to {filename}"
    except Exception as e:
        return False, f"Error saving file: {str(e)}"


def draw_ui():
    global save_message_timer

    # Tool info
    tool_text = font.render(f"Current tool: {shape.upper()} (press R or C to switch)", True, BLACK)
    screen.blit(tool_text, (10, 10))

    # Instructions
    instructions = font.render("Click Save button or press S to save", True, BLACK)
    screen.blit(instructions, (10, 35))

    # Save button
    pygame.draw.rect(screen, GREEN, save_button_rect)
    pygame.draw.rect(screen, BLACK, save_button_rect, 2)
    save_text = font.render("Save", True, BLACK)
    text_rect = save_text.get_rect(center=save_button_rect.center)
    screen.blit(save_text, text_rect)

    # If input is active, show input field and confirm button
    if input_active:
        # Input field background
        pygame.draw.rect(screen, WHITE, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)

        # Input text
        display_text = input_text
        if len(display_text) > 25:  # Limit display length
            display_text = display_text[-25:]

        text_surface = font.render(display_text, True, BLACK)
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        # Cursor
        cursor_x = input_rect.x + 5 + text_surface.get_width()
        if pygame.time.get_ticks() % 1000 < 500:  # Blinking cursor
            pygame.draw.line(screen, BLACK, (cursor_x, input_rect.y + 5), (cursor_x, input_rect.y + 25), 1)

        # Confirm button
        pygame.draw.rect(screen, BLUE, confirm_button_rect)
        pygame.draw.rect(screen, BLACK, confirm_button_rect, 2)
        confirm_text = font.render("Confirm", True, WHITE)
        confirm_text_rect = confirm_text.get_rect(center=confirm_button_rect.center)
        screen.blit(confirm_text, confirm_text_rect)

        # Input label
        label_text = small_font.render("Enter filename:", True, BLACK)
        screen.blit(label_text, (input_rect.x, input_rect.y - 20))

        # Instructions for input
        input_instructions = small_font.render("Type filename and click Confirm or press Enter", True, DARK_GRAY)
        screen.blit(input_instructions, (input_rect.x, input_rect.y + 35))

        # Cancel instruction
        cancel_text = small_font.render("Press Escape to cancel", True, DARK_GRAY)
        screen.blit(cancel_text, (input_rect.x, input_rect.y + 50))

    # Show save message if there is one
    if save_message and save_message_timer > 0:
        message_color = GREEN if "Error" not in save_message else RED
        message_surface = font.render(save_message, True, message_color)
        screen.blit(message_surface, (10, HEIGHT - 30))
        save_message_timer -= 1


def handle_text_input(event):
    global input_text

    if event.key == pygame.K_BACKSPACE:
        input_text = input_text[:-1]
    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
        save_file()
    elif event.key == pygame.K_ESCAPE:
        cancel_input()
    else:
        # Add character to input_text
        if len(input_text) < 50:  # Limit input length
            input_text += event.unicode


def save_file():
    global input_active, input_text, save_message, save_message_timer

    if input_text.strip():
        filename = input_text.strip()
        if not filename.endswith('.json'):
            filename += '.json'

        success, message = save_shapes_to_file(filename)
        save_message = message
        save_message_timer = 180  # Show message for 3 seconds at 60 FPS

        input_active = False
        input_text = ""
    else:
        save_message = "Please enter a filename"
        save_message_timer = 120


def cancel_input():
    global input_active, input_text
    input_active = False
    input_text = ""


def start_save_input():
    global input_active, input_text
    input_active = True
    input_text = ""


# Main game loop
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    draw_ui()

    # Draw all previously drawn shapes
    for s in shapes:
        label_text = font.render(str(s['label']), True, BLACK)
        if s['type'] == 'rectangle':
            # Center the label inside the rectangle
            label_pos = (
                s['rect'].x + s['rect'].width // 2 - label_text.get_width() // 2,
                s['rect'].y + s['rect'].height // 2 - label_text.get_height() // 2
            )
            pygame.draw.rect(screen, RED, s['rect'], 2)
            screen.blit(label_text, label_pos)

        elif s['type'] == 'circle':
            # Center the label at the center of the circle
            label_pos = (
                s['center'][0] - label_text.get_width() // 2,
                s['center'][1] - label_text.get_height() // 2
            )
            pygame.draw.circle(screen, BLUE, s['center'], s['radius'], 2)
            screen.blit(label_text, label_pos)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keyboard input
        elif event.type == pygame.KEYDOWN:
            if input_active:
                handle_text_input(event)
            else:
                if event.key == pygame.K_r:
                    shape = "rectangle"
                elif event.key == pygame.K_c:
                    shape = "circle"
                elif event.key == pygame.K_s:  # Save with S key
                    start_save_input()

        # Mouse input
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if input_active:
                # Check if confirm button was clicked
                if confirm_button_rect.collidepoint(mouse_pos):
                    save_file()
                # Check if clicked outside input area to cancel
                elif not input_rect.collidepoint(mouse_pos) and not confirm_button_rect.collidepoint(mouse_pos):
                    cancel_input()
            else:
                # Check if save button was clicked
                if save_button_rect.collidepoint(mouse_pos):
                    start_save_input()
                else:
                    # Start drawing
                    drawing = True
                    start_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP:
            if drawing and not input_active:  # Only process if we were drawing and not inputting
                drawing = False
                end_pos = event.pos

                if shape == "rectangle":
                    x, y = start_pos
                    w = end_pos[0] - x
                    h = end_pos[1] - y
                    rect = pygame.Rect(x, y, w, h)
                    rect.normalize()  # Ensure width and height are positive
                    shapes.append({'type': 'rectangle', 'rect': rect, 'label': counter})
                    counter += 1
                elif shape == "circle":
                    center = start_pos
                    radius = int(((end_pos[0] - center[0]) ** 2 + (end_pos[1] - center[1]) ** 2) ** 0.5)
                    if radius > 0:  # Only add circle if radius > 0
                        shapes.append({'type': 'circle', 'center': center, 'radius': radius, 'label': counter})
                        counter += 1

    # Draw the preview shape (only if not inputting)
    if drawing and start_pos and not input_active:
        mouse_pos = pygame.mouse.get_pos()
        if shape == "rectangle":
            x, y = start_pos
            w = mouse_pos[0] - x
            h = mouse_pos[1] - y
            preview_rect = pygame.Rect(x, y, w, h)
            preview_rect.normalize()
            pygame.draw.rect(screen, RED, preview_rect, 1)

        elif shape == "circle":
            radius = int(((mouse_pos[0] - start_pos[0]) ** 2 + (mouse_pos[1] - start_pos[1]) ** 2) ** 0.5)
            if radius > 0:
                pygame.draw.circle(screen, BLUE, start_pos, radius, 1)

    pygame.display.flip()
    clock.tick(60)  # Limit to 60 FPS

# Clean exit
pygame.quit()
sys.exit()