import pygame
from entities import Character, Weapon, create_player, create_enemy
from enum import Enum, auto
# import pytmx

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 40
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = 15
FPS = 60
UI_HEIGHT = SCREEN_HEIGHT - GRID_HEIGHT * TILE_SIZE

class TurnState(Enum):
    PLAYER = auto()
    ENEMY = auto()
    VICTORY = auto()
    DEFEAT = auto()



# def load_map(filepath: str):
#     """Load a TMX map file using pytmx."""
#     return pytmx.load_pygame(filepath)


def draw_characters(surface: pygame.Surface, player: Character, enemy: Character) -> None:
    # draw actor placeholders
    pass


def draw_ui(surface: pygame.Surface, player: Character, enemy: Character, state: TurnState, message: str) -> None:
    
    pass


def process_player_input(event: pygame.event.Event, player: Character, enemy: Character) -> str:
    # handle player movement, attacks, and end-turn input
    return ""


def enemy_turn(player: Character, enemy: Character) -> str:
    # enemy decision-making placeholder
    return ""


def main() -> None:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("PlaceHolder")
    clock = pygame.time.Clock()

    # Load the tilemap
    # game_map = load_map("level.tmx")

    player = create_player()
    enemy = create_enemy()
    state = TurnState.PLAYER
    player.start_turn()
    message = "."

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif state == TurnState.PLAYER:
                message = process_player_input(event, player, enemy)

        if state == TurnState.ENEMY:
            message = enemy_turn(player, enemy)
            state = TurnState.PLAYER
            player.start_turn()

        screen.fill((0, 0, 0))
        draw_characters(screen, player, enemy)
        draw_ui(screen, player, enemy, state, message)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

