import math
import pygame
from collections import deque
from entities import Character, Weapon, create_player, create_enemy_for_area


pygame.init()


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = 15
FPS = 60


# --- WALL AND MAP CONFIGURATION ---
# 0 = Empty Floor, 1 = Solid Wall
GAME_MAP = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

# Creating physical tactical barrier pillars down columns 8 and 13
# Leaving row 6, 7, 8 open down the middle so units can walk through the center gaps
for y in range(2, 6):
    GAME_MAP[y][8] = 1
    GAME_MAP[y + 9][8] = 1
    GAME_MAP[y][13] = 1
    GAME_MAP[y + 9][13] = 1


class MapArea:
    def __init__(self, name, player_start, enemy_start, bg_color, next_area, teleport_pos):
        self.name = name
        self.player_start = player_start
        self.enemy_start = enemy_start
        self.bg_color = bg_color
        self.next_area = next_area
        self.teleport_pos = teleport_pos


AREAS = {
    "Ruins": MapArea("Ruins", (2, 7), (16, 7), (20, 20, 40), "Outpost", (17, 12)),
    "Outpost": MapArea("Outpost", (2, 7), (16, 7), (50, 30, 10), "Lab", (17, 12)),
    "Lab": MapArea("Lab", (2, 7), (16, 7), (30, 50, 30), "Shore", (17, 12)),
    "Shore": MapArea("Shore", (2, 7), (16, 7), (10, 30, 80), "Vault", (17, 12)),
    "Vault": MapArea("Vault", (2, 7), (16, 7), (60, 50, 30), "Wasteland", (17, 12)),
    "Wasteland": MapArea("Wasteland", (2, 7), (16, 7), (40, 35, 10), "Bunker", (17, 12)),
    "Bunker": MapArea("Bunker", (2, 7), (16, 7), (30, 30, 30), "Tower", (17, 12)),
    "Tower": MapArea("Tower", (2, 7), (16, 7), (50, 50, 50), "Underground", (17, 12)),
    "Underground": MapArea("Underground", (2, 7), (16, 7), (10, 10, 20), "Summit", (17, 12)),
    "Summit": MapArea("Summit", (2, 7), (16, 7), (80, 70, 60), None, (17, 12)),
}


def draw_background(surface, area):
    surface.fill(area.bg_color)


def draw_walls(surface, game_map):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if game_map[y][x] == 1:
                # Dark slate steel look
                pygame.draw.rect(surface, (60, 65, 75), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
                # Inner border detail
                pygame.draw.rect(surface, (35, 40, 45), (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)


def draw_teleport_spots(surface, area, unlocked):
    if not unlocked or area.next_area is None:
        return
    tx = area.teleport_pos[0]
    ty = area.teleport_pos[1]
    center_x = tx * TILE_SIZE + TILE_SIZE // 2
    center_y = ty * TILE_SIZE + TILE_SIZE // 2
    pygame.draw.circle(surface, (255, 215, 0), (center_x, center_y), TILE_SIZE // 3)
    font = pygame.font.SysFont(None, 18)
    label = font.render("N", True, (0, 0, 0))
    label_rect = label.get_rect(center=(center_x, center_y))
    surface.blit(label, label_rect)


def get_available_teleports(area, unlocked):
    if unlocked and area.next_area is not None:
        return area.next_area
    return None


def get_teleport_destination(area, position, unlocked):
    if position == area.teleport_pos and unlocked and area.next_area is not None:
        return area.next_area
    return None


def load_area(name, player, completed_areas):
    new_area = AREAS[name]
    player.position = new_area.player_start
    enemy = create_enemy_for_area(name)
    return new_area, enemy


def draw_characters(surface, player, enemy):
    px = player.position[0]
    py = player.position[1]
    ex = enemy.position[0]
    ey = enemy.position[1]
    pygame.draw.rect(surface, (0, 200, 0), (px * TILE_SIZE, py * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surface, (200, 0, 0), (ex * TILE_SIZE, ey * TILE_SIZE, TILE_SIZE, TILE_SIZE))


# --- LINE OF SIGHT (RAYCAST) UTILITY ---
def has_line_of_sight(start, end, game_map):
    """Calculates if there is an unblocked line between two grid positions."""
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    steps = max(abs(dx), abs(dy))
    if steps == 0:
        return True
    for i in range(1, steps):
        t = i / steps
        cx = int(round(x1 + dx * t))
        cy = int(round(y1 + dy * t))
        if game_map[cy][cx] == 1:
            return False
    return True


# --- BFS PATHFINDING UTILITY ---
def get_next_path_step(start, target, game_map):
    """Finds the absolute shortest path step around walls using Breadth-First Search."""
    if start == target:
        return start
    queue = deque([[start]])
    visited = {start}
    
    while queue:
        path = queue.popleft()
        x, y = path[-1]
        
        if (x, y) == target:
            return path[1] if len(path) > 1 else start
            
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if game_map[ny][nx] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    new_path = list(path)
                    new_path.append((nx, ny))
                    queue.append(new_path)
    return start


def get_enemy_target(player, enemy, game_map):
    px, py = player.position
    ex, ey = enemy.position
    distance = abs(px - ex) + abs(py - ey)
    
    if getattr(enemy, 'telegraph', False) or distance == 1:
        return (px, py)
        
    return get_next_path_step(enemy.position, player.position, game_map)


def draw_arrow(surface, start, end, color):
    pygame.draw.line(surface, color, start, end, 2)
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    ux = dx / dist
    uy = dy / dist
    arrow_len = max(8, TILE_SIZE // 2)
    half_w = max(4, TILE_SIZE // 4)
    base_x = end[0] - ux * arrow_len
    base_y = end[1] - uy * arrow_len
    px = -uy
    py = ux
    left = (base_x + px * half_w, base_y + py * half_w)
    right = (base_x - px * half_w, base_y - py * half_w)
    tip = end
    pygame.draw.polygon(surface, color, [tip, left, right])


def draw_enemy_aim(surface, enemy, target):
    tx, ty = target
    ex, ey = enemy.position
    start = (ex * TILE_SIZE + TILE_SIZE // 2, ey * TILE_SIZE + TILE_SIZE // 2)
    end = (tx * TILE_SIZE + TILE_SIZE // 2, ty * TILE_SIZE + TILE_SIZE // 2)
    if hasattr(enemy, 'telegraph') and enemy.telegraph:
        draw_arrow(surface, start, end, (255, 50, 50))
        pygame.draw.circle(surface, (255, 100, 100), end, TILE_SIZE // 4, 2)
    else:
        draw_arrow(surface, start, end, (255, 255, 0))


def get_player_attack_target(player, enemy, game_map):
    px, py = player.position
    ex, ey = enemy.position
    distance = abs(px - ex) + abs(py - ey)
    
    if player.weapon_melee and distance == 1:
        return ((ex, ey), True)
    
    if player.weapon_ranged:
        if distance <= player.weapon_ranged.range and has_line_of_sight(player.position, enemy.position, game_map):
            return ((ex, ey), True)
        
        # Draw shot projection until wall or max range
        if ex > px: dx = 1
        elif ex < px: dx = -1
        else: dx = 0
        
        if ey > py: dy = 1
        elif ey < py: dy = -1
        else: dy = 0
        
        steps = player.weapon_ranged.range
        tx, ty = px, py
        while steps > 0 and (tx, ty) != (ex, ey):
            nx, ny = tx, ty
            if tx != ex: nx = tx + dx
            elif ty != ey: ny = ty + dy
            
            if game_map[ny][nx] == 1:
                break
            tx, ty = nx, ny
            steps -= 1
        return ((tx, ty), (tx, ty) == (ex, ey) and distance <= player.weapon_ranged.range)
    return None


def draw_player_attack_aim(surface, player, target_info):
    tx = target_info[0][0]
    ty = target_info[0][1]
    in_range = target_info[1]
    
    px, py = player.position
    start = (px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2)
    end = (tx * TILE_SIZE + TILE_SIZE // 2, ty * TILE_SIZE + TILE_SIZE // 2)
    color = (0, 200, 255) if in_range else (0, 120, 200)
    draw_arrow(surface, start, end, color)


def draw_ui(surface, player, enemy, area, message, teleport_unlocked):
    font = pygame.font.SysFont(None, 24)
    player_hp_text = str(player.name) + " HP: " + str(player.hp) + "/" + str(player.max_hp)
    hp_surf = font.render(player_hp_text, True, (255, 255, 255))
    surface.blit(hp_surf, (10, GRID_HEIGHT * TILE_SIZE + 10))
    
    enemy_hp_text = str(enemy.name) + " HP: " + str(enemy.hp) + "/" + str(enemy.max_hp)
    enemy_surf = font.render(enemy_hp_text, True, (255, 255, 255))
    surface.blit(enemy_surf, (250, GRID_HEIGHT * TILE_SIZE + 10))
    
    teleport_status = "UNLOCKED" if teleport_unlocked else "LOCKED"
    area_text = "Area: " + area.name + "  Teleport: " + teleport_status + "  [T] pad"
    area_surf = font.render(area_text, True, (255, 255, 255))
    surface.blit(area_surf, (10, GRID_HEIGHT * TILE_SIZE + 40))
    
    msg_surf = font.render(message, True, (255, 255, 0))
    surface.blit(msg_surf, (10, GRID_HEIGHT * TILE_SIZE + 70))


def upgrade_weapon(player, choice):
    if choice == 1 and player.weapon_melee:
        player.weapon_melee.damage = player.weapon_melee.damage + 2
    elif choice == 2 and player.weapon_ranged:
        player.weapon_ranged.damage = player.weapon_ranged.damage + 2
        player.weapon_ranged.range = player.weapon_ranged.range + 1
    elif choice == 3:
        player.hp = min(player.max_hp, player.hp + 10)
    elif choice == 4:
        player.max_hp = player.max_hp + 5
        player.hp = player.hp + 5


def draw_upgrade_screen(surface, player):
    surface.fill((20, 20, 20))
    font_title = pygame.font.SysFont(None, 48)
    font_text = pygame.font.SysFont(None, 32)
    
    title = font_title.render("ENEMY DEFEATED!", True, (0, 255, 0))
    upgrade_prompt = font_text.render("Choose an upgrade:", True, (255, 255, 255))
    
    melee_damage = player.weapon_melee.damage + 2
    ranged_damage = player.weapon_ranged.damage + 2
    ranged_range = player.weapon_ranged.range + 1
    
    melee_text = "[1] Melee: " + player.weapon_melee.name + " (+2 damage) - " + str(melee_damage)
    ranged_text = "[2] Ranged: " + player.weapon_ranged.name + " (+1 damage, +1 range) - " + str(ranged_damage) + ", " + str(ranged_range)
    health_name = player.health.name if hasattr(player, 'health') else "Medkit"
    heal_text = "[3] Heal: " + health_name + " +10 HP (Current: " + str(player.hp) + "/" + str(player.max_hp) + ")"
    maxhp_text = "[4] Vitality: +5 max HP and +5 current HP (New max: " + str(player.max_hp + 5) + ")"
    
    melee_surf = font_text.render(melee_text, True, (100, 200, 255))
    ranged_surf = font_text.render(ranged_text, True, (100, 200, 255))
    heal_surf = font_text.render(heal_text, True, (100, 200, 255))
    maxhp_surf = font_text.render(maxhp_text, True, (100, 200, 255))
    
    title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
    surface.blit(title, (title_x, 100))
    surface.blit(upgrade_prompt, (50, 200))
    surface.blit(melee_surf, (50, 280))
    surface.blit(ranged_surf, (50, 340))
    surface.blit(heal_surf, (50, 400))
    surface.blit(maxhp_surf, (50, 460))
    pygame.display.flip()


def draw_victory_screen(surface, player):
    surface.fill((20, 40, 20))
    font_title = pygame.font.SysFont(None, 64)
    font_text = pygame.font.SysFont(None, 32)
    
    title = font_title.render("VICTORY!", True, (0, 255, 0))
    message = font_text.render(player.name + " has conquered all 10 areas!", True, (255, 255, 255))
    hp_text = font_text.render("Final HP: " + str(player.hp) + "/" + str(player.max_hp), True, (255, 255, 100))
    melee_text = font_text.render("Melee Damage: " + str(player.weapon_melee.damage), True, (100, 200, 255))
    ranged_text = font_text.render("Ranged Damage: " + str(player.weapon_ranged.damage) + ", Range: " + str(player.weapon_ranged.range), True, (100, 200, 255))
    exit_text = font_text.render("Press any key to exit...", True, (200, 200, 200))
    
    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
    surface.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 180))
    surface.blit(hp_text, (50, 280))
    surface.blit(melee_text, (50, 340))
    surface.blit(ranged_text, (50, 400))
    surface.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 500))
    pygame.display.flip()


def draw_name_input(surface, name_text):
    surface.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 36)
    prompt = font.render("Enter your name and press Enter:", True, (255, 255, 255))
    name_surf = font.render("_" if name_text == "" else name_text, True, (255, 255, 0))
    surface.blit(prompt, (20, SCREEN_HEIGHT // 2 - 40))
    surface.blit(name_surf, (20, SCREEN_HEIGHT // 2 + 10))
    pygame.display.flip()


def get_player_name(screen, clock):
    name_text = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "Player" if name_text.strip() == "" else name_text.strip()
                if event.key == pygame.K_BACKSPACE:
                    name_text = name_text[:-1]
                elif event.unicode.isprintable():
                    name_text = name_text + event.unicode
        draw_name_input(screen, name_text)
        clock.tick(FPS)


def process_player_input(event, player, enemy, game_map):
    if event.type != pygame.KEYDOWN:
        return False
    
    x, y = player.position
    nx, ny = x, y
    moved = False
    
    if event.key == pygame.K_LEFT:
        nx = max(0, x - 1)
        moved = True
    elif event.key == pygame.K_RIGHT:
        nx = min(GRID_WIDTH - 1, x + 1)
        moved = True
    elif event.key == pygame.K_UP:
        ny = max(0, y - 1)
        moved = True
    elif event.key == pygame.K_DOWN:
        ny = min(GRID_HEIGHT - 1, y + 1)
        moved = True
        
    if moved:
        # Prevent stepping into an enemy or a wall layout block
        if (nx, ny) != enemy.position and game_map[ny][nx] != 1:
            player.position = (nx, ny)
            return True
    return False


def enemy_turn(player, enemy, game_map):
    px, py = player.position
    ex, ey = enemy.position
    message = ""
    
    def process_status_effects(entity):
        msgs = []
        new_effects = []
        for eff in getattr(entity, 'status_effects', []):
            etype = eff.get('type')
            dmg = eff.get('dmg', 0)
            duration = eff.get('duration', 0)
            if dmg > 0 and duration > 0:
                entity.hp = max(0, entity.hp - dmg)
                msgs.append(f"{entity.name} suffers {dmg} {etype} damage.")
            eff['duration'] = duration - 1
            if eff['duration'] > 0:
                new_effects.append(eff)
        entity.status_effects = new_effects
        return msgs

    s_msgs = process_status_effects(player) + process_status_effects(enemy)
    if s_msgs:
        message = " ".join(s_msgs)

    distance = abs(px - ex) + abs(py - ey)
    behavior = getattr(enemy, 'behavior', 'melee')

    if behavior == 'sniper':
        if getattr(enemy, 'special_cooldown', 0) > 0:
            enemy.special_cooldown -= 1

        if getattr(enemy, 'telegraph', False):
            # Check if sniper still has line of sight when firing
            if has_line_of_sight(enemy.position, player.position, game_map):
                damage = enemy.weapon.damage * 1.5 if enemy.weapon else 0
                player.hp = max(0, player.hp - damage)
                message = str(enemy.name) + " fires a precise shot!"
            else:
                message = str(enemy.name) + "'s shot was blocked by a wall!"
            enemy.telegraph = False
            enemy.special_cooldown = 3
            return message

        if getattr(enemy, 'special_cooldown', 0) <= 0 and distance >= 3 and has_line_of_sight(enemy.position, player.position, game_map):
            enemy.telegraph = True
            message = str(enemy.name) + " takes aim..."
            return message

    if distance == 1:
        damage = enemy.weapon.damage if enemy.weapon else 0
        player.hp = max(0, player.hp - damage)
        message = str(enemy.name) + " hits you!"
        if getattr(enemy, 'behavior', '') == 'melee' and 'Raddle' in enemy.name:
            player.status_effects.append({'type': 'poison', 'duration': 3, 'dmg': 2})
            message += " You are poisoned!"
        if getattr(enemy, 'behavior', '') == 'boss' or 'Skeleton' in enemy.name:
            player.status_effects.append({'type': 'burn', 'duration': 3, 'dmg': 3})
            message += " You are burning!"
    else:
        # Utilize BFS pathfinding step around walls instead of straight-line math
        next_step = get_next_path_step(enemy.position, player.position, game_map)
        if next_step != player.position:
            enemy.position = next_step
    
    return message


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Nuclear Winter")
    clock = pygame.time.Clock()

    player_name = get_player_name(screen, clock)
    if player_name is None:
        pygame.quit()
        return

    player = create_player(player_name)
    current_area, enemy = load_area("Ruins", player, set())
    message = ""
    game_over = False
    upgrade_screen = False
    victory = False
    next_area_unlocked = False
    areas_completed = 0

    running = True
    while running:
        if victory:
            draw_victory_screen(screen, player)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    running = False
            clock.tick(FPS)
            continue
        
        if upgrade_screen:
            draw_upgrade_screen(screen, player)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        choice = int(event.unicode) if event.unicode.isdigit() else 1
                        upgrade_weapon(player, choice)
                        next_area_unlocked = True
                        upgrade_screen = False
                        message = "Upgrade applied! Teleport ready."
            clock.tick(FPS)
            continue
        
        player_acted = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    teleport_target = get_teleport_destination(current_area, player.position, next_area_unlocked)
                    if teleport_target:
                        current_area, enemy = load_area(teleport_target, player, set())
                        message = "Teleported to " + teleport_target + "."
                        game_over = False
                        next_area_unlocked = False
                        areas_completed += 1
                    elif game_over:
                        message = "Defeat the enemy and choose an upgrade!"
                    else:
                        message = "No active teleporter here."
                elif not game_over and event.key == pygame.K_SPACE:
                    px, py = player.position
                    ex, ey = enemy.position
                    distance = abs(px - ex) + abs(py - ey)
                    if distance == 1 and player.weapon_melee:
                        enemy.hp = max(0, enemy.hp - player.weapon_melee.damage)
                        message = "You slash " + enemy.name + "!"
                        player_acted = True
                    elif player.weapon_ranged and distance > 0 and distance <= player.weapon_ranged.range:
                        if has_line_of_sight(player.position, enemy.position, GAME_MAP):
                            enemy.hp = max(0, enemy.hp - player.weapon_ranged.damage)
                            message = "You shoot " + enemy.name + "!"
                        else:
                            message = "Shot blocked by a wall obstacle!"
                        player_acted = True
                    else:
                        message = "Enemy out of range!"
                elif not game_over:
                    if process_player_input(event, player, enemy, GAME_MAP):
                        player_acted = True

        # Sequential clean execution logic of the strict Turn-Based system
        if player_acted and not game_over:
            if enemy.hp <= 0:
                game_over = True
                message = player.name + " defeated " + enemy.name + "!"
                if current_area.next_area is None:
                    victory = True
                else:
                    upgrade_screen = True
            else:
                emsg = enemy_turn(player, enemy, GAME_MAP)
                if emsg:
                    message = emsg
                
                if enemy.hp <= 0:
                    game_over = True
                    message = player.name + " defeated " + enemy.name + "!"
                    if current_area.next_area is None:
                        victory = True
                    else:
                        upgrade_screen = True
                elif player.hp <= 0:
                    game_over = True
                    message = enemy.name + " wins!"

        # Render Layer Updates
        draw_background(screen, current_area)
        draw_walls(screen, GAME_MAP)  # Renders the solid walls layout
        draw_teleport_spots(screen, current_area, next_area_unlocked)
        
        player_target = get_player_attack_target(player, enemy, GAME_MAP)
        if player_target is not None:
            draw_player_attack_aim(screen, player, player_target)
            
        enemy_target = get_enemy_target(player, enemy, GAME_MAP)
        draw_enemy_aim(screen, enemy, enemy_target)
        
        draw_characters(screen, player, enemy)
        draw_ui(screen, player, enemy, current_area, message, next_area_unlocked)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()