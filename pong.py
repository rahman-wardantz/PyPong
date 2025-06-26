import pygame
import sys
import random
import time

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
PADDLE_SOUND = load_sound('gameboy-pluck-41265.mp3')
SCORE_SOUND = load_sound('8-bit-powerup-6768.mp3')

# Game states
START, PLAYING, GAME_OVER = 0, 1, 2
game_state = START
WINNING_SCORE = 5

clock = pygame.time.Clock()

# Add AI for right paddle
AI_ENABLED = True
AI_DIFFICULTY = 0.08  # Lower is easier, higher is harder (0.05-0.15 recommended)
# AI error chance and max speed
AI_ERROR_CHANCE = 0.25  # 0.0 = selalu tepat, 1.0 = selalu salah (disarankan 0.15-0.3)
AI_MAX_SPEED = 3  # Batasi kecepatan paddle AI

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

# Add score history with timestamp
score_history = []  # (scorer, l, r, timestamp)

# Power-up feature
POWERUP_SIZE = 24
POWERUP_DURATION = 5  # seconds
powerup = None  # {'rect': pygame.Rect, 'type': str, 'active': bool, 'spawn_time': float}
powerup_types = ['enlarge', 'shrink', 'speed']
powerup_effect = None  # {'type': str, 'end_time': float, 'target': str}

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
        # AI: move towards the ball, with error and speed limit
        ai_target = ball.centery
        if random.random() < AI_ERROR_CHANCE:
            ai_target += random.randint(-80, 80)  # AI kadang salah prediksi
        move = int(PADDLE_SPEED * AI_DIFFICULTY * abs(ai_target - right_paddle.centery))
        move = min(move, AI_MAX_SPEED)
        if right_paddle.centery < ai_target:
            right_paddle.y += move
        elif right_paddle.centery > ai_target:
            right_paddle.y -= move
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
        score_history.append(('Right', left_score, right_score, time.time()))
        if SCORE_SOUND:
            SCORE_SOUND.play()
        reset_ball()
    if ball.right >= WIDTH:
        left_score += 1
        score_history.append(('Left', left_score, right_score, time.time()))
        if SCORE_SOUND:
            SCORE_SOUND.play()
        reset_ball()

    # Prevent ball from getting too fast
    max_speed = 15
    ball_dx = max(-max_speed, min(ball_dx, max_speed))
    ball_dy = max(-max_speed, min(ball_dy, max_speed))

    # Power-up spawn logic
    if powerup is None and game_state == PLAYING and random.random() < 0.002:
        px = random.randint(WIDTH//4, WIDTH*3//4 - POWERUP_SIZE)
        py = random.randint(50, HEIGHT-50-POWERUP_SIZE)
        ptype = random.choice(powerup_types)
        powerup = {'rect': pygame.Rect(px, py, POWERUP_SIZE, POWERUP_SIZE), 'type': ptype, 'active': True, 'spawn_time': time.time()}

    # Power-up collision
    if powerup and powerup['active']:
        if ball.colliderect(powerup['rect']):
            # Apply effect to the last hitter
            if ball_dx < 0:
                target = 'left'
            else:
                target = 'right'
            effect_end = time.time() + POWERUP_DURATION
            powerup_effect = {'type': powerup['type'], 'end_time': effect_end, 'target': target}
            powerup['active'] = False

    # Power-up effect logic
    if powerup_effect:
        # Use nonlocal for ball speed change
        if powerup_effect['type'] == 'enlarge':
            if powerup_effect['target'] == 'left':
                left_paddle.height = 160
            else:
                right_paddle.height = 160
        elif powerup_effect['type'] == 'shrink':
            if powerup_effect['target'] == 'left':
                left_paddle.height = 60
            else:
                right_paddle.height = 60
        elif powerup_effect['type'] == 'speed':
            # Set ball_dx and ball_dy direction, but with new speed
            sign_x = 1 if ball_dx > 0 else -1
            sign_y = 1 if ball_dy > 0 else -1
            ball_dx = 8 * sign_x
            ball_dy = 8 * sign_y
        if time.time() > powerup_effect['end_time']:
            left_paddle.height = PADDLE_HEIGHT
            right_paddle.height = PADDLE_HEIGHT
            # Reset ball speed to default, keep direction
            sign_x = 1 if ball_dx > 0 else -1
            sign_y = 1 if ball_dy > 0 else -1
            ball_dx = 5 * sign_x
            ball_dy = 5 * sign_y
            powerup_effect = None
            powerup = None

    # Remove powerup if not taken after 7 seconds
    if powerup and powerup['active'] and time.time() - powerup['spawn_time'] > 7:
        powerup = None

    # Drawing
    screen.fill(BG_COLOR)
    # Draw center dashed line
    dash_height = 20
    dash_gap = 15
    for y in range(0, HEIGHT, dash_height + dash_gap):
        pygame.draw.rect(screen, FG_COLOR, (WIDTH//2 - 2, y, 4, dash_height), border_radius=2)
    # Draw paddles with rounded corners
    pygame.draw.rect(screen, FG_COLOR, left_paddle, border_radius=8)
    pygame.draw.rect(screen, FG_COLOR, right_paddle, border_radius=8)
    # Draw ball with shadow
    shadow_offset = 4
    pygame.draw.ellipse(screen, (0,0,0,80), ball.move(shadow_offset, shadow_offset))
    pygame.draw.ellipse(screen, FG_COLOR, ball)

    # Draw scores with subtle shadow
    left_text = font.render(str(left_score), True, (0,0,0))
    screen.blit(left_text, (WIDTH//4+2, 22))
    left_text = font.render(str(left_score), True, FG_COLOR)
    screen.blit(left_text, (WIDTH//4, 20))
    right_text = font.render(str(right_score), True, (0,0,0))
    screen.blit(right_text, (WIDTH*3//4+2, 22))
    right_text = font.render(str(right_score), True, FG_COLOR)
    screen.blit(right_text, (WIDTH*3//4, 20))

    # Draw powerup
    if powerup and powerup['active']:
        color = (0, 200, 255) if powerup['type'] == 'enlarge' else (255, 100, 0) if powerup['type'] == 'shrink' else (255, 255, 0)
        pygame.draw.rect(screen, color, powerup['rect'], border_radius=8)
        pfont = pygame.font.Font(None, 28)
        label = {'enlarge': '+', 'shrink': '-', 'speed': 'S'}[powerup['type']]
        text = pfont.render(label, True, (0,0,0))
        screen.blit(text, (powerup['rect'].x+6, powerup['rect'].y+2))

    # FPS display
    if show_fps:
        fps = int(clock.get_fps())
        fps_text = fps_font.render(f'FPS: {fps}', True, FG_COLOR)
        screen.blit(fps_text, (10, 10))

    # Score history display (last 5, only if <3s old)
    hist_font = pygame.font.Font(None, 28)
    y_offset = HEIGHT - 30
    now = time.time()
    for entry in score_history[::-1]:
        scorer, l, r, t = entry
        if now - t > 3:
            continue
        hist_text = hist_font.render(f'{scorer} scored! {l}-{r}', True, FG_COLOR)
        screen.blit(hist_text, (10, y_offset))
        y_offset -= 22
        if y_offset < 0:
            break

    # Show controls at the top right in a semi-transparent box ONLY on start/pause/game over
    show_controls = (game_state in [START, GAME_OVER]) or (PAUSED and game_state == PLAYING)
    if show_controls:
        controls_font = pygame.font.Font(None, 24)
        controls = [
            'Controls:',
            'W/S: Move Left Paddle',
            'Up/Down: Move Right Paddle',
            'P: Pause',
            'T: Theme',
            'R: Reset',
            'Esc: Quit'
        ]
        box_width = 240
        box_height = len(controls) * 22 + 16
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surf.fill((30,30,30,180))
        y_ctrl = 8
        for ctrl in controls:
            ctrl_text = controls_font.render(ctrl, True, (255,255,255))
            box_surf.blit(ctrl_text, (12, y_ctrl))
            y_ctrl += 22
        screen.blit(box_surf, (WIDTH - box_width - 10, 10))

    pygame.display.flip()
    clock.tick(60)
