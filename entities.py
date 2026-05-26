import pygame

class Entity:
    def __init__(self, x, y, hp, color, tile_size):
        self.grid_x = x  # Position in grid coordinates (e.g., tile 5, tile 4)
        self.grid_y = y
        self.hp = hp
        self.max_hp = hp
        self.color = color
        self.tile_size = tile_size

    def draw(self, surface):
        # Calculate pixel position based on grid position
        pixel_x = self.grid_x * self.tile_size
        pixel_y = self.grid_y * self.tile_size
        rect = pygame.Rect(pixel_x, pixel_y, self.tile_size, self.tile_size)
        pygame.draw.rect(surface, self.color, rect)

class Player(Entity):
    def __init__(self, x, y, tile_size):
        # Players have 100 HP, green color (Pip-Boy style), and 10 Action Points
        super().__init__(x, y, 100, (0, 255, 0), tile_size)
        self.max_ap = 10
        self.ap = self.max_ap
        self.stimpacks = 3

    def move(self, dx, dy, game_map):
        # Check boundaries and walls (0 = empty space, 1 = wall)
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy
        
        if 0 <= new_x < len(game_map[0]) and 0 <= new_y < len(game_map):
            if game_map[new_y][new_x] == 0:
                if self.ap >= 1:
                    self.grid_x = new_x
                    self.grid_y = new_y
                    self.ap -= 1
                    return True
        return False

    def heal(self):
        if self.stimpacks > 0 and self.ap >= 2:
            self.hp = min(self.max_hp, self.hp + 30)
            self.stimpacks -= 1
            self.ap -= 2
            return True
        return False

class Enemy(Entity):
    def __init__(self, x, y, tile_size):
        # Enemies have 30 HP and are red
        super().__init__(x, y, 30, (255, 0, 0), tile_size)

    def take_turn(self, player, game_map):
        """Simple AI: Move 1 step closer to the player on the grid."""
        if self.hp <= 0:
            return

        dx = player.grid_x - self.grid_x
        dy = player.grid_y - self.grid_y

        # Move horizontally or vertically toward player
        move_x = 1 if dx > 0 else -1 if dx < 0 else 0
        move_y = 1 if dy > 0 else -1 if dy < 0 else 0

        # Simple attack trigger if adjacent
        if abs(dx) + abs(dy) == 1:
            player.hp -= 5
            print(f"Enemy bit you! Player HP: {player.hp}")
        else:
            # Otherwise, move closer if there's no wall
            if move_x != 0 and game_map[self.grid_y][self.grid_x + move_x] == 0:
                self.grid_x += move_x
            elif move_y != 0 and game_map[self.grid_y + move_y][self.grid_x] == 0:
                self.grid_y += move_y