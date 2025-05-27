#!/usr/bin/env python3
import sys
import math
import random
import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 200
WIND_ACCEL = 20
BUILDING_COLOR = (70, 70, 70)
MONKEY_RADIUS = 20
MONKEY_COLORS = [(255, 0, 0), (0, 0, 255)]

# Optional sprite images for more realistic gorillas (Player 1 and Player 2).
GORILLA_SPRITE_PATHS = ["assets/images/gorilla_red.png", "assets/images/gorilla_blue.png"]
BANANA_RADIUS = 5
BANANA_COLOR = (255, 255, 0)
EXPLOSION_RADIUS = 30
EXPLOSION_DURATION = 0.5
EXPLOSION_COLORS = [(255, 255, 255), (255, 200, 0), (255, 50, 0)]

def generate_buildings():
    """Generate a list of building surfaces and rects across the screen."""
    buildings = []
    x = 0
    while x < SCREEN_WIDTH:
        width = random.randint(50, 100)
        if x + width > SCREEN_WIDTH:
            width = SCREEN_WIDTH - x
        height = random.randint(100, 300)
        rect = pygame.Rect(x, SCREEN_HEIGHT - height, width, height)
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill(BUILDING_COLOR)
        cols = width // 20
        rows = height // 20
        for row in range(rows):
            for col in range(cols):
                wx = col * 20 + 4
                wy = row * 20 + 4
                color = (255, 255, 150) if random.random() < 0.3 else (50, 50, 50)
                pygame.draw.rect(surf, color, (wx, wy, 12, 12))
        buildings.append({"surf": surf, "rect": rect})
        x += width
    return buildings

def draw_buildings(screen, buildings):
    for b in buildings:
        screen.blit(b["surf"], b["rect"].topleft)

def damage_building(building, center, radius):
    """Carve a circular hole in the given building surface at center with radius."""
    local_x = int(center[0] - building["rect"].x)
    local_y = int(center[1] - building["rect"].y)
    pygame.draw.circle(building["surf"], (0, 0, 0, 0), (local_x, local_y), radius)
    
def create_background():
    """Return a surface with sky gradient and ground."""
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    top = (135, 206, 235)
    bottom = (255, 255, 255)
    for y in range(SCREEN_HEIGHT):
        r = top[0] + (bottom[0] - top[0]) * y // SCREEN_HEIGHT
        g = top[1] + (bottom[1] - top[1]) * y // SCREEN_HEIGHT
        b = top[2] + (bottom[2] - top[2]) * y // SCREEN_HEIGHT
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    pygame.draw.rect(surf, (50, 205, 50), (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40))
    return surf

def draw_banana(screen, banana):
    """Draw a banana sprite rotated to match its velocity direction."""
    vx, vy = banana["vel"]
    angle = math.degrees(math.atan2(-vy, vx))
    x, y = banana["pos"]
    surf = pygame.Surface((BANANA_RADIUS * 4, BANANA_RADIUS * 2), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, BANANA_COLOR, (0, 0, BANANA_RADIUS * 4, BANANA_RADIUS * 2))
    stem = [(0, BANANA_RADIUS), (4, 2), (4, BANANA_RADIUS * 2 - 2)]
    pygame.draw.polygon(surf, (160, 82, 45), stem)
    rot = pygame.transform.rotate(surf, angle)
    rect = rot.get_rect(center=(int(x), int(y)))
    screen.blit(rot, rect)

def draw_monkey(screen, pos, color):
    """Draw a stylized monkey with a bandana."""
    x, y = pos
    body_color = (139, 69, 19)
    head_r = MONKEY_RADIUS
    ear_r = head_r // 2
    pygame.draw.circle(screen, body_color, (x - head_r + ear_r, y), ear_r)
    pygame.draw.circle(screen, body_color, (x + head_r - ear_r, y), ear_r)
    pygame.draw.circle(screen, body_color, (x, y), head_r)
    strap_h = max(head_r // 4, 4)
    pygame.draw.rect(screen, color, (x - head_r, y - strap_h // 2, head_r * 2, strap_h))
    eye_r = max(head_r // 6, 2)
    eye_y = y - head_r // 4
    ex = head_r // 2
    pygame.draw.circle(screen, (255, 255, 255), (x - ex, eye_y), eye_r)
    pygame.draw.circle(screen, (255, 255, 255), (x + ex, eye_y), eye_r)
    pygame.draw.circle(screen, (0, 0, 0), (x - ex, eye_y), eye_r // 2)
    pygame.draw.circle(screen, (0, 0, 0), (x + ex, eye_y), eye_r // 2)
    bw = head_r
    bh = head_r * 3 // 2
    body_rect = pygame.Rect(x - bw // 2, y + head_r, bw, bh)
    pygame.draw.ellipse(screen, body_color, body_rect)
    ly = y + head_r + bh
    pygame.draw.line(screen, body_color, (x - bw // 4, ly), (x - bw // 2, ly + head_r), 3)
    pygame.draw.line(screen, body_color, (x + bw // 4, ly), (x + bw // 2, ly + head_r), 3)
    ay = y + head_r + head_r // 2
    pygame.draw.line(screen, body_color, (x - bw // 2, ay), (x - bw, ay + head_r // 2), 3)
    pygame.draw.line(screen, body_color, (x + bw // 2, ay), (x + bw, ay + head_r // 2), 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Gorilla 2.0")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont(None, 24)
    background = create_background()

    # Load gorilla sprites; fallback to primitive drawing if not found
    gorilla_sprites = []
    for path in GORILLA_SPRITE_PATHS:
        try:
            img = pygame.image.load(path).convert_alpha()
            sprite = pygame.transform.smoothscale(img, (MONKEY_RADIUS * 4, MONKEY_RADIUS * 4))
        except Exception:
            sprite = None
        gorilla_sprites.append(sprite)

    buildings = generate_buildings()
    p1_rect = buildings[0]["rect"]
    p2_rect = buildings[-1]["rect"]
    player_pos = [
        (p1_rect.x + p1_rect.width // 2, p1_rect.y - MONKEY_RADIUS),
        (p2_rect.x + p2_rect.width // 2, p2_rect.y - MONKEY_RADIUS),
    ]

    scores = [0, 0]
    turn = 0

    angle = 45
    power = 50
    wind = random.randint(-10, 10)

    banana = None
    explosion = None

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and banana is None and explosion is None:
                if event.key == pygame.K_UP:
                    angle = min(angle + 1, 180)
                elif event.key == pygame.K_DOWN:
                    angle = max(angle - 1, 0)
                elif event.key == pygame.K_RIGHT:
                    power = min(power + 1, 100)
                elif event.key == pygame.K_LEFT:
                    power = max(power - 1, 0)
                elif event.key == pygame.K_r:
                    wind = random.randint(-10, 10)
                elif event.key == pygame.K_SPACE:
                    theta = math.radians(angle if turn == 0 else 180 - angle)
                    speed = power * 2
                    vx = math.cos(theta) * speed
                    vy = -math.sin(theta) * speed
                    banana = {"pos": list(player_pos[turn]), "vel": [vx, vy]}

        if banana:
            banana["vel"][0] += wind * WIND_ACCEL * dt
            banana["vel"][1] += GRAVITY * dt
            banana["pos"][0] += banana["vel"][0] * dt
            banana["pos"][1] += banana["vel"][1] * dt

            x, y = banana["pos"]
            if x < 0 or x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
                banana = None
                turn = 1 - turn
                wind = random.randint(-10, 10)
            else:
                for b in buildings:
                    if b["rect"].collidepoint(x, y):
                        explosion = {"pos": (x, y), "timer": 0}
                        damage_building(b, (x, y), EXPLOSION_RADIUS)
                        banana = None
                        wind = random.randint(-10, 10)
                        turn = 1 - turn
                        break
                if banana:
                    target = player_pos[1 - turn]
                    dist = math.hypot(x - target[0], y - target[1])
                    if dist <= BANANA_RADIUS + MONKEY_RADIUS:
                        explosion = {"pos": (x, y), "timer": 0}
                        scores[turn] += 1
                        banana = None
                        wind = random.randint(-10, 10)
                        turn = 1 - turn

        if explosion:
            explosion["timer"] += dt
            if explosion["timer"] > EXPLOSION_DURATION:
                explosion = None

        screen.blit(background, (0, 0))
        draw_buildings(screen, buildings)
        # Draw gorillas: sprite if available, else fallback to primitives
        if gorilla_sprites[0]:
            rect = gorilla_sprites[0].get_rect(center=player_pos[0])
            screen.blit(gorilla_sprites[0], rect)
        else:
            draw_monkey(screen, player_pos[0], MONKEY_COLORS[0])
        if gorilla_sprites[1]:
            rect = gorilla_sprites[1].get_rect(center=player_pos[1])
            screen.blit(gorilla_sprites[1], rect)
        else:
            draw_monkey(screen, player_pos[1], MONKEY_COLORS[1])

        if banana:
            draw_banana(screen, banana)

        if explosion:
            t = explosion["timer"] / EXPLOSION_DURATION
            for i, color in enumerate(EXPLOSION_COLORS, start=1):
                r = int(EXPLOSION_RADIUS * t * i / len(EXPLOSION_COLORS))
                pygame.draw.circle(screen, color, (int(explosion["pos"][0]), int(explosion["pos"][1])), r)

        angle_surf = font.render(f"Turn: Player {turn+1}", True, (0, 0, 0))
        angle_val = font.render(f"Angle: {angle}", True, (0, 0, 0))
        power_val = font.render(f"Power: {power}", True, (0, 0, 0))
        wind_val = font.render(f"Wind: {wind}", True, (0, 0, 0))
        score_val = font.render(f"{scores[0]} - {scores[1]}", True, (0, 0, 0))
        instr = font.render("UP/DOWN: Angle  LEFT/RIGHT: Power  R: Wind  SPACE: Shoot", True, (0, 0, 0))

        screen.blit(angle_surf, (10, 10))
        screen.blit(angle_val, (10, 30))
        screen.blit(power_val, (10, 50))
        screen.blit(wind_val, (10, 70))
        screen.blit(score_val, (SCREEN_WIDTH - 100, 10))
        screen.blit(instr, (10, SCREEN_HEIGHT - 30))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()