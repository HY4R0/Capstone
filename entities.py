from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Set


@dataclass
class Weapon:
    name: str
    damage: int
    range: int

@dataclass
class Character:
    name: str
    stats: Dict[str, int]
    hp: int
    max_hp: int
    weapon_ranged: Optional[Weapon] = None
    weapon_melee: Optional[Weapon] = None
    weapon: Optional[Weapon] = None
    position: Tuple[int, int] = (0, 0)

    def move(self, dx: int, dy: int, occupied: Set[Tuple[int, int]]) -> bool:
        # movement cost and valid tile checks go here
        return False

    def can_attack(self, target: "Character") -> bool:
        # range checks go here
        return False

    def attack(self, target: "Character") -> bool:
        # attack resolution stub
        return False


def create_player(name: str) -> Character:
    stats = {"Health": 5, "Agility": 6, "Strength": 5, "Thinking": 7, "Endurance": 4}
    hp = stats["Health"] * 5
    return Character(
        name=name or "Player",
        stats=stats,
        hp=hp,
        max_hp=hp,
        weapon_ranged=Weapon(name="9mm Pistol", damage=8, range=4),
        weapon_melee=Weapon(name="Combat Knife", damage=4, range=1),
        position=(2, 7),
    )


def create_enemy() -> Character:
    stats = {"Health": 8, "Agility": 7, "Strength": 6, "Thinking": 3, "Endurance": 9}
    hp = stats["Health"] * 5
    return Character(
        name="Joe The Scavenger",
        stats=stats,
        hp=hp,
        max_hp=hp,
        weapon=Weapon(name="Assault Rifle", damage=1, range=5),
        position=(16, 7),
    )
