import math
from dataclasses import dataclass
import pygame
from entities import Character, Weapon, create_player, create_enemy


pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = 15
FPS = 60
UI_HEIGHT = SCREEN_HEIGHT - GRID_HEIGHT * TILE_SIZE
ENEMY_TURN_INTERVAL = FPS // 2  # enemy acts every half-second


@dataclass
class MapArea:
    name: str
    player_start: tuple[int, int]
    enemy_start: tuple[int, int]
    bg_color: tuple[int, int, int]
    teleport_spots: dict[str, tuple[int, int]]


AREAS: dict[str, MapArea] = {
    "Superstore": MapArea(
        name="Superstore",
        player_start=(2, 7),
        enemy_start=(16, 7),
        bg_color=(20, 20, 40),
        teleport_spots={"Wasteland": (3, 2), "Laboratory": (17, 12)},
    ),
    "Wasteland": MapArea(
        name="Wasteland",
        player_start=(2, 7),
        enemy_start=(16, 7),
        bg_color=(50, 30, 10),
        teleport_spots={"Superstore": (2, 2), "Laboratory": (17, 12)},
    ),
    "Laboratory": MapArea(
        name="Laboratory",
        player_start=(2, 7),
        enemy_start=(16, 7),
        bg_color=(10, 30, 80),
        teleport_spots={"Superstore": (2, 2), "Wasteland": (17, 12)},
    ),
}


def draw_background(surface: pygame.Surface, area: MapArea) -> None:
    surface.fill(area.bg_color)


def draw_teleport_spots(surface: pygame.Surface, area: MapArea) -> None:
    for dest_name, (tx, ty) in area.teleport_spots.items():
        center = (tx * TILE_SIZE + TILE_SIZE // 2, ty * TILE_SIZE + TILE_SIZE // 2)
        pygame.draw.circle(surface, (255, 215, 0), center, TILE_SIZE // 3)
        font = pygame.font.SysFont(None, 18)
        label = font.render(dest_name[0], True, (0, 0, 0))
        label_rect = label.get_rect(center=center)
        surface.blit(label, label_rect)


def get_teleport_destination(area: MapArea, position: tuple[int, int]) -> str | None:
    for dest_name, spot_pos in area.teleport_spots.items():
        if spot_pos == position:
            return dest_name
    return None


def load_area(name: str, player: Character, enemy: Character) -> MapArea:
    new_area = AREAS[name]
    player.position = new_area.player_start
    enemy.position = new_area.enemy_start
    return new_area


def draw_characters(surface: pygame.Surface, player: Character, enemy: Character) -> None:
    # draw actor placeholders
    px, py = player.position
    ex, ey = enemy.position
    pygame.draw.rect(surface, (0, 200, 0), (px * TILE_SIZE, py * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surface, (200, 0, 0), (ex * TILE_SIZE, ey * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def get_enemy_target(player: Character, enemy: Character) -> tuple[int, int]:
    """Return the tile the enemy is aiming for next (move or attack target)."""
    px, py = player.position
    ex, ey = enemy.position
    # if adjacent, target the player (attack)
    if abs(px - ex) + abs(py - ey) == 1:
        return (px, py)
    # otherwise aim at the next movement step toward the player
    dx = 1 if px > ex else -1 if px < ex else 0
    dy = 1 if py > ey else -1 if py < ey else 0
    if dx != 0:
        nx, ny = (ex + dx, ey)
    else:
        nx, ny = (ex, ey + dy)
    # clamp to grid
    nx = max(0, min(GRID_WIDTH - 1, nx))
    ny = max(0, min(GRID_HEIGHT - 1, ny))
    return (nx, ny)


def draw_arrow(surface: pygame.Surface, start: tuple[int, int], end: tuple[int, int], color: tuple[int, int, int]) -> None:
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


def draw_enemy_aim(surface: pygame.Surface, enemy: Character, target: tuple[int, int]) -> None:
    tx, ty = target
    ex, ey = enemy.position
    start = (ex * TILE_SIZE + TILE_SIZE // 2, ey * TILE_SIZE + TILE_SIZE // 2)
    end = (tx * TILE_SIZE + TILE_SIZE // 2, ty * TILE_SIZE + TILE_SIZE // 2)
    draw_arrow(surface, start, end, (255, 255, 0))


def get_player_attack_target(player: Character, enemy: Character) -> tuple[tuple[int, int], bool] | None:
    px, py = player.position
    ex, ey = enemy.position
    distance = abs(px - ex) + abs(py - ey)
    if player.weapon_melee and distance == 1:
        return ((ex, ey), True)
    if player.weapon_ranged:
        if distance <= player.weapon_ranged.range:
            return ((ex, ey), True)
        # show the maximum reachable tile toward the enemy
        dx = 1 if ex > px else -1 if ex < px else 0
        dy = 1 if ey > py else -1 if ey < py else 0
        steps = player.weapon_ranged.range
        tx, ty = px, py
        while steps > 0 and (tx, ty) != (ex, ey):
            if tx != ex:
                tx += dx
            elif ty != ey:
                ty += dy
            steps -= 1
        return ((tx, ty), False)
    return None


def draw_player_attack_aim(surface: pygame.Surface, player: Character, target_info: tuple[tuple[int, int], bool]) -> None:
    (tx, ty), in_range = target_info
    px, py = player.position
    start = (px * TILE_SIZE + TILE_SIZE // 2, py * TILE_SIZE + TILE_SIZE // 2)
    end = (tx * TILE_SIZE + TILE_SIZE // 2, ty * TILE_SIZE + TILE_SIZE // 2)
    color = (0, 200, 255) if in_range else (0, 120, 200)
    draw_arrow(surface, start, end, color)


def draw_ui(surface: pygame.Surface, player: Character, enemy: Character, area: MapArea, message: str) -> None:
    font = pygame.font.SysFont(None, 24)
    hp_surf = font.render(f"{player.name} HP: {player.hp}/{player.max_hp}", True, (255, 255, 255))
    surface.blit(hp_surf, (10, GRID_HEIGHT * TILE_SIZE + 10))
    enemy_surf = font.render(f"{enemy.name} HP: {enemy.hp}/{enemy.max_hp}", True, (255, 255, 255))
    surface.blit(enemy_surf, (250, GRID_HEIGHT * TILE_SIZE + 10))
    area_surf = font.render(f"Area: {area.name}  [1]Superstore [2]Wasteland [3]Laboratory  [T] teleport pad", True, (255, 255, 255))
    surface.blit(area_surf, (10, GRID_HEIGHT * TILE_SIZE + 40))
    msg_surf = font.render(message, True, (255, 255, 0))
    surface.blit(msg_surf, (10, GRID_HEIGHT * TILE_SIZE + 70))


def draw_name_input(surface: pygame.Surface, name_text: str) -> None:
    surface.fill((0, 0, 0))
    font = pygame.font.SysFont(None, 36)
    prompt = font.render("Enter your name and press Enter:", True, (255, 255, 255))
    name_surf = font.render(name_text or "_", True, (255, 255, 0))
    surface.blit(prompt, (20, SCREEN_HEIGHT // 2 - 40))
    surface.blit(name_surf, (20, SCREEN_HEIGHT // 2 + 10))
    pygame.display.flip()


def get_player_name(screen: pygame.Surface, clock: pygame.time.Clock) -> str | None:
    name_text = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name_text.strip() or "Player"
                if event.key == pygame.K_BACKSPACE:
                    name_text = name_text[:-1]
                elif event.unicode.isprintable():
                    name_text += event.unicode
        draw_name_input(screen, name_text)
        clock.tick(FPS)


def process_player_input(event: pygame.event.Event, player: Character, enemy: Character) -> str:
    # handle player movement and attacks continuously
    if event.type != pygame.KEYDOWN:
        return ""
    x, y = player.position
    message = ""
    if event.key == pygame.K_LEFT:
        nx = max(0, x - 1)
        if (nx, y) != enemy.position:
            player.position = (nx, y)
    elif event.key == pygame.K_RIGHT:
        nx = min(GRID_WIDTH - 1, x + 1)
        if (nx, y) != enemy.position:
            player.position = (nx, y)
    elif event.key == pygame.K_UP:
        ny = max(0, y - 1)
        if (x, ny) != enemy.position:
            player.position = (x, ny)
    elif event.key == pygame.K_DOWN:
        ny = min(GRID_HEIGHT - 1, y + 1)
        if (x, ny) != enemy.position:
            player.position = (x, ny)
    elif event.key == pygame.K_SPACE:
        px, py = player.position
        ex, ey = enemy.position
        distance = abs(px - ex) + abs(py - ey)
        if distance == 1 and player.weapon_melee:
            enemy.hp -= player.weapon_melee.damage
            message = f"You slash {enemy.name}!"
        elif player.weapon_ranged and 0 < distance <= player.weapon_ranged.range:
            enemy.hp -= player.weapon_ranged.damage
            message = f"You shoot {enemy.name}!"
        else:
            message = "Enemy is too far!"
    return message


def enemy_turn(player: Character, enemy: Character) -> str:
    # simple continuous AI
    px, py = player.position
    ex, ey = enemy.position
    message = ""
    if abs(px - ex) + abs(py - ey) == 1:
        player.hp -= enemy.weapon.damage if enemy.weapon else 0
        message = f"{enemy.name} hits you!"
    else:
        dx = 1 if px > ex else -1 if px < ex else 0
        dy = 1 if py > ey else -1 if py < ey else 0
        if dx != 0:
            new_pos = (ex + dx, ey)
        else:
            new_pos = (ex, ey + dy)
        nx, ny = new_pos
        nx = max(0, min(GRID_WIDTH - 1, nx))
        ny = max(0, min(GRID_HEIGHT - 1, ny))
        if (nx, ny) != player.position:
            enemy.position = (nx, ny)
    return message


def main() -> None:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Nuclear Winter")
    clock = pygame.time.Clock()

    player_name = get_player_name(screen, clock)
    if player_name is None:
        pygame.quit()
        return

    current_area = AREAS["Superstore"]
    player = create_player(player_name)
    enemy = create_enemy()
    current_area = load_area(current_area.name, player, enemy)
    message = ""
    game_over = False
    enemy_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not game_over and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    target_area = {pygame.K_1: "Superstore", pygame.K_2: "Wasteland", pygame.K_3: "Laboratory"}[event.key]
                    if current_area.name != target_area:
                        current_area = load_area(target_area, player, enemy)
                        message = f"Teleported to {target_area}."
                    else:
                        message = f"Already in {target_area}."
                elif event.key == pygame.K_t:
                    teleport_target = get_teleport_destination(current_area, player.position)
                    if teleport_target:
                        current_area = load_area(teleport_target, player, enemy)
                        message = f"Teleported to {teleport_target}."
                    else:
                        message = "No teleporter here."
                else:
                    msg = process_player_input(event, player, enemy)
                    if msg:
                        message = msg

        if not game_over:
            if enemy.hp <= 0:
                game_over = True
                message = f"{player.name} wins!"
            elif player.hp <= 0:
                game_over = True
                message = f"{enemy.name} wins!"

        if not game_over:
            # throttle enemy actions so it doesn't rush the player instantly
            enemy_timer += 1
            if enemy_timer >= ENEMY_TURN_INTERVAL:
                emsg = enemy_turn(player, enemy)
                enemy_timer = 0
                if emsg:
                    message = emsg

        if not game_over:
            if player.hp <= 0:
                game_over = True
                message = f"{enemy.name} wins!"
            elif enemy.hp <= 0:
                game_over = True
                message = f"{player.name} wins!"

        draw_background(screen, current_area)
        draw_teleport_spots(screen, current_area)
        player_target = get_player_attack_target(player, enemy)
        if player_target is not None:
            draw_player_attack_aim(screen, player, player_target)
        enemy_target = get_enemy_target(player, enemy)
        draw_enemy_aim(screen, enemy, enemy_target)
        draw_characters(screen, player, enemy)
        draw_ui(screen, player, enemy, current_area, message)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

