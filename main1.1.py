import pygame
import sys
import random
import ctypes
import platform
from pypresence import Presence
import time
import math
DISCORD_CLIENT_ID = "1389154340933210142"
rpc = Presence(DISCORD_CLIENT_ID)
rpc.connect()
rpc.update(state="In Main Menu", details="Waiting to start...", large_image="default", start=time.time())
pygame.init()
is_drews_edition = platform.node() == "Drews-Computer"
is_drews_edition = platform.node() == "Drews-computer"
is_drews_edition = platform.node() == "drews-computer"
PLAYER_COLOR = (255, 50, 50)  # default
PLATFORM_COLOR = (100, 200, 100)

if is_drews_edition:
    PLAYER_COLOR = (74, 158, 110)     # #4a9e6e
    PLATFORM_COLOR = (200, 100, 100)  # #c86464

WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
JUMP_VELOCITY = -10
PLAYER_SPEED = 5
MAX_FALL_SPEED = 15
SCROLL_THRESHOLD = 250

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CubeJump")
clock = pygame.time.Clock()

font = pygame.font.Font("assets/fonts/mainfont.ttf", 24)
big_font = pygame.font.Font("assets/fonts/mainfont.ttf", 36)
icon_img = pygame.image.load("assets/images/icon.png")
pygame.display.set_icon(icon_img)
banner_img = pygame.image.load("assets/images/banner.png").convert_alpha()
banner_img = pygame.transform.scale(banner_img, (300, 100))

user32 = ctypes.windll.user32
hwnd = pygame.display.get_wm_info()['window']
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
rect = RECT()
user32.GetWindowRect(hwnd, ctypes.byref(rect))
prev_window_pos = (rect.left, rect.top)
def get_window_delta():
    global prev_window_pos
    rect = RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    new_pos = (rect.left, rect.top)
    dx = new_pos[0] - prev_window_pos[0]
    dy = new_pos[1] - prev_window_pos[1]
    prev_window_pos = new_pos
    return dx, dy

STATE_BOOT = "boot"
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_GAMEOVER = "gameover"
STATE_CREDITS = "credits"
game_state = STATE_BOOT

boot_duration = 2.5  # seconds to fill the loading bar
banner_y = HEIGHT // 2 - banner_img.get_height() // 2
banner_target_y = 60
buttons_alpha = 0

# Loading bar dimensions
loading_bar_width = 200
loading_bar_height = 12
loading_bar_progress = 0  # 0.0 to 1.0

def set_window_size(width, height):
    global screen, WIDTH, HEIGHT
    WIDTH, HEIGHT = width, height
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    
def reset_game():
    global player, velocity, can_jump, score, platforms, player_trail
    player = pygame.Rect(WIDTH//2 - 15, 500, 30, 30)
    velocity = [0, 0]
    can_jump = False
    score = 0
    platforms = [pygame.Rect(150, 550, 100, 10)]
    generate_platforms()
    player_trail = []

def generate_platforms():
    while len(platforms) < 8:
        last_y = platforms[-1].y
        y = last_y - 80
        x = random.randint(20, WIDTH - 120)
        platforms.append(pygame.Rect(x, y, 100, 10))

reset_game()
last_rpc_update = 0
boot_timer = 0
boot_duration = 2.5  # seconds to fill the loading bar
banner_y = HEIGHT // 2 - banner_img.get_height() // 2
banner_target_y = 80
buttons_alpha = 0

loading_bar_width = 200
loading_bar_height = 12
loading_bar_progress = 0.0

def draw_button(text, rect, mouse_pos, clicked, t=0, base_color=(50, 50, 100), hover_color=(70, 130, 180)):
    is_hover = rect.collidepoint(mouse_pos)
    color = hover_color if is_hover else base_color
    pulse = 1.05 + 0.05 * math.sin(t * 5) if is_hover else 1
    anim_rect = rect.inflate(rect.width * (pulse - 1), rect.height * (pulse - 1))
    anim_rect.center = rect.center

    pygame.draw.rect(screen, color, anim_rect, border_radius=10)
    label = font.render(text, True, (255, 255, 255))
    label_rect = label.get_rect(center=anim_rect.center)
    screen.blit(label, label_rect)

    return is_hover and clicked

running = True
while running:
    dt = clock.tick(FPS)
    screen.fill((25, 25, 30))
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = False
    t = pygame.time.get_ticks() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_click = True

    keys = pygame.key.get_pressed()
    
    if game_state == STATE_BOOT:
        dt_sec = dt / 1000
        boot_timer += dt_sec
        screen.fill((25, 25, 30))

        # Draw banner
        screen.blit(banner_img, (WIDTH // 2 - banner_img.get_width() // 2, int(banner_y)))

        # Draw "By Lycan"
        by_text = font.render("By Lycan", True, (180, 180, 180))
        by_rect = by_text.get_rect(center=(WIDTH // 2, int(banner_y) + banner_img.get_height() + 18))
        screen.blit(by_text, by_rect)

        # Draw loading bar (before banner moves)
        if boot_timer < boot_duration:
            loading_bar_progress = min(1.0, boot_timer / boot_duration)
            bar_x = WIDTH // 2 - loading_bar_width // 2
            bar_y = HEIGHT // 2 + 89

            # Border
            pygame.draw.rect(screen, (255, 255, 255), (bar_x - 2, bar_y - 2, loading_bar_width + 4, loading_bar_height + 4), 1)

            # Fill
            fill_width = int(loading_bar_width * loading_bar_progress)
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, fill_width, loading_bar_height))
        else:
            # Move banner upward
            if banner_y > banner_target_y:
                banner_y -= 200 * dt_sec
                banner_y = max(banner_y, banner_target_y)
            else:
                buttons_alpha = min(255, buttons_alpha + 300 * dt_sec)

            # Fade in real menu UI
            if buttons_alpha > 0:
                # Author label
                author_label = font.render("By Lycan", True, (180, 180, 180))
                author_label.set_alpha(int(buttons_alpha))
                author_rect = author_label.get_rect(center=(WIDTH // 2, 200))
                screen.blit(author_label, author_rect)

                # Buttons
                start_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2, 160, 50)
                quit_btn = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 70, 160, 50)
                for rect, label in [(start_btn, "Play"), (quit_btn, "Quit")]:
                    is_hover = rect.collidepoint(mouse_pos)
                    color = (100, 200, 100) if label == "Play" else (120, 40, 40)
                    hover_color = (200, 200, 100) if label == "Play" else (255, 60, 60)
                    used_color = hover_color if is_hover else color

                    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                    used_color_with_alpha = (*used_color[:3], int(buttons_alpha))
                    pygame.draw.rect(surf, used_color_with_alpha, surf.get_rect(), border_radius=10)
                    label_surf = font.render(label, True, (255, 255, 255))
                    label_surf.set_alpha(int(buttons_alpha))
                    label_rect = label_surf.get_rect(center=(rect.width // 2, rect.height // 2))
                    surf.blit(label_surf, label_rect)
                    screen.blit(surf, rect.topleft)

            # Fully done: move to MENU
            if banner_y == banner_target_y:
                game_state = STATE_MENU

        pygame.display.flip()
        continue
    
    if game_state == STATE_MENU:
        screen.blit(banner_img, (WIDTH//2 - banner_img.get_width()//2, 80))
        author_label = font.render("By Lycan", True, (180, 180, 180))
        author_rect = author_label.get_rect(center=(WIDTH // 2, 200))
        screen.blit(author_label, author_rect)
        if is_drews_edition:
            drew_label = font.render("Drew's Edition", True, (74, 158, 110))
            drew_rect = drew_label.get_rect(midleft=(author_rect.right + 10, author_rect.centery))
            screen.blit(drew_label, drew_rect)
        start_btn = pygame.Rect(WIDTH//2 - 80, HEIGHT//2, 160, 50)
        quit_btn = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 70, 160, 50)

        if draw_button("Play", start_btn, mouse_pos, mouse_click, t, base_color=(100, 200, 100, 255), hover_color=(200, 200, 100, 255)):
            game_state = STATE_PLAYING
            rpc.update(state="Jumping...", details="Started playing!", large_image="default", start=time.time())
            reset_game()

        credits_btn = pygame.Rect(WIDTH - 110, HEIGHT - 50, 100, 40)
        if draw_button("(C)", credits_btn, mouse_pos, mouse_click, t, base_color=(100, 100, 200), hover_color=(120, 120, 255)):
            set_window_size(850, 750)
            game_state = STATE_CREDITS

        pygame.display.flip()
        continue

    if game_state == STATE_PLAYING:
        if keys[pygame.K_LEFT]:
            player.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            player.x += PLAYER_SPEED

        if player.right < 0:
            player.left = WIDTH
        elif player.left > WIDTH:
            player.right = 0

        if keys[pygame.K_SPACE] and can_jump:
            velocity[1] = JUMP_VELOCITY
            can_jump = False

        dx, dy = get_window_delta()
        velocity[0] -= dx * 0.1
        velocity[1] -= dy * 0.1
        velocity[1] += GRAVITY
        velocity[1] = min(velocity[1], MAX_FALL_SPEED)

        player.y += int(velocity[1])

        can_jump = False
        if velocity[1] > 0:
            for plat in platforms:
                if player.colliderect(plat) and player.bottom - velocity[1] <= plat.top:
                    player.bottom = plat.top
                    velocity[1] = 0
                    can_jump = True

        if player.y < SCROLL_THRESHOLD:
            offset = SCROLL_THRESHOLD - player.y
            player.y = SCROLL_THRESHOLD
            for plat in platforms:
                plat.y += offset
            score += offset

        platforms = [p for p in platforms if p.y < HEIGHT + 40]
        generate_platforms()

        if player.y > HEIGHT:
            game_state = STATE_GAMEOVER
            rpc.update(state="Game Over", details=f"Final Height: {score}", large_image="default", start=time.time())
            pygame.time.wait(500)

        for plat in platforms:
            pygame.draw.rect(screen, PLATFORM_COLOR, plat)

        player_trail.append(player.copy())
        if len(player_trail) > 10:
            player_trail.pop(0)
        for i, p in enumerate(player_trail):
            alpha = int(255 * (i + 1) / len(player_trail))
            s = pygame.Surface((player.width, player.height), pygame.SRCALPHA)
            s.fill((255, 100, 100, alpha))
            screen.blit(s, p)

        pygame.draw.rect(screen, PLAYER_COLOR, player)
        screen.blit(font.render(f"Height: {score}", True, (255, 255, 255)), (10, 10))

        if time.time() - last_rpc_update > 2:
            rpc.update(state=f"Height: {score}", details="Jumping higher...", large_image="default", start=time.time())
            last_rpc_update = time.time()

    elif game_state == STATE_GAMEOVER:
        game_over_label = big_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_label.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
        screen.blit(game_over_label, game_over_rect)
        score_label = font.render(f"Height: {score}", True, (255, 255, 255))
        score_rect = score_label.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        screen.blit(score_label, score_rect)
        restart_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 10, 180, 50)
        quit_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT//2 + 70, 180, 50)

        if draw_button("Restart", restart_btn, mouse_pos, mouse_click, t, base_color=(40, 120, 40), hover_color=(60, 200, 60)):
            reset_game()
            game_state = STATE_PLAYING
            rpc.update(state="Jumping again!", details="Restarted game", large_image="default", start=time.time())

        if draw_button("Quit", quit_btn, mouse_pos, mouse_click, t, base_color=(120, 40, 40), hover_color=(255, 60, 60)):
            game_state = STATE_MENU
            
    elif game_state == STATE_CREDITS:
        screen.fill((20, 20, 30))
        title = big_font.render("CREDITS", True, (255, 255, 120))
        title_rect = title.get_rect(center=(WIDTH // 2, 60))
        screen.blit(title, title_rect)

        credits = [
            ("Lead Developer:", "Lycan"),
            ("Game Designer:", "Lycan"),
            ("Distributed by:", None),
            (None, "Ruff's Software and Games"),
            (None, None),
            ("Art & Assets:", None),
            (None, "Paint (Yes, MS Paint)"),
            (None, "Google Font"),
            (None, None),
            ("Font:", "Atari Classic"),
            ("Engine:", "Pygame"),
            ("Special Thanks:", None),
            (None, "Bamboo Drew (The first tester - IT'S YOU!)") if is_drews_edition else (None, "Bamboo Drew (The first tester)"),
            ("AND THANKS TO:", None),
            (None, "Doodle Jump (A 16y.o game)"),
            (None, "for inspiration"),
        ]


        for i, (role, name) in enumerate(credits):
            role_text = font.render(role, True, (255, 200, 100))  # Role color
            name_text = font.render(name, True, (200, 200, 255))  # Name color

            total_width = role_text.get_width() + name_text.get_width() + 10
            x_start = WIDTH // 2 - total_width // 2
            y_pos = 140 + i * 35

            screen.blit(role_text, (x_start, y_pos))
            screen.blit(name_text, (x_start + role_text.get_width() + 10, y_pos))

    back_btn = pygame.Rect(20, HEIGHT - 60, 100, 40)
    if draw_button("Back", back_btn, mouse_pos, mouse_click, t,
                   base_color=(60, 60, 60), hover_color=(100, 100, 100)):
        set_window_size(400, 600)
        game_state = STATE_MENU


    pygame.display.flip()

rpc.clear()
rpc.close()
pygame.quit()
sys.exit()