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


def draw_characters(surface: pygame.Surface, player: Character, enemy: Character) -> None:
    # draw actor placeholders
    px, py = player.position
    ex, ey = enemy.position
    pygame.draw.rect(surface, (0, 200, 0), (px * TILE_SIZE, py * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surface, (200, 0, 0), (ex * TILE_SIZE, ey * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def draw_ui(surface: pygame.Surface, player: Character, enemy: Character, message: str) -> None:
    font = pygame.font.SysFont(None, 24)
    hp_surf = font.render(f"{player.name} HP: {player.hp}/{player.max_hp}", True, (255, 255, 255))
    surface.blit(hp_surf, (10, GRID_HEIGHT * TILE_SIZE + 10))
    enemy_surf = font.render(f"{enemy.name} HP: {enemy.hp}/{enemy.max_hp}", True, (255, 255, 255))
    surface.blit(enemy_surf, (250, GRID_HEIGHT * TILE_SIZE + 10))
    msg_surf = font.render(message, True, (255, 255, 0))
    surface.blit(msg_surf, (10, GRID_HEIGHT * TILE_SIZE + 40))


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
        if abs(px - ex) + abs(py - ey) == 1:
            enemy.hp -= player.weapon_ranged.damage if player.weapon_ranged else 0
            message = f"You hit {enemy.name}!"
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

    player = create_player(player_name)
    enemy = create_enemy()
    message = ""
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif not game_over:
                msg = process_player_input(event, player, enemy)
                if msg:
                    message = msg

        if not game_over:
            emsg = enemy_turn(player, enemy)
            if emsg:
                message = emsg

        if not game_over:
            if player.hp <= 0:
                game_over = True
                message = f"{enemy.name} wins!"
            elif enemy.hp <= 0:
                game_over = True
                message = f"{player.name} wins!"

        screen.fill((0, 0, 0))
        draw_characters(screen, player, enemy)
        draw_ui(screen, player, enemy, message)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

