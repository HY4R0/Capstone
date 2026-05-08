import pygame
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum


pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
TILE_SIZE = 40
FPS = 60

class SPECIAL(Enum):
    STRENGTH = "STR"
    PERCEPTION = "PER"
    ENDURANCE = "END"
    CHARISMA = "CHA"
    INTELLIGENCE = "INT"
    AGILITY = "AGI"
    LUCK = "LCK"

@dataclass
class Character:
    """Base character class"""
    name: str
    stats: Dict[CharacterStat, int]  # 1-10 scale
    hp: int
    max_hp: int
    skills: Dict[str, int]  # Guns, Melee, Speech, etc.
    level: int = 1
    experience: int = 0
    
    def chance_to_hit(self, weapon_skill: str, distance: int) -> int:
        # Base chance off of AGI, PER, and WEAPON_SKILL

    def take_damage(self, damage: int):
        self.hp -= damage
        if self.hp <= 0:

    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)

class Player(Character):
    
    def __init__(self, name: str):

