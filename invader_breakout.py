import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 20
BALL_RADIUS = 10
BLOCK_WIDTH, BLOCK_HEIGHT = 60, 30
BLOCK_ROWS, BLOCK_COLS = 5, 10
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Invader Breakout")
clock = pygame.time.Clock()

# Font for text
font = pygame.font.SysFont("Arial", 24)

# Paddle class
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 40))
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += 5
        # Keep paddle within bounds
        self.rect.clamp_ip(screen.get_rect())

# Ball class
class Ball(pygame.sprite.Sprite):
    def __init__(self, paddle):
        super().__init__()
        self.image = pygame.Surface((BALL_RADIUS * 2, BALL_RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
        self.rect = self.image.get_rect(center=(paddle.rect.centerx, paddle.rect.top - BALL_RADIUS))
        self.velocity = [0, 0]  # Start stationary
        self.launched = False
    
    def update(self):
        if not self.launched:
            # Stick to paddle until launched
            self.rect.centerx = paddle.rect.centerx
            self.rect.bottom = paddle.rect.top
        else:
            # Move based on velocity
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
            # Bounce off walls
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.velocity[0] = -self.velocity[0]
            if self.rect.top <= 0:
                self.velocity[1] = -self.velocity[1]
            # Check if ball goes below paddle
            if self.rect.top > HEIGHT:
                self.reset(paddle)
                return True  # Indicate life lost
        return False

    def launch(self):
        if not self.launched:
            self.velocity = [random.choice([-4, 4]), -4]
            self.launched = True
    
    def reset(self, paddle):
        self.rect.centerx = paddle.rect.centerx
        self.rect.bottom = paddle.rect.top
        self.velocity = [0, 0]
        self.launched = False

# Block class
class Block(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BLOCK_WIDTH, BLOCK_HEIGHT))
        self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))

# Game setup
paddle = Paddle()
ball = Ball(paddle)
all_sprites = pygame.sprite.Group(paddle, ball)
blocks = pygame.sprite.Group()

# Create block formation
for row in range(BLOCK_ROWS):
    for col in range(BLOCK_COLS):
        x = col * (BLOCK_WIDTH + 10) + 50
        y = row * (BLOCK_HEIGHT + 10) + 50
        blocks.add(Block(x, y))
all_sprites.add(blocks)

# Game variables
score = 0
lives = 3
block_direction = 1  # 1 for right, -1 for left
block_speed = 1

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                ball.launch()
    
    # Update
    all_sprites.update()
    
    # Move blocks
    for block in blocks:
        block.rect.x += block_speed * block_direction
    # Check block boundaries
    if any(block.rect.left <= 0 or block.rect.right >= WIDTH for block in blocks):
        block_direction *= -1
        for block in blocks:
            block.rect.y += 10  # Move down
    
    # Ball collisions
    if ball.launched:
        if pygame.sprite.collide_rect(ball, paddle):
            ball.velocity[1] = -ball.velocity[1]
        hit_blocks = pygame.sprite.spritecollide(ball, blocks, True)
        for block in hit_blocks:
            ball.velocity[1] = -ball.velocity[1]  # Simple bounce
            score += 10
        
        # Lose life if ball falls or blocks reach bottom
        if ball.update():  # Ball fell
            lives -= 1
        if any(block.rect.bottom >= HEIGHT for block in blocks):
            lives -= 1
            ball.reset(paddle)  # Reset ball
    
    # Check game over
    if lives <= 0:
        running = False
    
    # Draw
    screen.fill(BLACK)  # Simple background
    all_sprites.draw(screen)
    
    # Draw UI
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 10, 10))
    
    pygame.display.flip()
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()
