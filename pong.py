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

# Add pause functionality
PAUSED = False

# Add FPS display
show_fps = True
fps_font = pygame.font.Font(None, 32)

# Add color themes
THEMES = [
    {'bg': (0,0,0), 'fg': (255,255,255)},
    {'bg': (30,30,60), 'fg': (255, 200, 0)},
    {'bg': (20, 20, 20), 'fg': (0, 255, 128)},
    {'bg': (255,255,255), 'fg': (0,0,0)},
]
theme_index = 0

# Add score history
score_history = []

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

# Add reset score/history with R key
def reset_game():
    global left_score, right_score, score_history
    left_score = 0
    right_score = 0
    score_history.clear()
    reset_ball()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if game_state == START and event.type == pygame.KEYDOWN:
            game_state = PLAYING
        if game_state == GAME_OVER and event.type == pygame.KEYDOWN:
            reset_game()
            game_state = START
        if game_state == PLAYING and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                PAUSED = not PAUSED
            if event.key == pygame.K_t:
                theme_index = (theme_index + 1) % len(THEMES)
            if event.key == pygame.K_r:
                reset_game()

    BG_COLOR = THEMES[theme_index]['bg']
    FG_COLOR = THEMES[theme_index]['fg']

    if PAUSED and game_state == PLAYING:
        screen.fill(BG_COLOR)
        draw_center_text('PAUSED', font, FG_COLOR, HEIGHT//2)
        draw_center_text('Press P to resume', pygame.font.Font(None, 48), FG_COLOR, HEIGHT//2 + 50)
        pygame.display.flip()
        clock.tick(60)
        continue

    if game_state == START:
        screen.fill(BG_COLOR)
        draw_center_text('PyPong', font, FG_COLOR, HEIGHT//2 - 50)
        draw_center_text('Press any key to start', pygame.font.Font(None, 48), FG_COLOR, HEIGHT//2 + 30)
        draw_center_text('Press T to change theme', pygame.font.Font(None, 32), FG_COLOR, HEIGHT//2 + 80)
        draw_center_text('Press R to reset score/history', pygame.font.Font(None, 28), FG_COLOR, HEIGHT//2 + 120)
        pygame.display.flip()
        clock.tick(60)
        continue
    if game_state == GAME_OVER:
        screen.fill(BG_COLOR)
        winner = 'Left Player' if left_score >= WINNING_SCORE else 'Right Player'
        draw_center_text(f'{winner} Wins!', font, FG_COLOR, HEIGHT//2 - 50)
        draw_center_text('Press any key to restart', pygame.font.Font(None, 48), FG_COLOR, HEIGHT//2 + 30)
        draw_center_text('Press T to change theme', pygame.font.Font(None, 32), FG_COLOR, HEIGHT//2 + 80)
        draw_center_text('Press R to reset score/history', pygame.font.Font(None, 28), FG_COLOR, HEIGHT//2 + 120)
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
        score_history.append(('Right', left_score, right_score))
        if SCORE_SOUND:
            SCORE_SOUND.play()
        reset_ball()
    if ball.right >= WIDTH:
        left_score += 1
        score_history.append(('Left', left_score, right_score))
        if SCORE_SOUND:
            SCORE_SOUND.play()
        reset_ball()

    # Prevent ball from getting too fast
    max_speed = 15
    ball_dx = max(-max_speed, min(ball_dx, max_speed))
    ball_dy = max(-max_speed, min(ball_dy, max_speed))

    # Drawing
    screen.fill(BG_COLOR)
    pygame.draw.rect(screen, FG_COLOR, left_paddle)
    pygame.draw.rect(screen, FG_COLOR, right_paddle)
    pygame.draw.ellipse(screen, FG_COLOR, ball)
    pygame.draw.aaline(screen, FG_COLOR, (WIDTH//2, 0), (WIDTH//2, HEIGHT))

    left_text = font.render(str(left_score), True, FG_COLOR)
    right_text = font.render(str(right_score), True, FG_COLOR)
    screen.blit(left_text, (WIDTH//4, 20))
    screen.blit(right_text, (WIDTH*3//4, 20))

    # FPS display
    if show_fps:
        fps = int(clock.get_fps())
        fps_text = fps_font.render(f'FPS: {fps}', True, FG_COLOR)
        screen.blit(fps_text, (10, 10))

    # Score history display (last 5)
    hist_font = pygame.font.Font(None, 28)
    y_offset = HEIGHT - 30
    for entry in score_history[-5:][::-1]:
        scorer, l, r = entry
        hist_text = hist_font.render(f'{scorer} scored! {l}-{r}', True, FG_COLOR)
        screen.blit(hist_text, (10, y_offset))
        y_offset -= 22

    pygame.display.flip()
    clock.tick(60)
