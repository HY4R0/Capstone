from dataclasses import dataclass
from typing import Dict, Tuple, Set


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
    weapon_ranged: Weapon
    weapon_melee: Weapon
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

def player_name_input() -> str:
    name = input("Enter your character's name: ")
    if not name.strip():
        return "Player"
    return name

def create_player() -> Character:
    return Character(
        name= player_name_input(),
        stats={"Health": 5, "Agility": 6, "Strength": 5, "Thinking": 7, "Endurance": 4},
        hp="Health" * 5,
        max_hp="Health" * 5,
        weapon_ranged=Weapon(name="9mm Pistol", damage=8, range=4, ap_cost=3),
        weapon_melee=Weapon(name="Combat Knife", damage=4, range=1, ap_cost=2),
        position=(2, 7),
    )


def create_enemy() -> Character:
    return Character(
        name="Raddle Snake",
        stats={"Health": 3, "Agility": 7, "Strength": 5, "Thinking": 2, "Endurance": 2},
        hp="Health" * 5,
        max_hp="Health" * 5,
        weapon=Weapon(name="Bite", damage=6, range=1, ap_cost=2),
        position=(16, 7),
    )

def create_enemy() -> Character:
    return Character(
        name="Scavenger",
        stats={"Health": 5, "Agility": 3, "Strength": 5, "Thinking": 1, "Endurance": 6},
        hp="Health" * 5,
        max_hp="Health" * 5,
        weapon=Weapon(name="Baseball Bat", damage=6, range=2, ap_cost=2),
        position=(16, 7),
    )

def create_enemy() -> Character:
    return Character(
        name="Joe The Scavenger",
        stats={"Health": 8, "Agility": 7, "Strength": 6, "Thinking": 3, "Endurance": 9},
        hp="Health" * 5,
        max_hp="Health" * 5,
        weapon=Weapon(name="Assault Rifle", damage=10, range=5, ap_cost=6),
        position=(16, 7),
    )