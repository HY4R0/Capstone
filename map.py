import math
import pygame
from collections import deque

from entities import create_enemy_for_area

# =====================
# Game constants
# =====================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = 15
FPS = 60
ENEMY_TURN_INTERVAL = FPS // 2


# =====================
# Map data
# 0 = floor, 1 = wall
# =====================
GAME_MAP = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

for y in range(2, 6):
    GAME_MAP[y][4] = 1
    GAME_MAP[y + 7][4] = 1
    GAME_MAP[y + 4][9] = 1
    GAME_MAP[y][14] = 1
    GAME_MAP[y + 7][14] = 1
    GAME_MAP[y + 4][19] = 1


class MapArea:
    def __init__(self, name, player_start, enemy_start, bg_color, next_area, teleport_pos):
        # purposefully using explicit attribute names
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


# =====================
# Drawing helpers
# =====================

def draw_background(surface, area):
    surface.fill(area.bg_color)


def draw_walls(surface, game_map):
    # draw every wall tile
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if game_map[y][x] == 1:
                pygame.draw.rect(
                    surface,
                    (60, 65, 75),
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                )
                pygame.draw.rect(
                    surface,
                    (35, 40, 45),
                    (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                    2,
                )


def draw_teleport_spots(surface, area, unlocked):
    # if not unlocked, don't draw it
    if not unlocked:
        return
    if area.next_area is None:
        return

    # teleport_pos is grid coordinate (tile coordinate)
    tile_x = area.teleport_pos[0]
    tile_y = area.teleport_pos[1]

    center_x = tile_x * TILE_SIZE + TILE_SIZE // 2
    center_y = tile_y * TILE_SIZE + TILE_SIZE // 2

    pygame.draw.circle(surface, (255, 215, 0), (center_x, center_y), TILE_SIZE // 3)

    # tiny label
    font = pygame.font.SysFont(None, 18)
    label = font.render("N", True, (0, 0, 0))
    label_rect = label.get_rect(center=(center_x, center_y))
    surface.blit(label, label_rect)


def get_teleport_destination(area, position, unlocked):
    # only works if you are at the teleport spot AND it is unlocked
    if position == area.teleport_pos and unlocked and area.next_area is not None:
        return area.next_area
    return None


def load_area(name, player, completed_areas):
    # completed_areas isn't used right now, but leaving it here keeps compatibility
    new_area = AREAS[name]

    # set the player to the starting position for that area
    player.position = new_area.player_start

    # spawn enemy for that area
    enemy = create_enemy_for_area(name)

    return new_area, enemy


# =====================
# Line-of-sight / path helpers
# =====================

def has_line_of_sight(start, end, game_map):
    """Simple grid line-of-sight checker.

    This is NOT super advanced. It just samples points along the line.
    """
    start_x = start[0]
    start_y = start[1]
    end_x = end[0]
    end_y = end[1]

    diff_x = end_x - start_x
    diff_y = end_y - start_y

    steps = max(abs(diff_x), abs(diff_y))
    if steps == 0:
        return True

    # walk from start to end, checking every sample
    for i in range(1, steps):
        t = i / steps

        check_x = int(round(start_x + diff_x * t))
        check_y = int(round(start_y + diff_y * t))

        if game_map[check_y][check_x] == 1:
            return False

    return True


def get_next_path_step(start, target, game_map):
    """Find one step of the shortest path using BFS.

    Returns the NEXT tile you should step into (not the full path).
    """
    if start == target:
        return start

    queue = deque([[start]])
    visited = {start}

    while queue:
        current_path = queue.popleft()
        last_pos = current_path[-1]
        last_x = last_pos[0]
        last_y = last_pos[1]

        if (last_x, last_y) == target:
            if len(current_path) > 1:
                return current_path[1]
            return start

        for change_x, change_y in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx = last_x + change_x
            ny = last_y + change_y

            if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                if game_map[ny][nx] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    new_path = list(current_path)
                    new_path.append((nx, ny))
                    queue.append(new_path)

    return start


def get_player_attack_target(player, enemy, game_map):
    player_x = player.position[0]
    player_y = player.position[1]

    enemy_x = enemy.position[0]
    enemy_y = enemy.position[1]

    distance = abs(player_x - enemy_x) + abs(player_y - enemy_y)

    # melee attack: only if adjacent
    if player.weapon_melee and distance == 1:
        return ((enemy_x, enemy_y), True)

    # ranged attack
    if player.weapon_ranged:
        # First, check exact conditions for a valid shoot
        if distance <= player.weapon_ranged.range:
            if has_line_of_sight(player.position, enemy.position, game_map):
                return ((enemy_x, enemy_y), True)

        # If not valid, show where the shot would kinda go.

        # figure out x direction step
        if enemy_x > player_x:
            x_step = 1
        elif enemy_x < player_x:
            x_step = -1
        else:
            x_step = 0

        # figure out y direction step
        if enemy_y > player_y:
            y_step = 1
        elif enemy_y < player_y:
            y_step = -1
        else:
            y_step = 0

        remaining_steps = player.weapon_ranged.range

        march_x = player_x
        march_y = player_y

        while remaining_steps > 0 and (march_x, march_y) != (enemy_x, enemy_y):
            next_x = march_x
            next_y = march_y

            if march_x != enemy_x:
                next_x = march_x + x_step
                next_y = march_y
            else:
                if march_y != enemy_y:
                    next_y = march_y + y_step
                    next_x = march_x

            if game_map[next_y][next_x] == 1:
                break

            march_x = next_x
            march_y = next_y

            remaining_steps -= 1

        return ((march_x, march_y), False)

    return None


# =====================
# Attack aim rendering helpers
# =====================

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


def draw_player_attack_aim(surface, player, target_info):
    target_x = target_info[0][0]
    target_y = target_info[0][1]
    in_range = target_info[1]

    start_x = player.position[0]
    start_y = player.position[1]

    start_pixel = (start_x * TILE_SIZE + TILE_SIZE // 2, start_y * TILE_SIZE + TILE_SIZE // 2)
    end_pixel = (target_x * TILE_SIZE + TILE_SIZE // 2, target_y * TILE_SIZE + TILE_SIZE // 2)

    if in_range:
        col = (0, 200, 255)
    else:
        col = (0, 120, 200)

    draw_arrow(surface, start_pixel, end_pixel, col)

