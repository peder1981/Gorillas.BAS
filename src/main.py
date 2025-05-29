#!/usr/bin/env python3
import sys
import math
import random
import pygame
import os
import time
from PIL import Image, ImageOps

# Importar módulo de armazenamento
import game_storage

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
# Constantes físicas adequadas para um jogo 2D (sistema simples)
GRAVITY = 300       # Aceleração da gravidade em pixels/segundo²
WIND_FACTOR = 20    # Influência do vento em pixels/segundo²
VEL_FACTOR = 5      # Multiplicador de velocidade inicial (para ajustar "feel" do jogo)

# Constantes para energia dos gorilas
MAX_GORILLA_HEALTH = 100  # Energia máxima de cada gorila
DAMAGE_PER_HIT = 35       # Dano causado por acerto direto
DAMAGE_BUILDING_COLLAPSE = 20  # Dano causado quando prédio desaba
BUILDING_COLOR = (60, 60, 80)  # Cinza azulado para prédios urbanos
MONKEY_RADIUS = 7 # Originalmente 6. Aumentado em ~20% (6 * 1.2 = 7.2, arredondado para 7)
# Cores para o Gorila Realista: tons de cinza/preto.
# A cor original de MONKEY_COLORS (vermelho/azul) será usada para acessórios de distinção.
BEAST_FUR_COLORS = [(40, 40, 45), (60, 60, 65), (20, 20, 25)] # Cinzas escuros para gorila realista
MONKEY_COLORS = [(180, 50, 50), (50, 50, 180)] # Mantido para acessórios de distinção

# Sprites para gorilas (se existirem)
GORILLA_SPRITE_PATHS = ["assets/images/gorilla_red.png", "assets/images/gorilla_blue.png"]
BANANA_RADIUS = 4
# Banana amarela simples
BANANA_COLOR = (255, 255, 0)  # Amarelo clássico
EXPLOSION_RADIUS = 50
EXPLOSION_DURATION = 0.5
# Cores de explosão simples
EXPLOSION_COLORS = [
    (255, 255, 255),  # Branco
    (255, 200, 0),    # Amarelo
    (255, 100, 0),    # Laranja
    (255, 0, 0),      # Vermelho
]

def generate_buildings():
    """Gera prédios para um cenário urbano no estilo de Nova York."""
    buildings = []
    x = 0
    # Paleta de cores inspirada em Nova York
    nyc_building_colors = {
        "brick": [(130, 70, 60), (100, 50, 40), (150, 80, 70)],
        "stone": [(180, 170, 150), (200, 190, 170), (160, 150, 140)],
        "concrete": [(90, 90, 95), (70, 70, 75), (110, 110, 115)],
        "glass_steel": [(40, 50, 70), (30, 40, 60), (50, 60, 80)], # Para arranha-céus modernos
    }
    all_colors = [color for category in nyc_building_colors.values() for color in category]
    dark_structure_color = (50, 50, 55) # Para antenas, caixas d'água de metal
    wood_water_tank_color = (80, 60, 40) # Madeira escura para caixas d'água

    while x < SCREEN_WIDTH:
        width = random.randint(80, 200) # Largura dos prédios
        if x + width > SCREEN_WIDTH:
            width = SCREEN_WIDTH - x

        # Alturas variadas, com chance de arranha-céus
        is_skyscraper = random.random() < 0.15 # 15% de chance de ser um arranha-céu
        if is_skyscraper:
            height = random.randint(int(SCREEN_HEIGHT * 0.6), int(SCREEN_HEIGHT * 0.9))
            building_category = "glass_steel" # Arranha-céus tendem a ser de vidro/aço
        else:
            height = random.randint(150, int(SCREEN_HEIGHT * 0.55))
            building_category = random.choice(["brick", "stone", "concrete"])
        
        rect = pygame.Rect(x, SCREEN_HEIGHT - height, width, height)
        
        # Escolha da cor do prédio com base na categoria
        building_color = random.choice(nyc_building_colors[building_category])
        
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Aplicar gradiente sutil ou cor base
        # Para prédios de vidro/aço, um gradiente pode simular reflexo
        if building_category == "glass_steel":
            for iy in range(height):
                reflection_factor = 0.8 + (0.2 * iy / height) # Mais claro no topo
                column_color = (
                    int(building_color[0] * reflection_factor),
                    int(building_color[1] * reflection_factor),
                    int(building_color[2] * reflection_factor)
                )
                pygame.draw.line(surf, column_color, (0, iy), (width, iy))
        else: # Para outros materiais, um gradiente lateral
            for ix_grad in range(width):
                shadow_factor = 0.85 + (0.15 * ix_grad / width)  # Sombra sutil na lateral
                column_color = (
                    int(building_color[0] * shadow_factor),
                    int(building_color[1] * shadow_factor),
                    int(building_color[2] * shadow_factor)
                )
                pygame.draw.line(surf, column_color, (ix_grad, 0), (ix_grad, height))
        
        # Desenhar janelas
        window_width, window_height = 8, 12
        if is_skyscraper:
            window_width, window_height = 10, 18 # Janelas maiores para arranha-céus
        window_spacing_x, window_spacing_y = 15, 25
        window_margin = 10
        
        window_colors = [
            (255, 240, 180, 200),  # Luz amarela (com alfa)
            (230, 230, 220, 200),  # Luz branca (com alfa)
            (50, 50, 60, 150),     # Janela escura/reflexo (com alfa)
            (20, 20, 30, 220)      # Janela bem escura (com alfa)
        ]

        for r in range(window_margin, height - window_height - window_margin, window_spacing_y):
            for c in range(window_margin, width - window_width - window_margin, window_spacing_x):
                if random.random() < 0.7: # 70% de chance de ter uma janela
                    win_color = random.choice(window_colors)
                    # Para prédios de vidro, as janelas podem ser mais integradas ou ser a própria textura
                    if building_category == "glass_steel" and random.random() < 0.5:
                        # Simular faixas de vidro ou reflexos
                        if random.random() < 0.3:
                             pygame.draw.rect(surf, (win_color[0],win_color[1],win_color[2], 100), (c, r, window_width, height - r - window_margin), border_radius=1)
                        # else: não desenha janela individual, o gradiente do prédio já faz o efeito
                    else:
                        pygame.draw.rect(surf, win_color, (c, r, window_width, window_height), border_radius=1)
                        if random.random() < 0.2: # Pequeno brilho na janela
                            pygame.draw.circle(surf, (255,255,255,50), (c+3,r+3),2)

        # Detalhes no topo do prédio
        top_y_offset = 5 # Pequeno offset para desenhar no topo
        # Parapeito simples para prédios mais baixos
        if not is_skyscraper and random.random() < 0.6:
            parapet_height = random.randint(5, 10)
            parapet_color = (int(building_color[0]*0.7), int(building_color[1]*0.7), int(building_color[2]*0.7))
            pygame.draw.rect(surf, parapet_color, (0, 0, width, parapet_height))
            top_y_offset += parapet_height

        # Antenas (mais comuns em arranha-céus ou prédios altos)
        if (is_skyscraper or random.random() < 0.3) and random.random() < 0.5:
            num_antennas = random.randint(1, 3 if is_skyscraper else 1)
            for _ in range(num_antennas):
                antenna_height = random.randint(20, 60 if is_skyscraper else 40)
                antenna_width = random.randint(2, 5 if is_skyscraper else 3)
                antenna_x = random.randint(width//4, width - width//4 - antenna_width)
                pygame.draw.rect(surf, dark_structure_color, (antenna_x, top_y_offset - antenna_height, antenna_width, antenna_height))
                if random.random() < 0.7:
                    pygame.draw.circle(surf, (255, 0, 0, 200), (antenna_x + antenna_width//2, top_y_offset - antenna_height), 2)
        
        # Caixas d'água (mais comuns em prédios de tijolo/pedra mais antigos)
        if not is_skyscraper and building_category in ["brick", "stone"] and random.random() < 0.4:
            margin = 10
            min_tank_width_content = 20 
            max_tank_width_content_limit = 50
            min_tank_height = 15 
            max_tank_height = 30

            if width >= min_tank_width_content + (2 * margin):
                max_tank_width_allowed_by_building = width - (2 * margin)
                actual_max_tank_width = min(max_tank_width_content_limit, max_tank_width_allowed_by_building)
                if actual_max_tank_width >= min_tank_width_content:
                    tank_width = random.randint(min_tank_width_content, actual_max_tank_width)
                    tank_height = random.randint(min_tank_height, max_tank_height)
                    tank_x_start_range_on_surf = margin
                    tank_x_end_range_on_surf = width - tank_width - margin
                    if tank_x_start_range_on_surf <= tank_x_end_range_on_surf:
                        tank_x_on_surf = random.randint(tank_x_start_range_on_surf, tank_x_end_range_on_surf)
                        tank_color = wood_water_tank_color if random.random() < 0.7 else dark_structure_color # Madeira ou metal
                        pygame.draw.rect(surf, tank_color, (tank_x_on_surf, top_y_offset, tank_width, tank_height))
                        # Pernas da caixa d'água
                        leg_height = 5
                        pygame.draw.line(surf, dark_structure_color, (tank_x_on_surf + 2, top_y_offset + tank_height), (tank_x_on_surf + 2, top_y_offset + tank_height + leg_height), 2)
                        pygame.draw.line(surf, dark_structure_color, (tank_x_on_surf + tank_width - 2, top_y_offset + tank_height), (tank_x_on_surf + tank_width - 2, top_y_offset + tank_height + leg_height), 2)
        
        buildings.append({"surf": surf, "rect": rect})
        x += width
    return buildings

def draw_buildings(screen, buildings):
    for b in buildings:
        screen.blit(b["surf"], b["rect"].topleft)

def damage_building(building, center, radius):
    """Causa dano (remove pixels) em um prédio a partir de um ponto"""
    surf = building["surf"]
    x, y = center[0] - building["rect"].x, center[1] - building["rect"].y
    # Converter para inteiros para usar no range
    x_int, y_int = int(x), int(y)
    radius_int = int(radius)
    
    # Usar valores inteiros para o range
    for py in range(max(0, y_int-radius_int), min(surf.get_height(), y_int+radius_int+1)):
        for px in range(max(0, x_int-radius_int), min(surf.get_width(), x_int+radius_int+1)):
            # Usar valores originais (float) para o cálculo de distância para maior precisão
            if math.hypot(px-x, py-y) <= radius:
                surf.set_at((px, py), (0, 0, 0, 0))
    
    return check_building_collapse(building)

def check_building_collapse(building):
    """Verifica se um prédio tem sustentação ou deve desabar"""
    surf = building["surf"]
    width = surf.get_width()
    height = surf.get_height()
    
    # Verificar se a base do prédio foi danificada demais
    base_intact_pixels = 0
    base_check_height = min(30, height // 5)  # Verificar os 30 pixels inferiores ou 20% da altura
    
    for px in range(width):
        for py in range(height - base_check_height, height):
            # Verificar se o pixel ainda existe (não é transparente)
            if surf.get_at((px, py))[3] > 0:  # Alpha > 0 significa que o pixel é visível
                base_intact_pixels += 1
    
    # Calcular a porcentagem de pixels intactos na base
    base_total_pixels = width * base_check_height
    base_intact_percentage = base_intact_pixels / base_total_pixels
    
    # Se menos de 30% da base estiver intacta, o prédio deve desabar
    return base_intact_percentage < 0.3

def create_background():
    """Cria um plano de fundo urbano noturno para o jogo"""
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Gradiente de céu noturno - do azul escuro para preto
    top_color = (10, 20, 40)  # Azul muito escuro no topo
    bottom_color = (5, 5, 15)  # Quase preto embaixo
    
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # Adicionar estrelas aleatórias
    for _ in range(100):
        star_x = random.randint(0, SCREEN_WIDTH)
        star_y = random.randint(0, SCREEN_HEIGHT // 2)
        brightness = random.randint(150, 255)
        size = random.randint(1, 2)
        pygame.draw.circle(surf, (brightness, brightness, brightness), (star_x, star_y), size)
    
    # Lua com crateras para um aspecto mais realista
    moon_radius = 40
    moon_x, moon_y = SCREEN_WIDTH - 120, 80
    
    # Lua base
    pygame.draw.circle(surf, (220, 220, 200), (moon_x, moon_y), moon_radius)
    
    # Adicionar algumas crateras para realismo
    for _ in range(6):
        crater_size = random.randint(4, 10)
        crater_x = moon_x + random.randint(-moon_radius + 10, moon_radius - 10)
        crater_y = moon_y + random.randint(-moon_radius + 10, moon_radius - 10)
        # Certificar que a cratera está dentro da lua
        if math.hypot(crater_x - moon_x, crater_y - moon_y) < moon_radius - crater_size:
            pygame.draw.circle(surf, (180, 180, 160), (crater_x, crater_y), crater_size)
    
    # Adicionar um brilho suave ao redor da lua
    glow_surf = pygame.Surface((moon_radius*4, moon_radius*4), pygame.SRCALPHA)
    for i in range(10):
        alpha = 15 - i * 1.5  # Diminui a opacidade para os círculos externos
        if alpha > 0:
            radius = moon_radius + i * 3
            pygame.draw.circle(glow_surf, (220, 220, 200, int(alpha)), 
                              (moon_radius*2, moon_radius*2), radius)
    
    # Aplicar o brilho
    surf.blit(glow_surf, (moon_x - moon_radius*2, moon_y - moon_radius*2))
    
    # Adicionar silhueta de cidade distante (efeito de profundidade)
    city_height = 30
    city_y = SCREEN_HEIGHT - 280  # Posicionar acima dos prédios principais
    
    # Criar uma silhueta irregular para a cidade distante
    for x in range(0, SCREEN_WIDTH, 20):
        height_var = random.randint(10, city_height)
        width_var = random.randint(15, 35)
        pygame.draw.rect(surf, (20, 20, 30), 
                        (x, city_y - height_var, width_var, height_var))
    
    return surf

def draw_explosion(screen, pos, progress):
    """Desenha uma explosão realista e dramática"""
    x, y = int(pos[0]), int(pos[1])
    
    # 1. Núcleo brilhante
    core_radius = int(EXPLOSION_RADIUS * progress * 0.4)
    pygame.draw.circle(screen, (255, 255, 220), (x, y), core_radius)
    
    # 2. Camada de choque principal
    main_radius = int(EXPLOSION_RADIUS * progress * 0.8)
    glow_surf = pygame.Surface((main_radius*2, main_radius*2), pygame.SRCALPHA)
    for r in range(main_radius, int(main_radius*0.4), -2):
        alpha = 255 - int((main_radius - r) * (255 / main_radius * 0.7))
        # Gradiente de cores de explosão (amarelo -> laranja -> vermelho)
        if r > main_radius * 0.8:
            color = (255, 255, 150, alpha)  # Amarelo
        elif r > main_radius * 0.6:
            color = (255, 200, 50, alpha)   # Laranja amarelado
        elif r > main_radius * 0.4:
            color = (255, 100, 20, alpha)   # Laranja
        else:
            color = (200, 50, 20, alpha)    # Vermelho
        pygame.draw.circle(glow_surf, color, (main_radius, main_radius), r)
    
    # Aplicar a camada principal
    screen.blit(glow_surf, (x - main_radius, y - main_radius))
    
    # 3. Onda de choque externa
    outer_radius = int(EXPLOSION_RADIUS * progress)
    shock_width = int(EXPLOSION_RADIUS * 0.05)
    shock_color = (200, 200, 200, 100)
    
    # Desenhar anel externo
    shock_surf = pygame.Surface((outer_radius*2, outer_radius*2), pygame.SRCALPHA)
    pygame.draw.circle(shock_surf, shock_color, (outer_radius, outer_radius), outer_radius)
    pygame.draw.circle(shock_surf, (0, 0, 0, 0), (outer_radius, outer_radius), outer_radius - shock_width)
    screen.blit(shock_surf, (x - outer_radius, y - outer_radius))
    
    # 4. Partículas (opção simplificada sem rastreamento de partículas individuais)
    particles_count = 12
    for i in range(particles_count):
        angle = math.pi * 2 * i / particles_count
        dist = EXPLOSION_RADIUS * progress * 0.7
        particle_x = x + math.cos(angle) * dist
        particle_y = y + math.sin(angle) * dist
        size = max(2, int(5 * (1 - progress)))
        color = random.choice([(100, 100, 100), (80, 80, 80), (60, 60, 60)])
        pygame.draw.circle(screen, color, (int(particle_x), int(particle_y)), size)

def draw_banana(screen, banana):
    """Desenha uma banana realista com efeito de movimento"""
    vx, vy = banana["vel"]
    angle = math.degrees(math.atan2(-vy, vx))
    x, y = banana["pos"]
    
    # Dimensões da banana
    banana_width = BANANA_RADIUS * 6
    banana_height = BANANA_RADIUS * 2.5
    
    # Criar superfície para a banana
    surf = pygame.Surface((banana_width, banana_height), pygame.SRCALPHA)
    
    # Cores da banana - amarelo principal e sombras
    yellow = BANANA_COLOR
    dark_yellow = (220, 220, 0)
    highlight = (255, 255, 200)
    
    # Desenhar a forma curva da banana (arco)
    curve_angle = 30  # Graus de curvatura
    curve_radius = banana_height * 2
    
    # Centro do arco maior
    arc_center_x = banana_width // 2
    arc_center_y = banana_height * 2
    
    # Desenhar a banana em camadas para dar profundidade
    # Camada base (mais escura)
    pygame.draw.ellipse(surf, dark_yellow, (0, 0, banana_width, banana_height))
    
    # Camada do meio (cor principal)
    inner_width = banana_width * 0.85
    inner_height = banana_height * 0.85
    inner_x = (banana_width - inner_width) // 2
    inner_y = (banana_height - inner_height) // 2
    pygame.draw.ellipse(surf, yellow, (inner_x, inner_y, inner_width, inner_height))
    
    # Adicionar destaque na parte superior para dar dimensão
    highlight_width = banana_width * 0.5
    highlight_height = banana_height * 0.3
    highlight_x = banana_width * 0.25
    highlight_y = banana_height * 0.2
    pygame.draw.ellipse(surf, highlight, (highlight_x, highlight_y, highlight_width, highlight_height))
    
    # Adicionar extremidades (pontas da banana)
    for end_x in [banana_width * 0.1, banana_width * 0.9]:
        end_y = banana_height // 2
        end_width = banana_width * 0.15
        end_height = banana_height * 0.4
        pygame.draw.ellipse(surf, dark_yellow, (end_x - end_width/2, end_y - end_height/2, end_width, end_height))
    
    # Rotacionar a banana
    rot = pygame.transform.rotate(surf, angle)
    rect = rot.get_rect(center=(int(x), int(y)))
    
    # Adicionar rastro de movimento para mostrar a trajetória
    # Criar uma superfície para o rastro
    trail_segments = 5
    for i in range(1, trail_segments+1):
        # Calcular posição anterior na trajetória
        trail_x = x - vx * i * 0.05
        trail_y = y - vy * i * 0.05
        
        # Diminuir o tamanho e opacidade para cada segmento do rastro
        trail_scale = 1.0 - (i * 0.15)
        trail_alpha = 255 - (i * 40)
        
        # Criar uma versão reduzida e mais transparente da banana
        if trail_scale > 0.2:  # Evitar rastros muito pequenos
            scaled_width = int(rot.get_width() * trail_scale)
            scaled_height = int(rot.get_height() * trail_scale)
            if scaled_width > 0 and scaled_height > 0:  # Verificar dimensões válidas
                trail_surf = pygame.transform.scale(rot.copy(), (scaled_width, scaled_height))
                # Ajustar a opacidade
                trail_surf.set_alpha(trail_alpha)
                # Calcular posição para centralizar o rastro
                trail_rect = trail_surf.get_rect(center=(int(trail_x), int(trail_y)))
                screen.blit(trail_surf, trail_rect)
    
    # Desenhar a banana principal
    screen.blit(rot, rect)

def draw_health_bar(screen, pos, health, max_health, width=50, height=5, border=1):
    """Desenha uma barra de energia acima do gorila"""
    x, y = pos
    # Posicionar barra acima do gorila
    bar_pos = (x - width//2, y - MONKEY_RADIUS * 2.5)
    
    # Calcular largura da barra baseada na saúde atual
    health_percent = max(0, min(health / max_health, 1.0))
    filled_width = int(width * health_percent)
    
    # Definir cores baseadas na porcentagem de saúde
    if health_percent > 0.7:
        color = (0, 200, 0)  # Verde
    elif health_percent > 0.3:
        color = (200, 200, 0)  # Amarelo
    else:
        color = (200, 0, 0)  # Vermelho
    
    # Desenhar borda
    pygame.draw.rect(screen, (50, 50, 50), (bar_pos[0], bar_pos[1], width, height))
    
    # Desenhar barra de saúde
    if health > 0:
        pygame.draw.rect(screen, color, (bar_pos[0], bar_pos[1], filled_width, height))

def draw_monkey(screen, pos, color, health=MAX_GORILLA_HEALTH):
    """Desenha um gorila musculoso com pelos escuros, buscando um estilo mais realista.
    Inclui uma barra de energia acima do gorila."""
    # Desenhar a barra de energia primeiro
    draw_health_bar(screen, pos, health, MAX_GORILLA_HEALTH)
    x, y = pos
    radius = MONKEY_RADIUS # radius agora é o novo tamanho aumentado

    # Fator de deslocamento para simular arqueamento/flexão dos membros
    # Aumentado para um arqueamento mais pronunciado, como primatas.
    bend_offset = radius * 0.9 # Originalmente radius * 0.8, aumentado para 0.9

    # Deslocamentos para leve curvatura do corpo (cabeça e peito para frente)
    head_forward_offset = radius * 0.15
    chest_forward_offset = radius * 0.1

    # Cores (mantendo a paleta, mas a aplicação será mais sutil)
    deep_shadow_fur = BEAST_FUR_COLORS[2] # (20, 20, 25) Para oclusão e sombras profundas
    base_fur = BEAST_FUR_COLORS[0]      # (40, 40, 45) Cor principal do pelo
    mid_highlight_fur = BEAST_FUR_COLORS[1] # (60, 60, 65) Destaques suaves
    # Para um brilho especular sutil, podemos usar um tom ainda mais claro ou misturar com branco
    specular_highlight_fur = (80, 80, 85) 

    skin_tone_shadow = (55, 55, 60)     # Pele em áreas de sombra
    skin_tone_base = (70, 70, 75)       # Pele principal
    skin_tone_highlight = (85, 85, 90)  # Destaque sutil na pele

    eye_sclera = (180, 170, 160)      # Esclera menos vibrante
    eye_pupil = (15, 10, 5)           # Pupila escura, levemente acastanhada
    eye_catchlight = (220, 220, 210)  # Ponto de luz no olho

    accent_color = color

    # Helper para desenhar "tufos" de pelo ou formas orgânicas
    def draw_fur_patch(surface, color, points, width=0, aa=True):
        if len(points) > 2:
            pygame.draw.polygon(surface, color, points, width)
            if aa: # Anti-aliasing manual para as bordas se não for preenchido
                 pygame.draw.aalines(surface, color, True, points, 1)
        elif len(points) == 2:
            pygame.draw.line(surface, color, points[0], points[1], max(1,int(width)) if width > 0 else 1)
            if aa:
                 pygame.draw.aaline(surface, color, points[0], points[1], 1)

    # --- CABEÇA E ROSTO --- (Mais foco em estrutura óssea e menos simetria)
    head_radius = radius * 0.8
    head_center_x = x + head_forward_offset # Levemente para frente
    head_center_y = y - radius * 1.2 # Posição Y da cabeça (topo)
    head_base_y = head_center_y + head_radius * 0.6  # Base do crânio/pescoço
    head_top_y = head_base_y - radius * 1.8 # Topo da cabeça (crista sagital implícita)
    head_width = radius * 1.6

    # Formato do crânio (camada mais escura, base)
    skull_base_points = [
        (head_center_x - head_width * 0.5, head_base_y),
        (head_center_x - head_width * 0.6, head_base_y - radius * 0.7), # Têmpora
        (head_center_x - head_width * 0.3, head_top_y + radius * 0.2), # Topo lateral
        (head_center_x, head_top_y), # Crista sagital central
        (head_center_x + head_width * 0.3, head_top_y + radius * 0.2),
        (head_center_x + head_width * 0.6, head_base_y - radius * 0.7),
        (head_center_x + head_width * 0.5, head_base_y),
    ]
    draw_fur_patch(screen, deep_shadow_fur, skull_base_points)

    # Volume principal do pelo da cabeça
    skull_mid_points = [
        (head_center_x - head_width * 0.45, head_base_y - radius * 0.1),
        (head_center_x - head_width * 0.55, head_base_y - radius * 0.75), 
        (head_center_x - head_width * 0.25, head_top_y + radius * 0.25),
        (head_center_x, head_top_y + radius*0.05), 
        (head_center_x + head_width * 0.25, head_top_y + radius * 0.25),
        (head_center_x + head_width * 0.55, head_base_y - radius * 0.75),
        (head_center_x + head_width * 0.45, head_base_y - radius * 0.1),
    ]
    draw_fur_patch(screen, base_fur, skull_mid_points)
    # Destaques no topo da cabeça
    draw_fur_patch(screen, mid_highlight_fur, [
        (head_center_x - head_width * 0.15, head_top_y + radius * 0.3),
        (head_center_x, head_top_y + radius*0.15), 
        (head_center_x + head_width * 0.15, head_top_y + radius * 0.3),
        (head_center_x, head_top_y + radius*0.45), 
    ])

    # Área da face (pele)
    face_center_y = head_base_y - radius * 0.5
    face_skin_points = [
        (head_center_x - radius * 0.7, face_center_y + radius * 0.6), # Mandíbula inferior esquerda
        (head_center_x - radius * 0.75, face_center_y - radius * 0.1), # Têmpora esquerda
        (head_center_x - radius * 0.4, face_center_y - radius * 0.7), # Testa esquerda
        (head_center_x + radius * 0.4, face_center_y - radius * 0.7), # Testa direita
        (head_center_x + radius * 0.75, face_center_y - radius * 0.1), # Têmpora direita
        (head_center_x + radius * 0.7, face_center_y + radius * 0.6), # Mandíbula inferior direita
        (head_center_x, face_center_y + radius * 0.75), # Queixo
    ]
    pygame.draw.polygon(screen, skin_tone_base, face_skin_points)
    # Sombra na pele da face
    pygame.draw.polygon(screen, skin_tone_shadow, [
        (head_center_x - radius * 0.65, face_center_y + radius * 0.55),
        (head_center_x - radius * 0.7, face_center_y - radius * 0.05),
        (head_center_x, face_center_y - radius * 0.6), # Abaixo da testa
        (head_center_x + radius * 0.7, face_center_y - radius * 0.05),
        (head_center_x + radius * 0.65, face_center_y + radius * 0.55),
        (head_center_x, face_center_y + radius * 0.7), 
    ])

    # Arco supraciliar (testa pronunciada)
    brow_ridge_y = face_center_y - radius * 0.45
    brow_points = [
        (head_center_x - radius * 0.6, brow_ridge_y + radius * 0.05),
        (head_center_x - radius * 0.4, brow_ridge_y - radius * 0.15),
        (head_center_x, brow_ridge_y - radius * 0.2), # Centro da testa
        (head_center_x + radius * 0.4, brow_ridge_y - radius * 0.15),
        (head_center_x + radius * 0.6, brow_ridge_y + radius * 0.05),
        (head_center_x, brow_ridge_y + radius * 0.15) # Parte inferior da testa central
    ]
    pygame.draw.polygon(screen, skin_tone_highlight, brow_points) # Destaque na testa
    pygame.draw.polygon(screen, skin_tone_base, [
         (brow_points[0][0], brow_points[0][1] + radius*0.05), (brow_points[1][0], brow_points[1][1]+radius*0.05),
         (brow_points[2][0], brow_points[2][1]+radius*0.05), (brow_points[3][0], brow_points[3][1]+radius*0.05),
         (brow_points[4][0], brow_points[4][1]+radius*0.05), (brow_points[5][0], brow_points[5][1]+radius*0.05)
    ], int(radius*0.1)) # Espessura da testa

    # Olhos (menores, mais profundos)
    eye_y_pos = brow_ridge_y + radius * 0.25
    eye_x_offset = radius * 0.3
    # Cavidade ocular (sombra)
    pygame.draw.ellipse(screen, skin_tone_shadow, (head_center_x - eye_x_offset - radius*0.2, eye_y_pos - radius*0.15, radius*0.4, radius*0.3))
    pygame.draw.ellipse(screen, skin_tone_shadow, (head_center_x + eye_x_offset - radius*0.2, eye_y_pos - radius*0.15, radius*0.4, radius*0.3))
    # Esclera
    pygame.draw.ellipse(screen, eye_sclera, (head_center_x - eye_x_offset - radius*0.1, eye_y_pos - radius*0.07, radius*0.2, radius*0.14))
    pygame.draw.ellipse(screen, eye_sclera, (head_center_x + eye_x_offset - radius*0.1, eye_y_pos - radius*0.07, radius*0.2, radius*0.14))
    # Pupila
    pygame.draw.circle(screen, eye_pupil, (int(head_center_x - eye_x_offset), int(eye_y_pos)), int(radius*0.06))
    pygame.draw.circle(screen, eye_pupil, (int(head_center_x + eye_x_offset), int(eye_y_pos)), int(radius*0.06))
    # Brilho no olho
    pygame.draw.circle(screen, eye_catchlight, (int(head_center_x - eye_x_offset + radius*0.02), int(eye_y_pos - radius*0.02)), int(radius*0.025))
    pygame.draw.circle(screen, eye_catchlight, (int(head_center_x + eye_x_offset + radius*0.02), int(eye_y_pos - radius*0.02)), int(radius*0.025))

    # Nariz e Focinho
    snout_center_y = face_center_y + radius * 0.25
    # Base do focinho (pele)
    snout_base_points = [
        (head_center_x - radius*0.5, snout_center_y - radius*0.1),
        (head_center_x - radius*0.3, snout_center_y - radius*0.25), # Topo do nariz
        (head_center_x + radius*0.3, snout_center_y - radius*0.25),
        (head_center_x + radius*0.5, snout_center_y - radius*0.1),
        (head_center_x + radius*0.35, snout_center_y + radius*0.3), # Lábio superior
        (head_center_x - radius*0.35, snout_center_y + radius*0.3),
    ]
    pygame.draw.polygon(screen, skin_tone_base, snout_base_points)
    # Sombra abaixo do nariz
    pygame.draw.polygon(screen, skin_tone_shadow, [
        (snout_base_points[0][0]+radius*0.05, snout_base_points[0][1]+radius*0.05),
        (snout_base_points[1][0], snout_base_points[1][1]+radius*0.05),
        (snout_base_points[2][0], snout_base_points[2][1]+radius*0.05),
        (snout_base_points[3][0]-radius*0.05, snout_base_points[3][1]+radius*0.05),
        (head_center_x, snout_center_y + radius*0.2) # Centro do lábio superior
    ])
    # Narinas (mais orgânicas)
    nostril_l_points = [(head_center_x - radius*0.2, snout_center_y - radius*0.05), (head_center_x - radius*0.15, snout_center_y + radius*0.05), (head_center_x - radius*0.25, snout_center_y + radius*0.05)]
    nostril_r_points = [(head_center_x + radius*0.2, snout_center_y - radius*0.05), (head_center_x + radius*0.15, snout_center_y + radius*0.05), (head_center_x + radius*0.25, snout_center_y + radius*0.05)]
    pygame.draw.polygon(screen, deep_shadow_fur, nostril_l_points)
    pygame.draw.polygon(screen, deep_shadow_fur, nostril_r_points)

    # Boca
    mouth_y = snout_center_y + radius * 0.35
    pygame.draw.line(screen, skin_tone_shadow, (head_center_x - radius*0.25, mouth_y), (head_center_x + radius*0.25, mouth_y), int(radius*0.08))

    # --- CORPO --- (Ombros largos, peito forte, mais definição muscular)
    body_top_y = y
    body_height = radius * 3.3
    shoulder_width = radius * 3.2
    waist_width = radius * 1.8

    # Massa principal do torso (pelo base)
    torso_base_points = [
        (x - shoulder_width * 0.5, body_top_y), # Ombro esquerdo
        (x - shoulder_width * 0.55, body_top_y + radius * 0.5), # Lateral do peito esquerdo
        (x - waist_width * 0.6, body_top_y + body_height * 0.8), # Cintura esquerda
        (x - waist_width * 0.3, body_top_y + body_height), # Pelve esquerda
        (x + waist_width * 0.3, body_top_y + body_height), # Pelve direita
        (x + waist_width * 0.6, body_top_y + body_height * 0.8), # Cintura direita
        (x + shoulder_width * 0.55, body_top_y + radius * 0.5), # Lateral do peito direito
        (x + shoulder_width * 0.5, body_top_y), # Ombro direito
        (x, body_top_y - radius*0.1) # Trapézio sutil
    ]
    draw_fur_patch(screen, base_fur, torso_base_points)

    # Sombras profundas no torso (axilas, abaixo dos peitorais)
    torso_shadow_points = [
        (x - shoulder_width * 0.45, body_top_y + radius * 0.3),
        (x - waist_width * 0.5, body_top_y + body_height * 0.7),
        (x, body_top_y + body_height * 0.85),
        (x + waist_width * 0.5, body_top_y + body_height * 0.7),
        (x + shoulder_width * 0.45, body_top_y + radius * 0.3),
        (x, body_top_y + radius * 0.6) # Centro do peito (sombra)
    ]
    draw_fur_patch(screen, deep_shadow_fur, torso_shadow_points)

    # Destaques no peito e ombros
    chest_highlight_points_l = [
        (x - shoulder_width * 0.4, body_top_y + radius * 0.2),
        (x - radius * 0.5, body_top_y + radius * 1.2),
        (x - radius * 0.8, body_top_y + radius * 0.8),
    ]
    draw_fur_patch(screen, mid_highlight_fur, chest_highlight_points_l)
    chest_highlight_points_r = [
        (x + shoulder_width * 0.4, body_top_y + radius * 0.2),
        (x + radius * 0.5, body_top_y + radius * 1.2),
        (x + radius * 0.8, body_top_y + radius * 0.8),
    ]
    draw_fur_patch(screen, mid_highlight_fur, chest_highlight_points_r)
    # Destaque especular sutil nos ombros
    pygame.draw.circle(screen, specular_highlight_fur, (int(x - shoulder_width * 0.35), int(body_top_y + radius*0.3)), int(radius*0.3))
    pygame.draw.circle(screen, specular_highlight_fur, (int(x + shoulder_width * 0.35), int(body_top_y + radius*0.3)), int(radius*0.3))

    # Peitorais (pele)
    pec_width = radius * 1.6
    pec_height = radius * 0.8
    pec_y = body_top_y + radius * 0.5
    # ... (código dos peitorais permanece o mesmo)

    # --- BRAÇOS --- (Musculosos, agora com arqueamento)
    # Variáveis de braço (algumas podem ser de uma versão anterior, mas úteis para forma)
    arm_length_upper = radius * 1.5 
    arm_length_lower = radius * 1.6 
    hand_size = radius * 0.9

    # Pontos chave para membros (ombros, cotovelos, quadris, joelhos)
    # Ombros e quadris MAIS AFASTADOS do centro para uma postura mais larga
    shoulder_l_pos = (x - radius * 0.8, y - radius * 0.2) # X: 0.5->0.8, Y: 0.3->0.2 (ombros um pouco mais altos)
    # Cotovelo esquerdo AINDA MAIS para fora
    elbow_l_pos = (shoulder_l_pos[0] - radius * 1.0, shoulder_l_pos[1] + arm_length_upper * 0.8) # X: 0.7->1.0, Y: 0.9->0.8
    # Antebraço angulado para dentro, ajustando para o cotovelo mais aberto
    original_wrist_l_pos = (elbow_l_pos[0] + radius * 0.6, elbow_l_pos[1] + arm_length_lower * 1.1) # X: 0.3->0.6, Y: arm_length_lower -> arm_length_lower * 1.1
    wrist_l_pos = (original_wrist_l_pos[0] + bend_offset * 0.7, original_wrist_l_pos[1] - bend_offset * 1.2) # X: 0.8->0.7, Y: 1.1->1.2

    shoulder_r_pos = (x + radius * 0.8, y - radius * 0.2) # X: 0.5->0.8, Y: 0.3->0.2
    # Cotovelo direito AINDA MAIS para fora
    elbow_r_pos = (shoulder_r_pos[0] + radius * 1.0, shoulder_r_pos[1] + arm_length_upper * 0.8) # X: 0.7->1.0, Y: 0.9->0.8
    # Antebraço angulado para dentro
    original_wrist_r_pos = (elbow_r_pos[0] - radius * 0.6, elbow_r_pos[1] + arm_length_lower * 1.1) # X: 0.3->0.6, Y: arm_length_lower -> arm_length_lower * 1.1
    wrist_r_pos = (original_wrist_r_pos[0] - bend_offset * 0.7, original_wrist_r_pos[1] - bend_offset * 1.2) # X: 0.8->0.7, Y: 1.1->1.2

    hip_l_pos = (x - radius * 0.6, y + radius * 1.1) # X: 0.3->0.6, Y: 1.2->1.1 (quadril um pouco mais alto)
    # Joelho esquerdo AINDA MAIS para fora
    original_knee_l_pos = (hip_l_pos[0] - radius * 1.1, hip_l_pos[1] + radius * 1.6) # X: 0.8->1.1, Y: 1.7->1.6
    knee_l_pos = (original_knee_l_pos[0] + bend_offset * 0.3, original_knee_l_pos[1] - bend_offset * 0.1) # X:0.4->0.3, Y: 0.2->0.1
    # Panturrilha angulada para dentro
    original_ankle_l_pos = (knee_l_pos[0] + radius * 0.7, knee_l_pos[1] + radius * 1.5) # X: 0.4->0.7, Y: 1.6->1.5
    ankle_l_pos = (original_ankle_l_pos[0] + bend_offset * 0.6, original_ankle_l_pos[1] - bend_offset * 0.9) # X:0.7->0.6, Y: 1.0->0.9

    hip_r_pos = (x + radius * 0.6, y + radius * 1.1) # X: 0.3->0.6, Y: 1.2->1.1
    # Joelho direito AINDA MAIS para fora
    original_knee_r_pos = (hip_r_pos[0] + radius * 1.1, hip_r_pos[1] + radius * 1.6) # X: 0.8->1.1, Y: 1.7->1.6
    knee_r_pos = (original_knee_r_pos[0] - bend_offset * 0.3, original_knee_r_pos[1] - bend_offset * 0.1) # X:0.4->0.3, Y: 0.2->0.1
    # Panturrilha angulada para dentro
    original_ankle_r_pos = (knee_r_pos[0] - radius * 0.7, knee_r_pos[1] + radius * 1.5) # X: 0.4->0.7, Y: 1.6->1.5
    ankle_r_pos = (original_ankle_r_pos[0] - bend_offset * 0.6, original_ankle_r_pos[1] - bend_offset * 0.9) # X:0.7->0.6, Y: 1.0->0.9

    # Braço Esquerdo
    # Úmero (braço superior)
    humerus_l_points = [
        shoulder_l_pos,
        (shoulder_l_pos[0] - radius * 0.7, shoulder_l_pos[1] + radius * 0.5),
        (elbow_l_pos[0] - radius * 0.3, elbow_l_pos[1] - radius * 0.2),
        (elbow_l_pos[0] + radius * 0.4, elbow_l_pos[1] - radius * 0.4)
    ]
    draw_fur_patch(screen, base_fur, humerus_l_points)
    humerus_l_highlight_points = [
        (shoulder_l_pos[0] - radius * 0.2, shoulder_l_pos[1] + radius * 0.2),
        (shoulder_l_pos[0] - radius * 0.6, shoulder_l_pos[1] + radius * 0.6),
        (elbow_l_pos[0] - radius * 0.1, elbow_l_pos[1] - radius * 0.1)
    ]
    draw_fur_patch(screen, mid_highlight_fur, humerus_l_highlight_points) # Destaque no deltoide/bíceps

    # Antebraço
    forearm_l_points = [
        elbow_l_pos,
        (elbow_l_pos[0] - radius * 0.5, elbow_l_pos[1] + radius * 0.6),
        (wrist_l_pos[0] - radius * 0.4, wrist_l_pos[1] - radius * 0.1),
        (wrist_l_pos[0] + radius * 0.3, wrist_l_pos[1] - radius * 0.3)
    ]
    draw_fur_patch(screen, base_fur, forearm_l_points)

    # Braço Direito
    # Úmero (braço superior)
    humerus_r_points = [
        shoulder_r_pos,
        (shoulder_r_pos[0] + radius * 0.7, shoulder_r_pos[1] + radius * 0.5),
        (elbow_r_pos[0] + radius * 0.3, elbow_r_pos[1] - radius * 0.2),
        (elbow_r_pos[0] - radius * 0.4, elbow_r_pos[1] - radius * 0.4)
    ]
    draw_fur_patch(screen, base_fur, humerus_r_points)
    humerus_r_highlight_points = [
        (shoulder_r_pos[0] + radius * 0.2, shoulder_r_pos[1] + radius * 0.2),
        (shoulder_r_pos[0] + radius * 0.6, shoulder_r_pos[1] + radius * 0.6),
        (elbow_r_pos[0] + radius * 0.1, elbow_r_pos[1] - radius * 0.1)
    ]
    draw_fur_patch(screen, mid_highlight_fur, humerus_r_highlight_points)

    # Antebraço
    forearm_r_points = [
        elbow_r_pos,
        (elbow_r_pos[0] + radius * 0.5, elbow_r_pos[1] + radius * 0.6),
        (wrist_r_pos[0] + radius * 0.4, wrist_r_pos[1] - radius * 0.1),
        (wrist_r_pos[0] - radius * 0.3, wrist_r_pos[1] - radius * 0.3)
    ]
    draw_fur_patch(screen, base_fur, forearm_r_points)

    # Mãos (ajustadas para seguir os novos pulsos)
    hand_l_points = [
        (wrist_l_pos[0] - hand_size*0.4, wrist_l_pos[1] - hand_size*0.3),
        (wrist_l_pos[0] + hand_size*0.3, wrist_l_pos[1] - hand_size*0.3),
        (wrist_l_pos[0] + hand_size*0.3, wrist_l_pos[1] + hand_size*0.3),
        (wrist_l_pos[0] - hand_size*0.4, wrist_l_pos[1] + hand_size*0.3),
    ]
    pygame.draw.polygon(screen, skin_tone_base, hand_l_points)
    pygame.draw.polygon(screen, skin_tone_shadow, [
        (hand_l_points[0][0] + radius*0.05, hand_l_points[0][1] + radius*0.05),
        (hand_l_points[1][0] - radius*0.05, hand_l_points[1][1] + radius*0.05),
        (hand_l_points[2][0] - radius*0.05, hand_l_points[2][1] - radius*0.05),
        (hand_l_points[3][0] + radius*0.05, hand_l_points[3][1] - radius*0.05),
    ])

    hand_r_points = [
        (wrist_r_pos[0] - hand_size*0.4, wrist_r_pos[1] - hand_size*0.3),
        (wrist_r_pos[0] + hand_size*0.3, wrist_r_pos[1] - hand_size*0.3),
        (wrist_r_pos[0] + hand_size*0.3, wrist_r_pos[1] + hand_size*0.3),
        (wrist_r_pos[0] - hand_size*0.4, wrist_r_pos[1] + hand_size*0.3),
    ]
    pygame.draw.polygon(screen, skin_tone_base, hand_r_points)
    pygame.draw.polygon(screen, skin_tone_shadow, [
        (hand_r_points[0][0] + radius*0.05, hand_r_points[0][1] + radius*0.05),
        (hand_r_points[1][0] - radius*0.05, hand_r_points[1][1] + radius*0.05),
        (hand_r_points[2][0] - radius*0.05, hand_r_points[2][1] - radius*0.05),
        (hand_r_points[3][0] + radius*0.05, hand_r_points[3][1] - radius*0.05),
    ])

    # --- PERNAS --- (Mais curtas e grossas, pés grandes)
    leg_top_y = y + radius * 1.2
    leg_length_upper = radius * 1.8
    leg_length_lower = radius * 1.7
    foot_size_l = radius * 1.7
    foot_size_w = radius * 1.0

    # Perna Esquerda
    # Coxa
    draw_fur_patch(screen, base_fur, [(hip_l_pos[0], hip_l_pos[1]), (hip_l_pos[0] - radius*0.8, hip_l_pos[1] + radius*0.6), (knee_l_pos[0] - radius*0.4, knee_l_pos[1] - radius*0.1), (knee_l_pos[0] + radius*0.5, knee_l_pos[1] - radius*0.3)])
    # Panturrilha
    draw_fur_patch(screen, base_fur, [(knee_l_pos[0], knee_l_pos[1]), (knee_l_pos[0] - radius*0.6, knee_l_pos[1] + radius*0.7), (ankle_l_pos[0] - radius*0.3, ankle_l_pos[1] - radius*0.1), (ankle_l_pos[0] + radius*0.4, ankle_l_pos[1] - radius*0.2)])
    # Pé (pele)
    foot_l_points = [
        (ankle_l_pos[0] - foot_size_w*0.6, ankle_l_pos[1] + foot_size_l*0.1),
        (ankle_l_pos[0] + foot_size_w*0.4, ankle_l_pos[1] - foot_size_l*0.1),
        (ankle_l_pos[0] + foot_size_w*0.5, ankle_l_pos[1] + foot_size_l*0.4),
        (ankle_l_pos[0] - foot_size_w*0.7, ankle_l_pos[1] + foot_size_l*0.5) # Calcanhar
    ]
    pygame.draw.polygon(screen, skin_tone_base, foot_l_points)
    pygame.draw.ellipse(screen, skin_tone_shadow, (ankle_l_pos[0] - foot_size_w*0.5, ankle_l_pos[1], foot_size_w, foot_size_l*0.4)) # Sombra no peito do pé

    # Perna Direita
    # Coxa
    draw_fur_patch(screen, base_fur, [(hip_r_pos[0], hip_r_pos[1]), (hip_r_pos[0] + radius*0.8, hip_r_pos[1] + radius*0.6), (knee_r_pos[0] + radius*0.4, knee_r_pos[1] - radius*0.1), (knee_r_pos[0] - radius*0.5, knee_r_pos[1] - radius*0.3)])
    # Panturrilha
    draw_fur_patch(screen, base_fur, [(knee_r_pos[0], knee_r_pos[1]), (knee_r_pos[0] + radius*0.6, knee_r_pos[1] + radius*0.7), (ankle_r_pos[0] + radius*0.3, ankle_r_pos[1] - radius*0.1), (ankle_r_pos[0] - radius*0.4, ankle_r_pos[1] - radius*0.2)])
    # Pé
    foot_r_points = [
        (ankle_r_pos[0] + foot_size_w*0.6, ankle_r_pos[1] + foot_size_l*0.1),
        (ankle_r_pos[0] - foot_size_w*0.4, ankle_r_pos[1] - foot_size_l*0.1),
        (ankle_r_pos[0] - foot_size_w*0.5, ankle_r_pos[1] + foot_size_l*0.4),
        (ankle_r_pos[0] + foot_size_w*0.7, ankle_r_pos[1] + foot_size_l*0.5)
    ]
    pygame.draw.polygon(screen, skin_tone_base, foot_r_points)
    pygame.draw.ellipse(screen, skin_tone_shadow, (ankle_r_pos[0] - foot_size_w*0.5, ankle_r_pos[1], foot_size_w, foot_size_l*0.4))

    # --- ACESSÓRIO --- (Mantido, mas ajustado para o novo braço)
    # Faixa no bíceps direito
    accessory_attach_x = shoulder_r_pos[0] + radius * 0.1
    accessory_attach_y = shoulder_r_pos[1] + radius * 0.6 # Mais abaixo no bíceps
    accessory_width = radius * 0.6
    accessory_height = radius * 0.35

    accessory_points = [
        (accessory_attach_x - accessory_width * 0.3, accessory_attach_y - accessory_height * 0.5),
        (accessory_attach_x + accessory_width * 0.7, accessory_attach_y - accessory_height * 0.4),
        (accessory_attach_x + accessory_width * 0.6, accessory_attach_y + accessory_height * 0.6),
        (accessory_attach_x - accessory_width * 0.4, accessory_attach_y + accessory_height * 0.5),
    ]
    pygame.draw.polygon(screen, accent_color, accessory_points)
    # Contorno mais escuro para dar profundidade à faixa
    darker_accent = (max(0, accent_color[0]-60), max(0, accent_color[1]-60), max(0, accent_color[2]-60))
    pygame.draw.lines(screen, darker_accent, True, accessory_points, int(radius*0.07))

def apply_comic_filter(surface):
    """Aplica efeito de pixel art simples, limitando a paleta de cores"""
    # Converter para PIL
    raw_str = pygame.image.tostring(surface, "RGB")
    pil_img = Image.frombytes("RGB", surface.get_size(), raw_str)
    
    # Posterizar para reduzir o número de cores (estilo pixel art)
    poster = ImageOps.posterize(pil_img, 3)
    
    # Converter de volta para pygame
    result = pygame.image.fromstring(poster.tobytes(), poster.size, poster.mode)
    
    return result

# Estados do jogo
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_PAUSED = 2
GAME_STATE_GAME_OVER = 3
GAME_STATE_HIGH_SCORES = 4
GAME_STATE_NAME_INPUT = 5

# Opções de menu
MENU_NEW_GAME = 0
MENU_CONTINUE = 1
MENU_HIGH_SCORES = 2
MENU_QUIT = 3

# Cores para o menu
MENU_BG_COLOR = (30, 30, 50)  # Azul escuro
MENU_TEXT_COLOR = (220, 220, 220)  # Branco acinzentado
MENU_HIGHLIGHT_COLOR = (255, 255, 0)  # Amarelo
MENU_TITLE_COLOR = (180, 50, 50)  # Vermelho

def draw_menu(screen, font, large_font, selected_option, has_saved_game):
    """Desenha o menu principal do jogo"""
    screen.fill(MENU_BG_COLOR)
    
    # Título do jogo
    title = large_font.render("GORILLAS 2.0", True, MENU_TITLE_COLOR)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
    
    # Opções do menu
    menu_options = [
        "Novo Jogo",
        "Continuar" if has_saved_game else "Continuar (Indisponível)",
        "Recordes",
        "Sair"
    ]
    
    start_y = SCREEN_HEIGHT // 2 - 50
    for i, option in enumerate(menu_options):
        # Opacidade reduzida para opções indisponíveis
        if i == MENU_CONTINUE and not has_saved_game:
            color = (100, 100, 100)  # Cinza (desativado)
        else:
            color = MENU_HIGHLIGHT_COLOR if i == selected_option else MENU_TEXT_COLOR
            
        text = font.render(option, True, color)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, start_y + i * 60))
    
    # Instruções
    instructions = font.render("Use as setas para navegar e ENTER para selecionar", True, MENU_TEXT_COLOR)
    screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 100))
    
    pygame.display.flip()

def draw_high_scores(screen, font, large_font, high_scores):
    """Desenha a tela de recordes"""
    screen.fill(MENU_BG_COLOR)
    
    # Título
    title = large_font.render("RECORDES", True, MENU_TITLE_COLOR)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 50))
    
    if not high_scores:
        text = font.render("Nenhum recorde encontrado", True, MENU_TEXT_COLOR)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
    else:
        # Cabeçalho
        header = font.render("Posição  Nome              Pontuação  Data", True, MENU_HIGHLIGHT_COLOR)
        screen.blit(header, (SCREEN_WIDTH // 2 - 200, 150))
        
        # Lista de recordes
        start_y = 200
        for i, score in enumerate(high_scores[:10]):
            rank_text = font.render(f"{i+1:<8}", True, MENU_TEXT_COLOR)
            name_text = font.render(f"{score['name']:<18}", True, MENU_TEXT_COLOR)
            score_text = font.render(f"{score['score']:<10}", True, MENU_TEXT_COLOR)
            date_text = font.render(score.get('timestamp', 'N/A'), True, MENU_TEXT_COLOR)
            
            screen.blit(rank_text, (SCREEN_WIDTH // 2 - 200, start_y + i * 40))
            screen.blit(name_text, (SCREEN_WIDTH // 2 - 140, start_y + i * 40))
            screen.blit(score_text, (SCREEN_WIDTH // 2 + 60, start_y + i * 40))
            screen.blit(date_text, (SCREEN_WIDTH // 2 + 140, start_y + i * 40))
    
    # Instruções
    instructions = font.render("Pressione ESC para voltar ao menu", True, MENU_TEXT_COLOR)
    screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 50))
    
    pygame.display.flip()

def get_player_names(screen, font, large_font):
    """Tela para inserir nomes dos jogadores"""
    player1_name = ""
    player2_name = ""
    current_player = 0  # 0 para jogador 1, 1 para jogador 2
    
    done = False
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if current_player == 0:
                        if player1_name.strip():  # Garantir que não seja vazio
                            current_player = 1
                    else:
                        if player2_name.strip():  # Garantir que não seja vazio
                            done = True
                            
                elif event.key == pygame.K_BACKSPACE:
                    if current_player == 0:
                        player1_name = player1_name[:-1]
                    else:
                        player2_name = player2_name[:-1]
                        
                elif event.key == pygame.K_ESCAPE:
                    return None, None
                    
                else:
                    # Adicionar caractere (limitar a 15 caracteres)
                    if event.unicode.isprintable():
                        if current_player == 0 and len(player1_name) < 15:
                            player1_name += event.unicode
                        elif current_player == 1 and len(player2_name) < 15:
                            player2_name += event.unicode
        
        # Desenhar tela de entrada de nomes
        screen.fill(MENU_BG_COLOR)
        
        title = large_font.render("Insira os nomes dos jogadores", True, MENU_TITLE_COLOR)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Jogador 1
        p1_label = font.render("Jogador 1 (Vermelho):", True, MONKEY_COLORS[0])
        p1_text = font.render(player1_name + ("_" if current_player == 0 else ""), True, MENU_TEXT_COLOR)
        screen.blit(p1_label, (SCREEN_WIDTH // 2 - 200, 250))
        screen.blit(p1_text, (SCREEN_WIDTH // 2 - 200, 290))
        
        # Jogador 2
        p2_label = font.render("Jogador 2 (Azul):", True, MONKEY_COLORS[1])
        p2_text = font.render(player2_name + ("_" if current_player == 1 else ""), True, MENU_TEXT_COLOR)
        screen.blit(p2_label, (SCREEN_WIDTH // 2 - 200, 350))
        screen.blit(p2_text, (SCREEN_WIDTH // 2 - 200, 390))
        
        # Instruções
        instructions = font.render("Pressione ENTER para confirmar, ESC para voltar", True, MENU_TEXT_COLOR)
        screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, SCREEN_HEIGHT - 50))
        
        pygame.display.flip()
    
    return player1_name, player2_name

# Função para salvar o estado atual do jogo
def save_current_game(buildings, scores, turn, player_pos, player_names):
    """Salva o estado atual do jogo"""
    # Converter objetos Rect para dicionários serializáveis
    serializable_buildings = []
    for b in buildings:
        building_copy = {}
        # Copiar apenas os campos serialiáveis
        for key, value in b.items():
            # Ignorar campos que possam conter objetos Surface ou outros não-serializáveis
            if key not in ['surf', 'image', 'surface']:
                if key == 'rect':
                    # Converter Rect para dicionário
                    rect_dict = {
                        'x': b['rect'].x,
                        'y': b['rect'].y,
                        'width': b['rect'].width,
                        'height': b['rect'].height
                    }
                    building_copy['rect'] = rect_dict
                else:
                    # Verificar se o valor é um tipo básico serializável
                    if isinstance(value, (int, float, str, bool, list, dict, tuple)) or value is None:
                        building_copy[key] = value
        
        # Adicionar cor do prédio (se não estiver presente e for necessário)
        if 'color' not in building_copy:
            building_copy['color'] = BUILDING_COLOR
            
        serializable_buildings.append(building_copy)
    
    game_state = {
        'buildings': serializable_buildings,
        'scores': scores,
        'turn': turn,
        'player_positions': player_pos,
        'player_names': player_names,
        'gravity': GRAVITY
    }
    
    game_storage.save_game_state(game_state)

# Função para carregar o jogo salvo
def load_saved_game():
    """Carrega o jogo salvo"""
    state = game_storage.load_game_state()
    if not state:
        return None
    
    # Converter dicionários de volta para Rect
    for b in state['buildings']:
        rect_dict = b['rect']
        b['rect'] = pygame.Rect(rect_dict['x'], rect_dict['y'], rect_dict['width'], rect_dict['height'])
    
    # Atualizar variável global GRAVITY
    global GRAVITY
    GRAVITY = state.get('gravity', GRAVITY)
    
    return state

def main():
    # Declarar que vamos usar a variável global GRAVITY
    global GRAVITY
    
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Gorillas 2.0")
    clock = pygame.time.Clock()
    
    # Carregar fontes
    font = pygame.font.SysFont(None, 28)
    large_font = pygame.font.SysFont(None, 48)
    
    # Estado atual do jogo (começa no menu)
    game_state = GAME_STATE_MENU
    selected_menu_option = MENU_NEW_GAME
    
    # Verificar se existe jogo salvo
    has_saved_game = game_storage.load_game_state() is not None
    
    # Carregar recordes
    high_scores = game_storage.load_high_scores()
    
    # Variáveis para o jogo
    buildings = None
    player_pos = None
    scores = [0, 0]
    turn = 0
    banana = None
    explosion = None
    angle = 45
    power = 50
    wind = random.randint(-10, 10)
    
    # Nomes dos jogadores
    player_names = ["Jogador 1", "Jogador 2"]
    
    # Saúde dos gorilas
    player_health = [MAX_GORILLA_HEALTH, MAX_GORILLA_HEALTH]
    
    # Criar fundo do jogo uma única vez
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

    def setup_new_game():
        nonlocal buildings, player_pos, scores, turn, angle, power, wind, banana, explosion, player_health
        
        # Gerar novos prédios
        buildings = generate_buildings()
        
        # Posicionar jogadores em prédios mais centrais
        if len(buildings) >= 5:
            p1_building_index = 2  # Terceiro prédio da esquerda
            p2_building_index = -3  # Terceiro prédio da direita
        elif len(buildings) >= 3:
            p1_building_index = 1
            p2_building_index = -2
        else:  # Caso extremo com poucos prédios
            p1_building_index = 0
            p2_building_index = -1

        p1_rect = buildings[p1_building_index]["rect"]
        p2_rect = buildings[p2_building_index]["rect"]

        # Ajustar a altura Y para os gorilas sobre os prédios
        offset_y_para_pes_no_predio = MONKEY_RADIUS * 1.5

        player_pos = [
            (p1_rect.centerx, p1_rect.top - offset_y_para_pes_no_predio),
            (p2_rect.centerx, p2_rect.top - offset_y_para_pes_no_predio),
        ]

        # Resetar valores do jogo
        scores = [0, 0]
        turn = 0
        angle = 45
        power = 50
        wind = random.randint(-10, 10)
        banana = None
        explosion = None
        player_health = [MAX_GORILLA_HEALTH, MAX_GORILLA_HEALTH]  # Inicializar saúde dos gorilas
        
        return buildings, player_pos, scores, turn, angle, power, wind, banana, explosion, player_health

    # Iniciar no menu principal
    if has_saved_game:
        saved_state = load_saved_game()
    else:
        saved_state = None
        
    # Loop principal do jogo
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Verificação de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Salvar o jogo se estiver em andamento
                if game_state == GAME_STATE_PLAYING and buildings and player_pos:
                    save_current_game(buildings, scores, turn, player_pos, player_names)
                running = False
            
            # Processamento de eventos de acordo com o estado do jogo
            if game_state == GAME_STATE_MENU:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected_menu_option = (selected_menu_option - 1) % 4
                    elif event.key == pygame.K_DOWN:
                        selected_menu_option = (selected_menu_option + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if selected_menu_option == MENU_NEW_GAME:
                            game_state = GAME_STATE_NAME_INPUT
                        elif selected_menu_option == MENU_CONTINUE and has_saved_game:
                            # Carregar jogo salvo
                            state = load_saved_game()
                            buildings = state['buildings']
                            scores = state['scores']
                            turn = state['turn']
                            player_pos = state['player_positions']
                            player_names = state.get('player_names', ["Jogador 1", "Jogador 2"])
                            # Inicializar outros valores
                            angle = 45
                            power = 50
                            wind = random.randint(-10, 10)
                            banana = None
                            explosion = None
                            # Mudar para o estado de jogo
                            game_state = GAME_STATE_PLAYING
                        elif selected_menu_option == MENU_HIGH_SCORES:
                            game_state = GAME_STATE_HIGH_SCORES
                        elif selected_menu_option == MENU_QUIT:
                            running = False
            
            elif game_state == GAME_STATE_HIGH_SCORES:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_state = GAME_STATE_MENU
            
            elif game_state == GAME_STATE_NAME_INPUT:
                # Lógica para entrada de nomes é tratada na função get_player_names
                player1_name, player2_name = get_player_names(screen, font, large_font)
                if player1_name is not None and player2_name is not None:
                    player_names = [player1_name, player2_name]
                    # Inicializar novo jogo
                    buildings, player_pos, scores, turn, angle, power, wind, banana, explosion, player_health = setup_new_game()
                    game_state = GAME_STATE_PLAYING
                else:
                    game_state = GAME_STATE_MENU
            
            elif game_state == GAME_STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Salvar o jogo antes de ir para o menu
                        save_current_game(buildings, scores, turn, player_pos, player_names)
                        game_state = GAME_STATE_MENU
                    elif banana is None and explosion is None:
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
                        # Controles para modificar a gravidade
                        elif event.key == pygame.K_g:
                            GRAVITY += 50  # Incremento adequado para o sistema 2D
                        elif event.key == pygame.K_h:
                            GRAVITY = max(50, GRAVITY - 50)  # Impede gravidade muito baixa
                        elif event.key == pygame.K_t:
                            GRAVITY = 300  # Restaura para o valor padrão do jogo
                        elif event.key == pygame.K_SPACE:
                            # Calcula ângulo de lançamento (inverte para o segundo jogador)
                            theta = math.radians(angle if turn == 0 else 180 - angle)
                            
                            # Velocidade inicial baseada na potência selecionada
                            speed = power * VEL_FACTOR
                            
                            # Calcula componentes da velocidade
                            vx = math.cos(theta) * speed
                            vy = -math.sin(theta) * speed  # Negativo porque Y aumenta para baixo
                            
                            # Adiciona deslocamento inicial para evitar colisão imediata
                            start_pos = list(player_pos[turn])
                            offset_x = math.cos(theta) * (MONKEY_RADIUS + BANANA_RADIUS + 5)
                            offset_y = -math.sin(theta) * (MONKEY_RADIUS + BANANA_RADIUS + 5)
                            start_pos[0] += offset_x
                            start_pos[1] += offset_y
                            
                            banana = {
                                "pos": start_pos, 
                                "vel": [vx, vy],
                                "owner": turn,
                                "time_alive": 0
                            }
        
        # Atualização da lógica do jogo baseada no estado atual
        if game_state == GAME_STATE_PLAYING:
            # Lógica da banana
            if banana:
                # Atualizar contador de tempo de vida e física
                banana["time_alive"] += dt
                banana["vel"][0] += wind * WIND_FACTOR * dt
                banana["vel"][1] += GRAVITY * dt
                banana["pos"][0] += banana["vel"][0] * dt
                banana["pos"][1] += banana["vel"][1] * dt

                x, y = banana["pos"]
                # Verificar se a banana saiu da tela
                if x < 0 or x > SCREEN_WIDTH or y > SCREEN_HEIGHT:
                    banana = None
                    turn = 1 - turn
                    wind = random.randint(-10, 10)
                else:
                    # Verificar colisão com os prédios
                    for i, b in enumerate(buildings):
                        if b["rect"].collidepoint(x, y):
                            explosion = {"pos": (x, y), "timer": 0}
                            # Verificar se o prédio vai desabar após o dano
                            building_collapse = damage_building(b, (x, y), EXPLOSION_RADIUS)
                            
                            if building_collapse:
                                # Prédio desabando!
                                # Verificar se algum gorila está no prédio que está desabando
                                for player_idx, pos in enumerate(player_pos):
                                    if b["rect"].collidepoint(pos[0], pos[1]):
                                        # Gorila está no prédio que desabou - sofre dano
                                        player_health[player_idx] -= DAMAGE_BUILDING_COLLAPSE
                                        # Criar explosão secundária na posição do gorila
                                        explosion = {"pos": pos, "timer": 0}
                                
                                # Remover o prédio do jogo
                                buildings[i]["collapsed"] = True
                            
                            banana = None
                            wind = random.randint(-10, 10)
                            turn = 1 - turn
                            break
                            
                    if banana:
                        # Verificar colisão com o gorila adversário
                        target_idx = 1 - banana["owner"]
                        target = player_pos[target_idx]
                        dist = math.hypot(x - target[0], y - target[1])
                        if dist <= BANANA_RADIUS + MONKEY_RADIUS:
                            # Salvar referências importantes antes de limpar a banana
                            banana_owner = banana["owner"]
                            explosion = {"pos": (x, y), "timer": 0}
                            banana = None
                            
                            # Reduzir a energia do gorila atingido
                            player_health[target_idx] -= DAMAGE_PER_HIT
                            
                            # Verificar se o gorila foi derrotado (energia <= 0)
                            if player_health[target_idx] <= 0:
                                # Gorila derrotado! Quem lançou ganha ponto
                                scores[banana_owner] += 1
                                
                                # Salvar recordes
                                players_scores = [
                                    {"name": player_names[0], "score": scores[0]},
                                    {"name": player_names[1], "score": scores[1]}
                                ]
                                game_storage.save_high_scores(players_scores)
                                high_scores = game_storage.load_high_scores()
                                
                                # Exibir mensagem de vitória
                                victory_screen_start = time.time()
                                winner_text = f"{player_names[banana['owner']]} venceu!"
                                defeat_text = f"{player_names[target_idx]} ficou sem energia!"
                                victory_font = pygame.font.SysFont(None, 72)
                                victory_surf = victory_font.render(winner_text, True, MONKEY_COLORS[banana['owner']])
                                defeat_surf = victory_font.render(defeat_text, True, (255, 50, 50))
                                screen.blit(defeat_surf, (SCREEN_WIDTH // 2 - defeat_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
                                screen.blit(victory_surf, (SCREEN_WIDTH // 2 - victory_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
                                pygame.display.flip()
                                pygame.time.delay(3000)  # Mostrar por 3 segundos
                                
                                # Voltar para o menu principal
                                game_state = GAME_STATE_MENU
                            else:
                                # Gorila ainda tem energia, continuar o jogo
                                wind = random.randint(-10, 10)
                                turn = 1 - turn
                        
                        # Verificar colisão com o próprio gorila (autodestruição)
                        # Só permitir após 0.5 segundos
                        if banana["time_alive"] > 0.5:
                            self_idx = banana["owner"]
                            self_pos = player_pos[self_idx]
                            self_dist = math.hypot(x - self_pos[0], y - self_pos[1])
                            if self_dist <= BANANA_RADIUS + MONKEY_RADIUS:
                                # Salvar referências importantes antes de limpar a banana
                                explosion = {"pos": (x, y), "timer": 0}
                                banana = None
                                
                                # Reduzir a energia do gorila que acertou a si mesmo
                                # Fazer o dano por auto-destruição ser maior (dano x 1.5)
                                player_health[self_idx] -= int(DAMAGE_PER_HIT * 1.5)
                                
                                # Verificar se o gorila foi derrotado (energia <= 0)
                                if player_health[self_idx] <= 0:
                                    # Gorila derrotado! Adversário ganha ponto
                                    winner_idx = 1 - self_idx
                                    scores[winner_idx] += 1
                                    
                                    # Salvar recordes
                                    players_scores = [
                                        {"name": player_names[0], "score": scores[0]},
                                        {"name": player_names[1], "score": scores[1]}
                                    ]
                                    game_storage.save_high_scores(players_scores)
                                    high_scores = game_storage.load_high_scores()
                                    
                                    # Exibir mensagem de vitória
                                    victory_screen_start = time.time()
                                    loser_text = f"{player_names[self_idx]} destruiu a si mesmo!"
                                    winner_text = f"{player_names[winner_idx]} venceu!"
                                    victory_font = pygame.font.SysFont(None, 72)
                                    loser_surf = victory_font.render(loser_text, True, (255, 50, 50))
                                    winner_surf = victory_font.render(winner_text, True, MONKEY_COLORS[winner_idx])
                                    screen.blit(loser_surf, (SCREEN_WIDTH // 2 - loser_surf.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
                                    screen.blit(winner_surf, (SCREEN_WIDTH // 2 - winner_surf.get_width() // 2, SCREEN_HEIGHT // 2))
                                    pygame.display.flip()
                                    pygame.time.delay(3000)  # Mostrar por 3 segundos
                                    
                                    # Voltar para o menu principal
                                    game_state = GAME_STATE_MENU
                                else:
                                    # Gorila ainda tem energia, continuar o jogo
                                    wind = random.randint(-10, 10)
                                    turn = 1 - turn

            # Lógica de explosão
            if explosion:
                explosion["timer"] += dt
                if explosion["timer"] > EXPLOSION_DURATION:
                    # Remover apenas a explosão, sem lógica adicional
                    # A partida só termina quando acerta um gorila
                    explosion = None

        # Renderização baseada no estado atual do jogo
        if game_state == GAME_STATE_MENU:
            # Desenhar menu principal
            draw_menu(screen, font, large_font, selected_menu_option, has_saved_game)
            
        elif game_state == GAME_STATE_HIGH_SCORES:
            # Desenhar tela de recordes
            draw_high_scores(screen, font, large_font, high_scores)
            
        elif game_state == GAME_STATE_PLAYING and buildings and player_pos:
            # Desenhar o jogo em andamento
            screen.blit(background, (0, 0))
            draw_buildings(screen, buildings)
            
            # Desenhar gorilas: sprite se disponível, ou versão primitiva
            if gorilla_sprites[0]:
                rect = gorilla_sprites[0].get_rect(center=player_pos[0])
                screen.blit(gorilla_sprites[0], rect)
                # Adicionar barra de energia acima do sprite
                draw_health_bar(screen, player_pos[0], player_health[0], MAX_GORILLA_HEALTH)
            else:
                draw_monkey(screen, player_pos[0], MONKEY_COLORS[0], player_health[0])
                
            if gorilla_sprites[1]:
                rect = gorilla_sprites[1].get_rect(center=player_pos[1])
                screen.blit(gorilla_sprites[1], rect)
                # Adicionar barra de energia acima do sprite
                draw_health_bar(screen, player_pos[1], player_health[1], MAX_GORILLA_HEALTH)
            else:
                draw_monkey(screen, player_pos[1], MONKEY_COLORS[1], player_health[1])

        # Renderizar elementos do jogo apenas quando estivermos jogando
        if game_state == GAME_STATE_PLAYING:
            if banana:
                draw_banana(screen, banana)
                
            if explosion:
                draw_explosion(screen, explosion["pos"], explosion["timer"] / EXPLOSION_DURATION)
                
            # Interface de jogador atual
            turn_text = font.render(f"Turno: {player_names[turn]}", True, MONKEY_COLORS[turn])
            screen.blit(turn_text, (10, 10))
            
            # Informações de jogo
            text_angle = font.render(f"Ângulo: {angle}", True, (255, 255, 255))
            text_power = font.render(f"Força: {power}", True, (255, 255, 255))
            text_wind = font.render(f"Vento: {wind:+d}", True, (255, 255, 255))
            text_gravity = font.render(f"Gravidade: {GRAVITY} (G/H para alterar, T para reset)", True, (255, 255, 255))
            text_score = font.render(f"Placar: {player_names[0]} {scores[0]} - {scores[1]} {player_names[1]}", True, (255, 255, 255))
            
            # Instruções
            instr = font.render("CIMA/BAIXO: Ângulo | ESQ/DIR: Força | R: Vento | ESC: Menu | ESPAÇO: Lançar", True, (255, 255, 255))

            # Exibir textos na tela
            screen.blit(text_angle, (10, 40))
            screen.blit(text_power, (10, 70))
            screen.blit(text_wind, (10, 100))
            screen.blit(text_gravity, (10, 130))
            screen.blit(text_score, (SCREEN_WIDTH - 350, 10))
            screen.blit(instr, (10, SCREEN_HEIGHT - 30))

        screen.blit(apply_comic_filter(screen), (0, 0))
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()