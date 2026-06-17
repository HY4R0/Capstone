import pygame

from entities import create_player

from map import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GRID_HEIGHT,
    GRID_WIDTH,
    TILE_SIZE,
    FPS,
    ENEMY_TURN_INTERVAL,
    GAME_MAP,
    draw_background,
    draw_walls,
    draw_teleport_spots,
    load_area,
    get_teleport_destination,
    get_player_attack_target,
    draw_player_attack_aim,
    has_line_of_sight,
)


from inputs import get_player_name, process_player_input
from combat import enemy_turn, get_enemy_target, draw_enemy_aim

pygame.init()


def upgrade_weapon(player, choice):
    if choice == 1 and player.weapon_melee:
        player.weapon_melee.damage = player.weapon_melee.damage + 4
    elif choice == 2 and player.weapon_ranged:
        player.weapon_ranged.damage = player.weapon_ranged.damage + 2
        player.weapon_ranged.range = player.weapon_ranged.range + 1
    elif choice == 3:
        player.hp = player.hp + 10
        if player.hp > player.max_hp:
            player.hp = player.max_hp
    elif choice == 4:
        player.max_hp = player.max_hp + 5
        player.hp = player.hp + 5


def draw_ui(surface, player, enemy, area, message, teleport_unlocked):
    font = pygame.font.SysFont(None, 24)

    player_hp_text = str(player.name) + " HP: " + str(player.hp) + "/" + str(player.max_hp)
    player_hp_surf = font.render(player_hp_text, True, (255, 255, 255))
    surface.blit(player_hp_surf, (10, GRID_HEIGHT * TILE_SIZE + 10))

    enemy_hp_text = str(enemy.name) + " HP: " + str(enemy.hp) + "/" + str(enemy.max_hp)
    enemy_hp_surf = font.render(enemy_hp_text, True, (255, 255, 255))
    surface.blit(enemy_hp_surf, (250, GRID_HEIGHT * TILE_SIZE + 10))

    if teleport_unlocked:
        teleport_status = "UNLOCKED"
    else:
        teleport_status = "LOCKED"

    area_text = "Area: " + area.name + "  Teleport: " + teleport_status + "  [T] pad"
    area_surf = font.render(area_text, True, (255, 255, 255))
    surface.blit(area_surf, (10, GRID_HEIGHT * TILE_SIZE + 40))

    msg_surf = font.render(message, True, (255, 255, 0))
    surface.blit(msg_surf, (10, GRID_HEIGHT * TILE_SIZE + 70))


def draw_upgrade_screen(surface, player):
    surface.fill((20, 20, 20))

    font_title = pygame.font.SysFont(None, 48)
    font_text = pygame.font.SysFont(None, 32)

    title = font_title.render("ENEMY DEFEATED!", True, (0, 255, 0))
    upgrade_prompt = font_text.render("Choose an upgrade:", True, (255, 255, 255))

    melee_damage = player.weapon_melee.damage + 4
    ranged_damage = player.weapon_ranged.damage + 2
    ranged_range = player.weapon_ranged.range + 1

    melee_text = "[1] Melee: " + player.weapon_melee.name + " (+ 4 damage) - New Damage: " + str(melee_damage)
    ranged_text = "[2] Ranged: " + player.weapon_ranged.name + " (+ 2 damage, + 1 range) - New Damage: " + str(ranged_damage) + ", New Range: " + str(ranged_range)

    health_name = player.health.name if hasattr(player, 'health') else "Medkit"
    heal_text = "[3] Heal: " + health_name + " + 10 HP (Current: " + str(player.hp) + "/" + str(player.max_hp) + ")"

    maxhp_text = "[4] Vitality: + 5 Max HP and + 5 Current HP - New max: " + str(player.max_hp + 5) + ""

    melee_surf = font_text.render(melee_text, True, (100, 200, 255))
    ranged_surf = font_text.render(ranged_text, True, (100, 200, 255))
    heal_surf = font_text.render(heal_text, True, (100, 200, 255))
    maxhp_surf = font_text.render(maxhp_text, True, (100, 200, 255))

    title_x = SCREEN_WIDTH // 2 - title.get_width() // 2
    surface.blit(title, (title_x, 100))
    surface.blit(upgrade_prompt, (50, 200))
    surface.blit(melee_surf, (50, 280))
    surface.blit(ranged_surf, (50, 340))
    surface.blit(heal_surf, (50, 400))
    surface.blit(maxhp_surf, (50, 460))

    pygame.display.flip()


def draw_victory_screen(surface, player):
    surface.fill((20, 40, 20))

    font_title = pygame.font.SysFont(None, 64)
    font_text = pygame.font.SysFont(None, 32)

    title = font_title.render("VICTORY!", True, (0, 255, 0))
    message = font_text.render(player.name + " has conquered all 10 areas!", True, (255, 255, 255))

    hp_text = font_text.render("Final HP: " + str(player.hp) + "/" + str(player.max_hp), True, (255, 255, 100))
    melee_text = font_text.render("Melee Damage: " + str(player.weapon_melee.damage), True, (100, 200, 255))
    ranged_text = font_text.render("Ranged Damage: " + str(player.weapon_ranged.damage) + ", Range: " + str(player.weapon_ranged.range), True, (100, 200, 255))
    exit_text = font_text.render("Press any key to exit...", True, (200, 200, 200))

    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
    surface.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 180))
    surface.blit(hp_text, (50, 280))
    surface.blit(melee_text, (50, 340))
    surface.blit(ranged_text, (50, 400))
    surface.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 500))

    pygame.display.flip()


def draw_defeat_screen(surface, player, enemy, reason_message):
    surface.fill((40, 10, 10))

    font_title = pygame.font.SysFont(None, 64)
    font_text = pygame.font.SysFont(None, 32)

    title = font_title.render("DEFEAT!", True, (255, 60, 60))

    if reason_message:
        message = font_text.render(reason_message, True, (255, 255, 255))
    else:
        message = font_text.render(enemy.name + " wins!", True, (255, 255, 255))

    hp_text = font_text.render("Final HP: " + str(player.hp) + "/" + str(player.max_hp), True, (255, 200, 120))
    exit_text = font_text.render("Press any key to exit...", True, (200, 200, 200))

    surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))
    surface.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, 180))
    surface.blit(hp_text, (50, 280))
    surface.blit(exit_text, (SCREEN_WIDTH // 2 - exit_text.get_width() // 2, 500))

    pygame.display.flip()



def draw_characters(surface, player, enemy):
    player_x = player.position[0]
    player_y = player.position[1]

    enemy_x = enemy.position[0]
    enemy_y = enemy.position[1]

    pygame.draw.rect(surface, (0, 200, 0), (player_x * TILE_SIZE, player_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    pygame.draw.rect(surface, (200, 0, 0), (enemy_x * TILE_SIZE, enemy_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Nuclear Winter")
    clock = pygame.time.Clock()

    player_name = get_player_name(screen, clock, FPS)

    if player_name is None:
        pygame.quit()
        return

    player = create_player(player_name)
    current_area, enemy = load_area("Ruins", player, set())

    message = ""
    game_over = False
    upgrade_screen = False
    victory = False
    defeat = False

    next_area_unlocked = False
    enemy_timer = 0
    areas_completed = 0


    running = True
    while running:
        if victory:
            draw_victory_screen(screen, player)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    running = False

            clock.tick(FPS)
            continue

        if defeat:
            draw_defeat_screen(screen, player, enemy, message)

            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    running = False

            clock.tick(FPS)
            continue


        if upgrade_screen:
            draw_upgrade_screen(screen, player)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        upgrade_weapon(player, 1)
                        next_area_unlocked = True
                        upgrade_screen = False
                        message = "Upgrade applied! Teleport ready."
                    elif event.key == pygame.K_2:
                        upgrade_weapon(player, 2)
                        next_area_unlocked = True
                        upgrade_screen = False
                        message = "Upgrade applied! Teleport ready."
                    elif event.key == pygame.K_3:
                        upgrade_weapon(player, 3)
                        next_area_unlocked = True
                        upgrade_screen = False
                        message = "Healed +10 HP! Teleport ready."
                    elif event.key == pygame.K_4:
                        upgrade_weapon(player, 4)
                        next_area_unlocked = True
                        upgrade_screen = False
                        message = "Max HP up +5! Teleport ready."

            clock.tick(FPS)
            continue

        # handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # teleport key
                if event.key == pygame.K_t:
                    teleport_target = get_teleport_destination(current_area, player.position, next_area_unlocked)
                    if teleport_target:
                        current_area, enemy = load_area(teleport_target, player, set())
                        message = "Teleported to " + teleport_target + "."
                        game_over = False
                        next_area_unlocked = False
                        enemy_timer = 0
                        areas_completed += 1
                    elif game_over:
                        message = "Defeat the enemy and choose an upgrade!"
                    else:
                        message = "No active teleporter here."

                # shoot key
                elif (not game_over) and event.key == pygame.K_SPACE:
                    player_x = player.position[0]
                    player_y = player.position[1]
                    enemy_x = enemy.position[0]
                    enemy_y = enemy.position[1]

                    distance = abs(player_x - enemy_x) + abs(player_y - enemy_y)

                    # melee slash
                    if distance == 1 and player.weapon_melee:
                        enemy.hp = max(0, enemy.hp - player.weapon_melee.damage)
                        message = "You slash " + enemy.name + "!"

                    # ranged shot
                    elif player.weapon_ranged and distance > 0 and distance <= player.weapon_ranged.range:
                        if has_line_of_sight(player.position, enemy.position, GAME_MAP):
                            enemy.hp = max(0, enemy.hp - player.weapon_ranged.damage)
                            message = "You shoot " + enemy.name + "!"
                        else:
                            message = "Shot blocked by a wall obstacle!"
                    else:
                        message = "Enemy out of range!"

                # movement
                else:
                    process_player_input(event, player, enemy, GAME_MAP)

        # check health
        if not game_over:
            if enemy.hp <= 0:
                game_over = True
                message = player.name + " defeated " + enemy.name + "!"

                if current_area.next_area is None:
                    victory = True
                else:
                    upgrade_screen = True

            elif player.hp <= 0:
                game_over = True
                defeat = True
                message = enemy.name + " wins!"

                if current_area.next_area is None:
                    victory = False




        # enemy turn on a timer
        if not game_over:
            enemy_timer += 1
            if enemy_timer >= ENEMY_TURN_INTERVAL:
                emsg = enemy_turn(player, enemy, GAME_MAP)
                enemy_timer = 0
                if emsg:
                    message = emsg

        # check again after enemy turn
        if not game_over:
            if player.hp <= 0:
                game_over = True
                defeat = True
                message = enemy.name + " wins!"
            elif enemy.hp <= 0:

                game_over = True
                if current_area.next_area is None:
                    victory = True
                else:
                    upgrade_screen = True

        # draw stuff
        draw_background(screen, current_area)
        draw_walls(screen, GAME_MAP)
        draw_teleport_spots(screen, current_area, next_area_unlocked)

        player_target = get_player_attack_target(player, enemy, GAME_MAP)
        if player_target is not None:
            draw_player_attack_aim(screen, player, player_target)

        enemy_target = get_enemy_target(player, enemy, GAME_MAP)
        draw_enemy_aim(screen, enemy, enemy_target)

        draw_characters(screen, player, enemy)
        draw_ui(screen, player, enemy, current_area, message, next_area_unlocked)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

# Main game
if __name__ == "__main__":
    main()

