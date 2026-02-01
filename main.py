import pygame
import sys
from settings import *
from assets import AssetManager
from tile_manager import TileManager
from chunk import Chunk
from physics import apply_physics
from character_body import CharacterBody, NPC
from player_input import PlayerInput
from calculation import is_player_near_block


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
    npcs = {}
    camera_scroll = [0, 0]

    highlight_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    highlight_surf.set_alpha(100)
    highlight_surf.fill((255, 255, 255))

    # UI pre interakciu
    font = pygame.font.SysFont("Arial", 18)
    interaction_text = ""

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        player_x, player_y = player.get_player_pos()
        player_cx = int(player.rect.centerx // (CHUNK_SIZE * TILE_SIZE))
        player_cy = int(player.rect.centery // (CHUNK_SIZE * TILE_SIZE))

        # --- EVENT HANDLING ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Interakcia s E
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                interaction_text = ""  # Reset text
                player_center_pos = player.get_player_pos()

                # Kontrola interakcie s NPC
                for npc_key, npc in npcs.items():
                    if npc.is_player_in_range(player_center_pos):
                        interaction_text = npc.interact()
                        break  # Interagujeme len s jedným NPC

        # --- CHUNK A NPC GENERÁCIA/NAČÍTANIE ---
        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                target_cx = player_cx + dx
                target_cy = player_cy + dy
                chunk_key = (target_cx, target_cy)

                if chunk_key not in chunks:
                    new_chunk = Chunk(target_cx, target_cy, tile_manager)
                    chunks[chunk_key] = new_chunk

                    # Spawnovanie NPC pri načítaní chunku
                    for wx, wy in new_chunk.npc_spawn_coords:
                        # Unikátny kľúč NPC (svetová súradnica X)
                        npc_key = wx
                        if npc_key not in npcs:
                            # Vypočítame pozíciu NPC (vycentrujeme nad blok)
                            npc_x = wx * TILE_SIZE + TILE_SIZE // 2
                            # Výška postavy je 160*scale
                            collider_height = 160 * PLAYER_SCALE
                            # rect.bottom chceme na hornej hrane bloku (wy * TILE_SIZE)
                            npc_y_center = wy * TILE_SIZE - collider_height / 2

                            npcs[npc_key] = NPC(npc_x, npc_y_center, PLAYER_SCALE, assets.get_player_paths(0))

        # --- UPDATE LOGIKA ---
        player_input.update(dt, camera_scroll, chunks)
        apply_physics(player, chunks)
        player.update()

        # Update NPC (otáčanie)
        for npc in npcs.values():
            npc.update(player.rect)

        # --- CAMERA A UNLOAD LOGIKA ---
        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2
        camera_scroll[0] += (target_x - camera_scroll[0]) * 0.1
        camera_scroll[1] += (target_y - camera_scroll[1]) * 0.1

        # Vyhadzovanie chunkov
        for key in list(chunks.keys()):
            cx, cy = key
            dist_x = abs(cx - player_cx)
            dist_y = abs(cy - player_cy)
            if dist_x > UNLOAD_DISTANCE or dist_y > UNLOAD_DISTANCE:
                del chunks[key]

        # Vyhadzovanie NPC
        for npc_key in list(npcs.keys()):
            npc = npcs[npc_key]
            # Zistíme, v akom chunku je NPC
            npc_cx = int(npc.rect.centerx // (CHUNK_SIZE * TILE_SIZE))
            npc_cy = int(npc.rect.centery // (CHUNK_SIZE * TILE_SIZE))

            if abs(npc_cx - player_cx) > UNLOAD_DISTANCE or abs(npc_cy - player_cy) > UNLOAD_DISTANCE:
                del npcs[npc_key]

        # --- VYKRESLOVANIE ---
        screen.fill(SKY_COLOR)

        # Vykresľovanie chunkov
        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                cx = player_cx + dx
                cy = player_cy + dy
                if (cx, cy) in chunks:
                    chunks[(cx, cy)].draw(screen, camera_scroll)

        # Vykresľovanie NPC (pred hráčom)
        for npc in npcs.values():
            npc.draw(screen, camera_scroll)

        player.draw(screen, camera_scroll)

        # Highlight pod myšou
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
        screen.blit(font.render(info_text, True, (0, 0, 0)), (10, 10))

        # Vykreslenie textu interakcie
        if interaction_text:
            text_surf = font.render(interaction_text, True, (0, 0, 0))
            screen.blit(text_surf, (SCREEN_WIDTH // 2 - text_surf.get_width() // 2, SCREEN_HEIGHT - 50))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()