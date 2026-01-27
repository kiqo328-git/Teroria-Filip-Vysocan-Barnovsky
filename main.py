import pygame
import sys
from settings import *
from assets import AssetManager
from tile_manager import TileManager
from chunk import Chunk
from physics import apply_physics
from character_body import CharacterBody
from player_input import PlayerInput
from numba import njit


@njit(fastmath=True)
def is_player_near_block(px, py, bx, by, reach):
    dx = px - bx
    dy = py - by
    return (dx * dx + dy * dy) <= (reach * reach)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Troria - Python")
    clock = pygame.time.Clock()

    assets = AssetManager()
    tile_manager = TileManager(assets)

    player = CharacterBody(0, -200, PLAYER_SCALE, assets.get_player_paths(0))
    player_input = PlayerInput(player)

    chunks = {}
    camera_scroll = [0, 0]

    highlight_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    highlight_surf.set_alpha(100)
    highlight_surf.fill((255, 255, 255))

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        player_x,player_y = player.get_player_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player_cx = int(player.rect.centerx // (CHUNK_SIZE * TILE_SIZE))
        player_cy = int(player.rect.centery // (CHUNK_SIZE * TILE_SIZE))

        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                target_cx = player_cx + dx
                target_cy = player_cy + dy
                if (target_cx, target_cy) not in chunks:
                    chunks[(target_cx, target_cy)] = Chunk(target_cx, target_cy, tile_manager)

        player_input.update(dt, camera_scroll, chunks)
        apply_physics(player, chunks)
        player.update()

        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2
        camera_scroll[0] += (target_x - camera_scroll[0]) * 0.1
        camera_scroll[1] += (target_y - camera_scroll[1]) * 0.1

        screen.fill(SKY_COLOR)

        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                cx = player_cx + dx
                cy = player_cy + dy
                if (cx, cy) in chunks:
                    chunks[(cx, cy)].draw(screen, camera_scroll)

        for key in list(chunks.keys()):
            cx, cy = key
            dist_x = abs(cx - player_cx)
            dist_y = abs(cy - player_cy)
            if dist_x > UNLOAD_DISTANCE or dist_y > UNLOAD_DISTANCE:
                del chunks[key]

        player.draw(screen, camera_scroll)

        wmx, wmy = player_input.get_mouse_world_pos(camera_scroll)

        grid_x = int(wmx // TILE_SIZE) * TILE_SIZE
        grid_y = int(wmy // TILE_SIZE) * TILE_SIZE

        screen_hl_x = grid_x - camera_scroll[0]
        screen_hl_y = grid_y - camera_scroll[1]

        mouse_cx = int(wmx // (CHUNK_SIZE * TILE_SIZE))
        mouse_cy = int(wmy // (CHUNK_SIZE * TILE_SIZE))

        if (mouse_cx, mouse_cy) in chunks:
            block_under_mouse = chunks[(mouse_cx, mouse_cy)].get_block_at(wmx, wmy)

            if (block_under_mouse != 0 and
                    block_under_mouse != 4 and
                    is_player_near_block(
                        player_x,
                        player_y,
                        grid_x + (TILE_SIZE / 2),
                        grid_y + (TILE_SIZE / 2),
                        float(CURRENT_PLAYER_REACH)
                    )):
                screen.blit(highlight_surf, (screen_hl_x, screen_hl_y))

        # --- UI ---
        world_x = player.rect.centerx // 32
        world_y = -player.rect.centery // 32

        info_text = (
            f"FPS: {int(clock.get_fps())} | "
            f"XY: {world_x}, {world_y}"
        )
        screen.blit(pygame.font.SysFont("Arial", 18).render(info_text, True, (0, 0, 0)), (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()