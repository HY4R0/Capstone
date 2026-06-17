class Weapon:
    def __init__(self, name, damage, range, hp=0):
        # this is a weapon, like a sword or gun
        self.name = name
        self.damage = damage
        self.range = range
        self.hp = hp


class Character:
    def __init__(
        self,
        name,
        stats,
        hp,
        max_hp,
        weapon_ranged=None,
        weapon_melee=None,
        weapon=None,
        health=None,
        position=(0, 0),
    ):
        # store everything as attributes
        self.name = name
        self.stats = stats

        self.hp = hp
        self.max_hp = max_hp

        self.weapon_ranged = weapon_ranged
        self.weapon_melee = weapon_melee

        self.weapon = weapon
        self.health = health

        # grid position (x,y)
        self.position = position

        # list of status effects we keep applying each turn
        self.status_effects = []


def create_player(name):
    # stats for the player (just a dict)
    stats = {
        "Health": 5,
        "Agility": 6,
        "Strength": 5,
        "Thinking": 7,
        "Endurance": 4,
    }

    # hp is just Health * 5
    hp = stats["Health"] * 5

    # create the player character with both melee and ranged weapons
    player = Character(
        name=name,
        stats=stats,
        hp=hp,
        max_hp=hp,
        weapon_ranged=Weapon(name="10mm Pistol", damage=4, range=2),
        weapon_melee=Weapon(name="Ripper", damage=8, range=1),
        health=Weapon(name="Medkit", damage=0, range=0, hp=10),
        position=(2, 7),
    )

    return player


def create_enemy_for_area(area_name):
    # All enemies for each area.
    # Each enemy record has the same basic stuff.
    enemies = {
        "Ruins": {
            "name": "Raddle-Snake",
            "stats": {"Health": 6, "Agility": 8, "Strength": 5, "Thinking": 2, "Endurance": 7},
            "weapon_name": "Claws",
            "damage": 6,
            "range": 1,
            "behavior": "melee",
        },
        "Outpost": {
            "name": "Raider Scout",
            "stats": {"Health": 7, "Agility": 7, "Strength": 6, "Thinking": 4, "Endurance": 8},
            "weapon_name": "Rifle",
            "damage": 7,
            "range": 6,
            "behavior": "sniper",
        },
        "Lab": {
            "name": "Mad Scientist",
            "stats": {"Health": 5, "Agility": 9, "Strength": 7, "Thinking": 8, "Endurance": 6},
            "weapon_name": "Laser",
            "damage": 9,
            "range": 5,
            "behavior": "ranged",
        },
        "Shore": {
            "name": "Mirelurk",
            "stats": {"Health": 9, "Agility": 5, "Strength": 8, "Thinking": 1, "Endurance": 10},
            "weapon_name": "Pincers",
            "damage": 8,
            "range": 1,
            "behavior": "melee",
        },
        "Vault": {
            "name": "Vault Dweller",
            "stats": {"Health": 10, "Agility": 2, "Strength": 8, "Thinking": 5, "Endurance": 12},
            "weapon_name": "Minigun",
            "damage": 5,
            "range": 6,
            "behavior": "ranged",
        },
        "Wasteland": {
            "name": "Deathclaw",
            "stats": {"Health": 12, "Agility": 6, "Strength": 10, "Thinking": 1, "Endurance": 11},
            "weapon_name": "Talons",
            "damage": 10,
            "range": 1,
            "behavior": "bruiser",
        },
        "Bunker": {
            "name": "Assaultron",
            "stats": {"Health": 11, "Agility": 4, "Strength": 9, "Thinking": 7, "Endurance": 13},
            "weapon_name": "Plasma Rifle",
            "damage": 8,
            "range": 5,
            "behavior": "ranged",
        },
        "Tower": {
            "name": "Synth Enforcer",
            "stats": {"Health": 8, "Agility": 8, "Strength": 8, "Thinking": 9, "Endurance": 8},
            "weapon_name": "Plasma Rifle",
            "damage": 9,
            "range": 4,
            "behavior": "ranged",
        },
        "Underground": {
            "name": "Feral Ghoul Roamer",
            "stats": {"Health": 7, "Agility": 9, "Strength": 6, "Thinking": 1, "Endurance": 8},
            "weapon_name": "Claws",
            "damage": 7,
            "range": 1,
            "behavior": "melee",
        },
        "Summit": {
            "name": "Skeleton Dragon",
            "stats": {"Health": 20, "Agility": 15, "Strength": 15, "Thinking": 15, "Endurance": 15},
            "weapon_name": "Breath",
            "damage": 15,
            "range": 8,
            "behavior": "boss",
        },
    }

    # if area doesn't exist, just use Ruins
    if area_name in enemies:
        enemy_data = enemies[area_name]
    else:
        enemy_data = enemies["Ruins"]

    # enemy stats and hp
    enemy_stats = enemy_data["stats"]
    enemy_hp = enemy_stats["Health"] * 5

    # make the weapon the enemy uses
    enemy_weapon = Weapon(
        name=enemy_data["weapon_name"],
        damage=enemy_data["damage"],
        range=enemy_data["range"],
    )

    # make enemy Character
    enemy = Character(
        name=enemy_data["name"],
        stats=enemy_stats,
        hp=enemy_hp,
        max_hp=enemy_hp,
        weapon=enemy_weapon,
        health=Weapon(name="Medkit", damage=0, range=0, hp=10),
        position=(16, 7),
    )

    # extra enemy fields used by main.py
    enemy.behavior = enemy_data.get("behavior", "melee")
    enemy.special_cooldown = 0
    enemy.telegraph = False

    return enemy

