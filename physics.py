import pygame
from settings import TILE_SIZE, CHUNK_SIZE, BLOCKS


def apply_physics(player, chunks, dt):
    # --- 1. APLIKÁCIA GRAVITÁCIE ---
    # Gravitáciu násobíme DT (zrýchlenie za čas)
    player.velocity.y += player.gravity * dt

    # Limit maximálnej rýchlosti pádu
    if player.velocity.y > player.max_gravity:
        player.velocity.y = player.max_gravity

    def is_solid(x, y):
        cx = x // CHUNK_SIZE
        cy = y // CHUNK_SIZE
        bx = x % CHUNK_SIZE
        by = y % CHUNK_SIZE

        if (cx, cy) in chunks:
            chunk = chunks[(cx, cy)]
            try:
                block_id = chunk.layer_fg[by][bx]
                if block_id == 0:
                    return False
                return BLOCKS[block_id]["solid"]
            except IndexError:
                return False
        return False

    # --- 2. POHYB X (Do strán) ---
    # Velocity.x už obsahuje dt z player_input (speed * dt), takže tu dt nepridávame
    player.rect.x += player.velocity.x

    start_x = int(player.rect.left // TILE_SIZE) - 1
    end_x = int(player.rect.right // TILE_SIZE) + 1
    start_y = int(player.rect.top // TILE_SIZE) - 1
    end_y = int(player.rect.bottom // TILE_SIZE) + 1

    for y in range(start_y, end_y + 1):
        for x in range(start_x, end_x + 1):
            if is_solid(x, y):
                tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player.rect.colliderect(tile_rect):
                    if player.velocity.x > 0:
                        player.rect.right = tile_rect.left
                        player.velocity.x = 0
                    elif player.velocity.x < 0:
                        player.rect.left = tile_rect.right
                        player.velocity.x = 0

    # --- 3. POHYB Y (Hore/Dole) ---
    # Tu násobíme DT, pretože velocity.y je v pixeloch za sekundu
    player.rect.y += player.velocity.y * dt

    player.grounded = False

    start_x = int(player.rect.left // TILE_SIZE) - 1
    end_x = int(player.rect.right // TILE_SIZE) + 1
    start_y = int(player.rect.top // TILE_SIZE) - 1
    end_y = int(player.rect.bottom // TILE_SIZE) + 1

    for y in range(start_y, end_y + 1):
        for x in range(start_x, end_x + 1):
            if is_solid(x, y):
                tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player.rect.colliderect(tile_rect):
                    if player.velocity.y > 0:
                        player.rect.bottom = tile_rect.top
                        player.velocity.y = 0
                        player.grounded = True
                    elif player.velocity.y < 0:
                        player.rect.top = tile_rect.bottom
                        player.velocity.y = 0