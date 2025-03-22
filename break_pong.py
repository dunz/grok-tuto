import pygame
import sys
import random

# --- Global constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (40, 40, 40)
RED   = (220, 20, 60)
GREEN = (0, 230, 118)
BLUE  = (0, 200, 255)
YELLOW= (255, 215, 0)
PURPLE= (160, 32, 240)

# Brick layout
BRICK_ROWS = 5
BRICK_COLS = 6
BRICK_WIDTH = 80
BRICK_HEIGHT = 30
BRICK_PADDING = 10

PADDLE_WIDTH = 20
PADDLE_HEIGHT = 100
PADDLE_SPEED = 5

BALL_SIZE = 16
BALL_SPEED = 5

# Initialize pygame
pygame.init()
pygame.display.set_caption("Break-Pong!")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

font_title = pygame.font.SysFont("Arial", 60, bold=True)
font_score = pygame.font.SysFont("Arial", 30, bold=True)

# --- Classes ---
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 0
        self.color = color

    def update(self):
        self.rect.y += self.speed
        # Keep paddle in screen bounds
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

class Ball(pygame.sprite.Sprite):
    def __init__(self, color):
        super().__init__()
        self.image = pygame.Surface((BALL_SIZE, BALL_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (BALL_SIZE//2, BALL_SIZE//2), BALL_SIZE//2)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.vx = BALL_SPEED * random.choice([-1, 1])
        self.vy = BALL_SPEED * random.choice([-1, 1])
        self.last_player_hit = None  # Track who last hit the ball

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Bounce off top/bottom
        if self.rect.top <= 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.vy = -self.vy
        
        # If ball goes off left or right, reset
        if self.rect.right < 0:
            # Right player gets a point (if last_player_hit was Right)
            self.reset()
        elif self.rect.left > SCREEN_WIDTH:
            # Left player gets a point (if last_player_hit was Left)
            self.reset()

    def reset(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.vx = BALL_SPEED * random.choice([-1, 1])
        self.vy = BALL_SPEED * random.choice([-1, 1])
        self.last_player_hit = None

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((BRICK_WIDTH, BRICK_HEIGHT))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.color = color

# --- Helper functions ---
def create_bricks():
    """Create a grid of bricks in the center of the screen."""
    bricks = pygame.sprite.Group()
    start_x = (SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING)) + BRICK_PADDING) // 2
    start_y = (SCREEN_HEIGHT - (BRICK_ROWS * (BRICK_HEIGHT + BRICK_PADDING)) + BRICK_PADDING) // 2

    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = start_x + col * (BRICK_WIDTH + BRICK_PADDING)
            y = start_y + row * (BRICK_HEIGHT + BRICK_PADDING)
            color = random.choice([RED, GREEN, BLUE, YELLOW, PURPLE])
            brick = Brick(x, y, color)
            bricks.add(brick)
    return bricks

def draw_text(surface, text, font, color, center):
    """Helper to draw text centered on screen."""
    render = font.render(text, True, color)
    rect = render.get_rect(center=center)
    surface.blit(render, rect)

# --- Main game function ---
def game():
    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    paddles = pygame.sprite.Group()
    bricks = create_bricks()
    
    # Create paddles
    left_paddle = Paddle(PADDLE_WIDTH//2 + 10, SCREEN_HEIGHT//2, BLUE)
    right_paddle = Paddle(SCREEN_WIDTH - PADDLE_WIDTH//2 - 10, SCREEN_HEIGHT//2, GREEN)
    paddles.add(left_paddle, right_paddle)
    all_sprites.add(left_paddle, right_paddle)

    # Create ball
    ball = Ball(WHITE)
    all_sprites.add(ball)

    # Add bricks to the all_sprites group
    for brick in bricks:
        all_sprites.add(brick)

    # Scores
    score_left = 0
    score_right = 0

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Paddle controls
            if event.type == pygame.KEYDOWN:
                # Left paddle (W/S)
                if event.key == pygame.K_w:
                    left_paddle.speed = -PADDLE_SPEED
                elif event.key == pygame.K_s:
                    left_paddle.speed = PADDLE_SPEED
                
                # Right paddle (UP/DOWN)
                if event.key == pygame.K_UP:
                    right_paddle.speed = -PADDLE_SPEED
                elif event.key == pygame.K_DOWN:
                    right_paddle.speed = PADDLE_SPEED
            
            if event.type == pygame.KEYUP:
                # Left paddle (W/S)
                if event.key in (pygame.K_w, pygame.K_s):
                    left_paddle.speed = 0
                # Right paddle (UP/DOWN)
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    right_paddle.speed = 0

        # Update sprites
        all_sprites.update()

        # Check collisions: Ball with paddles
        if pygame.sprite.collide_rect(ball, left_paddle):
            ball.vx = abs(ball.vx)  # ensure to go right
            ball.last_player_hit = "LEFT"
        if pygame.sprite.collide_rect(ball, right_paddle):
            ball.vx = -abs(ball.vx) # ensure to go left
            ball.last_player_hit = "RIGHT"

        # Check collisions: Ball with bricks
        hit_bricks = pygame.sprite.spritecollide(ball, bricks, dokill=True)
        if hit_bricks:
            # Reverse the ball's direction if it hits a brick
            ball.vy = -ball.vy

            # Award a point to whoever last touched the ball
            if ball.last_player_hit == "LEFT":
                score_left += len(hit_bricks)
            elif ball.last_player_hit == "RIGHT":
                score_right += len(hit_bricks)

        # Redraw background
        screen.fill(GRAY)

        # Draw dividing line in the center (for a stylish look)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT), 2)

        # Draw all sprites (paddles, ball, bricks)
        all_sprites.draw(screen)

        # Draw scores
        draw_text(screen, f"Score: {score_left}", font_score, WHITE, (SCREEN_WIDTH//4, 30))
        draw_text(screen, f"Score: {score_right}", font_score, WHITE, (3*SCREEN_WIDTH//4, 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

def start_screen():
    """Simple start screen with instructions."""
    in_start_screen = True
    while in_start_screen:
        screen.fill(BLACK)
        draw_text(screen, "Break-Pong!", font_title, YELLOW, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        draw_text(screen, "Press ENTER to Start", font_score, WHITE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        draw_text(screen, "Blue Paddle (Left): W/S to move", font_score, BLUE, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        draw_text(screen, "Green Paddle (Right): UP/DOWN to move", font_score, GREEN, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    in_start_screen = False
        
        pygame.display.flip()
        clock.tick(FPS)

def main():
    start_screen()
    game()

if __name__ == "__main__":
    main()
