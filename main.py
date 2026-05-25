import pygame
from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Tuple, Set

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

@dataclass
class Weapon:
    name: str
    damage: int
    range: int
    ap_cost: int

@dataclass
class Character:
    name: str
    stats: Dict[str, int]
    hp: int
    max_hp: int
    weapon: Weapon
    position: Tuple[int, int]
    ap: int = 0
    max_ap: int = 6

    def start_turn(self) -> None:
        self.ap = self.max_ap

    def move(self, dx: int, dy: int, occupied: Set[Tuple[int, int]]) -> bool:
        # movement cost and valid tile checks go here
        return False

    def can_attack(self, target: "Character") -> bool:
        # range checks and AP checks go here
        return False

    def attack(self, target: "Character") -> bool:
        # attack resolution stub
        return False


def create_player() -> Character:
    return Character(
        name="Scout",
        stats={"Power": 5, "Sight": 6, "Resolve": 5, "Speed": 7, "Tech": 4},
        hp=30,
        max_hp=30,
        weapon=Weapon(name="Burst Pistol", damage=8, range=4, ap_cost=3),
        position=(2, 7),
    )


def create_enemy() -> Character:
    return Character(
        name="Wasteland Stalker",
        stats={"Power": 4, "Sight": 5, "Resolve": 4, "Speed": 5, "Tech": 2},
        hp=24,
        max_hp=24,
        weapon=Weapon(name="Claw", damage=6, range=1, ap_cost=2),
        position=(16, 7),
    )


def draw_grid(surface: pygame.Surface) -> None:
    # draw tile grid
    pass


def draw_characters(surface: pygame.Surface, player: Character, enemy: Character) -> None:
    # draw actor placeholders
    pass


def draw_ui(surface: pygame.Surface, player: Character, enemy: Character, state: TurnState, message: str) -> None:
    # draw combat UI and status text
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

    player = create_player()
    enemy = create_enemy()
    state = TurnState.PLAYER
    player.start_turn()
    message = "Turn-based combat skeleton ready."

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
        draw_grid(screen)
        draw_characters(screen, player, enemy)
        draw_ui(screen, player, enemy, state, message)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()

