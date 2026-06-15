import pygame

from map import GRID_HEIGHT, GRID_WIDTH


def get_player_name(screen, clock, fps):
    name_text = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name_text.strip() == "":
                        return "Player"
                    return name_text.strip()

                if event.key == pygame.K_BACKSPACE:
                    name_text = name_text[:-1]
                else:
                    if event.unicode.isprintable():
                        name_text = name_text + event.unicode

        draw_name_input(screen, name_text)
        clock.tick(fps)


def draw_name_input(surface, name_text):
    surface.fill((0, 0, 0))

    font = pygame.font.SysFont(None, 36)

    prompt = font.render("Enter your name and press Enter:", True, (255, 255, 255))
    if name_text == "":
        shown = "_"
    else:
        shown = name_text

    name_surf = font.render(shown, True, (255, 255, 0))

    surface.blit(prompt, (20, surface.get_height() // 2 - 40))
    surface.blit(name_surf, (20, surface.get_height() // 2 + 10))

    pygame.display.flip()


def process_player_input(event, player, enemy, game_map):
    if event.type != pygame.KEYDOWN:
        return ""

    x = player.position[0]
    y = player.position[1]

    new_x = x
    new_y = y
    moved = False

    if event.key == pygame.K_LEFT:
        new_x = max(0, x - 1)
        moved = True
    elif event.key == pygame.K_RIGHT:
        new_x = min(GRID_WIDTH - 1, x + 1)
        moved = True
    elif event.key == pygame.K_UP:
        new_y = max(0, y - 1)
        moved = True
    elif event.key == pygame.K_DOWN:
        new_y = min(GRID_HEIGHT - 1, y + 1)
        moved = True

    if moved:
        if (new_x, new_y) != enemy.position and game_map[new_y][new_x] != 1:
            player.position = (new_x, new_y)

    return ""
