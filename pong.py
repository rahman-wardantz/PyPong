import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Paddle settings
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 7

# Ball settings
BALL_SIZE = 20
BALL_SPEED_X, BALL_SPEED_Y = 5, 5

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('PyPong')

# Paddle positions
left_paddle = pygame.Rect(10, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 20, HEIGHT//2 - PADDLE_HEIGHT//2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Ball position
ball = pygame.Rect(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, BALL_SIZE, BALL_SIZE)

# Scores
left_score = 0
right_score = 0
font = pygame.font.Font(None, 74)

# Ball direction
ball_dx = BALL_SPEED_X
ball_dy = BALL_SPEED_Y

# Sound effects
pygame.mixer.init()
# Improved sound effect loading (use real .wav files if available)
def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None
PADDLE_SOUND = load_sound('paddle.wav')
SCORE_SOUND = load_sound('score.wav')

# Game states
START, PLAYING, GAME_OVER = 0, 1, 2
game_state = START
WINNING_SCORE = 5

clock = pygame.time.Clock()

# Add AI for right paddle
AI_ENABLED = True
AI_DIFFICULTY = 0.08  # Lower is easier, higher is harder (0.05-0.15 recommended)

# Helper functions
def reset_ball():
    global ball_dx, ball_dy
    ball.x, ball.y = WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2
    ball_dx = BALL_SPEED_X * random.choice([-1, 1])
    ball_dy = BALL_SPEED_Y * random.choice([-1, 1])

def draw_center_text(text, font, color, y):
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect(center=(WIDTH//2, y))
    screen.blit(text_surface, rect)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_state == START and event.type == pygame.KEYDOWN:
            game_state = PLAYING
        if game_state == GAME_OVER and event.type == pygame.KEYDOWN:
            left_score = 0
            right_score = 0
            reset_ball()
            game_state = START

    if game_state == START:
        screen.fill(BLACK)
        draw_center_text('PyPong', font, WHITE, HEIGHT//2 - 50)
        draw_center_text('Press any key to start', pygame.font.Font(None, 48), WHITE, HEIGHT//2 + 30)
        pygame.display.flip()
        clock.tick(60)
        continue
    if game_state == GAME_OVER:
        screen.fill(BLACK)
        winner = 'Left Player' if left_score >= WINNING_SCORE else 'Right Player'
        draw_center_text(f'{winner} Wins!', font, WHITE, HEIGHT//2 - 50)
        draw_center_text('Press any key to restart', pygame.font.Font(None, 48), WHITE, HEIGHT//2 + 30)
        pygame.display.flip()
        clock.tick(60)
        continue

    keys = pygame.key.get_pressed()
    # Left paddle movement
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED
    # Right paddle movement (AI or player)
    if AI_ENABLED and game_state == PLAYING:
        # Simple AI: move towards the ball
        if right_paddle.centery < ball.centery:
            right_paddle.y += int(PADDLE_SPEED * AI_DIFFICULTY * abs(ball.centery - right_paddle.centery))
        elif right_paddle.centery > ball.centery:
            right_paddle.y -= int(PADDLE_SPEED * AI_DIFFICULTY * abs(ball.centery - right_paddle.centery))
        # Clamp paddle position
        if right_paddle.top < 0:
            right_paddle.top = 0
        if right_paddle.bottom > HEIGHT:
            right_paddle.bottom = HEIGHT
    else:
        if keys[pygame.K_UP] and right_paddle.top > 0:
            right_paddle.y -= PADDLE_SPEED
        if keys[pygame.K_DOWN] and right_paddle.bottom < HEIGHT:
            right_paddle.y += PADDLE_SPEED

    # Move the ball
    ball.x += ball_dx
    ball.y += ball_dy

    # Ball collision with top/bottom
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        ball_dy *= -1

    # Ball collision with paddles
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        # Calculate bounce angle based on where the ball hits the paddle
        if ball.colliderect(left_paddle):
            offset = (ball.centery - left_paddle.centery) / (PADDLE_HEIGHT / 2)
        else:
            offset = (ball.centery - right_paddle.centery) / (PADDLE_HEIGHT / 2)
        ball_dx *= -1.1  # Speed up ball
        ball_dy = (BALL_SPEED_Y * offset) or ball_dy * 1.05
        if PADDLE_SOUND:
            PADDLE_SOUND.play()

    # Ball out of bounds
    if ball.left <= 0:
        right_score += 1
        if SCORE_SOUND:
            SCORE_SOUND.play()
        reset_ball()
    if ball.right >= WIDTH:
        left_score += 1
        if SCORE_SOUND:
            SCORE_SOUND.play()
        reset_ball()

    # Prevent ball from getting too fast
    max_speed = 15
    ball_dx = max(-max_speed, min(ball_dx, max_speed))
    ball_dy = max(-max_speed, min(ball_dy, max_speed))

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    left_text = font.render(str(left_score), True, WHITE)
    right_text = font.render(str(right_score), True, WHITE)
    screen.blit(left_text, (WIDTH//4, 20))
    screen.blit(right_text, (WIDTH*3//4, 20))

    pygame.display.flip()
    clock.tick(60)
