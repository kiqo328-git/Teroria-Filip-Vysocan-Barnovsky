import pygame
from settings import TILE_SIZE, CHUNK_SIZE
from tile_manager import BLOCKS


def check_collisions(player, chunk_map):
    def is_solid(x, y):
        cx = x // CHUNK_SIZE
        cy = y // CHUNK_SIZE
        bx = x % CHUNK_SIZE
        by = y % CHUNK_SIZE

        if (cx, cy) in chunk_map:
            chunk = chunk_map[(cx, cy)]
            block_id = chunk.layer_fg[by][bx]
            return BLOCKS[block_id]["solid"]
        return False  # Ak chunk nie je načítaný, považuj to za vzduch

    # X Osa
    player.rect.x += player.velocity.x
    start_x = player.rect.left // TILE_SIZE - 1
    end_x = player.rect.right // TILE_SIZE + 1
    start_y = player.rect.top // TILE_SIZE - 1
    end_y = player.rect.bottom // TILE_SIZE + 1

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

    # Y Osa
    player.rect.y += player.velocity.y
    player.grounded = False

    start_x = player.rect.left // TILE_SIZE - 1
    end_x = player.rect.right // TILE_SIZE + 1
    start_y = player.rect.top // TILE_SIZE - 1
    end_y = player.rect.bottom // TILE_SIZE + 1

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