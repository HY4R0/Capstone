from map import has_line_of_sight, get_next_path_step


def get_enemy_target(player, enemy, game_map):
    player_x = player.position[0]
    player_y = player.position[1]
    enemy_x = enemy.position[0]
    enemy_y = enemy.position[1]

    distance = abs(player_x - enemy_x) + abs(player_y - enemy_y)

    if getattr(enemy, 'telegraph', False) or distance == 1:
        return (player_x, player_y)

    return get_next_path_step(enemy.position, player.position, game_map)


def enemy_turn(player, enemy, game_map):
    # enemy attacks player, handles poison/burn, moves enemy if not adjacent
    player_x = player.position[0]
    player_y = player.position[1]

    enemy_x = enemy.position[0]
    enemy_y = enemy.position[1]

    message = ""

    def process_status_effects(entity):
        msgs = []
        new_effects = []

        for eff in getattr(entity, 'status_effects', []):
            etype = eff.get('type')
            dmg = eff.get('dmg', 0)
            duration = eff.get('duration', 0)

            if dmg > 0 and duration > 0:
                entity.hp = max(0, entity.hp - dmg)
                msgs.append(str(entity.name) + " suffers " + str(dmg) + " " + str(etype) + " damage.")

            eff['duration'] = duration - 1

            if eff['duration'] > 0:
                new_effects.append(eff)

        entity.status_effects = new_effects
        return msgs

    all_msgs = process_status_effects(player) + process_status_effects(enemy)
    if all_msgs:
        message = " ".join(all_msgs)

    distance = abs(player_x - enemy_x) + abs(player_y - enemy_y)
    behavior = getattr(enemy, 'behavior', 'melee')

    # special sniper logic
    if behavior == 'sniper':
        if getattr(enemy, 'special_cooldown', 0) > 0:
            enemy.special_cooldown -= 1

        if getattr(enemy, 'telegraph', False):
            if has_line_of_sight(enemy.position, player.position, game_map):
                if enemy.weapon:
                    damage = enemy.weapon.damage * 1.5
                else:
                    damage = 0

                player.hp = player.hp - damage
                if player.hp < 0:
                    player.hp = 0

                message = str(enemy.name) + " fires a precise shot!"
            else:
                message = str(enemy.name) + "'s shot was blocked by a wall!"

            enemy.telegraph = False
            enemy.special_cooldown = 3
            return message

        if getattr(enemy, 'special_cooldown', 0) <= 0 and distance >= 3:
            if has_line_of_sight(enemy.position, player.position, game_map):
                enemy.telegraph = True
                message = str(enemy.name) + " takes aim..."
                return message

    if distance == 1:
        if enemy.weapon:
            damage = enemy.weapon.damage
        else:
            damage = 0

        player.hp = player.hp - damage
        if player.hp < 0:
            player.hp = 0

        message = str(enemy.name) + " hits you!"

        if getattr(enemy, 'behavior', '') == 'melee' and 'Raddle' in enemy.name:
            player.status_effects.append({'type': 'poison', 'duration': 3, 'dmg': 2})
            message += " You are poisoned!"

        if getattr(enemy, 'behavior', '') == 'boss' or 'Skeleton' in enemy.name:
            player.status_effects.append({'type': 'burn', 'duration': 3, 'dmg': 3})
            message += " You are burning!"

    else:
        next_step = get_next_path_step(enemy.position, player.position, game_map)
        if next_step != player.position:
            enemy.position = next_step

    return message


def draw_enemy_aim(surface, enemy, target):
    from map import TILE_SIZE, draw_arrow

    target_x = target[0]
    target_y = target[1]

    enemy_x = enemy.position[0]
    enemy_y = enemy.position[1]

    start = (enemy_x * TILE_SIZE + TILE_SIZE // 2, enemy_y * TILE_SIZE + TILE_SIZE // 2)
    end = (target_x * TILE_SIZE + TILE_SIZE // 2, target_y * TILE_SIZE + TILE_SIZE // 2)

    if hasattr(enemy, 'telegraph') and enemy.telegraph:
        draw_arrow(surface, start, end, (255, 50, 50))

        # local import to avoid pygame at module import time
        import pygame

        pygame.draw.circle(surface, (255, 100, 100), end, TILE_SIZE // 4, 2)
    else:
        draw_arrow(surface, start, end, (255, 255, 0))

