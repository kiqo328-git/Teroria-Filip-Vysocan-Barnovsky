import pygame
import sys
import os
from settings import *
from assets import AssetManager
from tile_manager import TileManager
from chunk import Chunk
from physics import apply_physics
from character_body import CharacterBody, NPC
from player_input import PlayerInput
from calculation import is_player_near_block
from inventory_manager import InventoryManager
from menu import Menu, LEADERBOARD_FILE


# --- POMOCNÉ FUNKCIE ---

def save_score(time_elapsed):
    """Uloží čas do súboru."""
    try:
        scores = []
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, "r") as f:
                scores = [float(line.strip()) for line in f.readlines() if line.strip()]

        scores.append(time_elapsed)
        scores.sort()
        scores = scores[:15]

        with open(LEADERBOARD_FILE, "w") as f:
            for s in scores:
                f.write(f"{s:.2f}\n")
    except Exception as e:
        print(f"Chyba pri ukladaní skóre: {e}")


def find_surface_y(chunks, x_coord):
    """
    Nájde Y súradnicu prvého pevného bloku v UŽ VYGENEROVANÝCH chunkoch.
    """
    print(f"Hľadám povrch na X={x_coord}...")
    chunk_x = int(x_coord // (CHUNK_SIZE * TILE_SIZE))

    # Prehľadávame bloky odhora (-1000) nadol
    # Predpokladáme, že chunky už sú v slovníku 'chunks'
    for y in range(-1000, 2000, TILE_SIZE):
        cy = int(y // (CHUNK_SIZE * TILE_SIZE))

        if (chunk_x, cy) in chunks:
            block = chunks[(chunk_x, cy)].get_block_at(x_coord, y)
            # Hľadáme čokoľvek okrem vzduchu (0) a Bedrocku (4 - ak nechceš spawnúť na dne)
            # Alebo ak je Bedrock v poriadku, vymaž "and block != 4"
            if block != 0:
                print(f"Povrch nájdený na Y={y} (Blok ID: {block})")
                return y - (PLAYER_SCALE * 160) - 5  # Spawn trochu nad blokom

    print("VAROVANIE: Povrch nenájdený, používam fallback.")
    return -500


# --- HLAVNÝ KÓD ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Troria - Python")
    clock = pygame.time.Clock()

    # Načítanie assetov
    assets = AssetManager()
    tile_manager = TileManager(assets)

    # End screen
    try:
        end_bg_img = pygame.image.load(os.path.join(ASSETS_DIR, END_SCREEN)).convert()
        end_bg_img = pygame.transform.scale(end_bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception:
        end_bg_img = None

    menu = Menu(screen)
    font = pygame.font.SysFont("Arial", 18)
    large_font = pygame.font.SysFont("Arial", 50)

    # Premenné hry
    game_state = "menu"
    player = None
    player_input = None
    inventory = None
    chunks = {}
    npcs = {}
    camera_scroll = [0, 0]

    # Logika časovača a hry
    time_left = GAME_DURATION
    final_time = 0.0
    mining_timer = 0.0
    MINING_SPEED = 0.15
    interaction_text = ""

    highlight_surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
    highlight_surf.set_alpha(100)
    highlight_surf.fill((255, 255, 255))

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --- 1. MENU ---
        if game_state == "menu":
            action = menu.handle_input()

            if action == "game":
                # === INICIALIZÁCIA NOVEJ HRY ===
                chunks = {}
                npcs = {}
                camera_scroll = [0, 0]
                mining_timer = 0.0
                time_left = GAME_DURATION
                interaction_text = ""

                # KROK 1: Najprv vygenerujeme stredové chunky (aby mal hráč kam dopadnúť)
                print("Pred-generujem spawn chunky...")
                spawn_chunk_x = 0
                # Vygenerujeme vertikálny stĺpec okolo stredu
                for cy in range(-5, 6):
                    # Vygenerujeme aj susedov do šírky, aby to vyzeralo dobre hneď
                    for cx in range(-1, 2):
                        if (cx, cy) not in chunks:
                            chunks[(cx, cy)] = Chunk(cx, cy, tile_manager)

                # KROK 3: Vytvoríme hráča na nájdenej pozícii
                player = CharacterBody(0, -2000, PLAYER_SCALE, assets.get_player_paths(0))
                player_input = PlayerInput(player)
                inventory = InventoryManager(hotbar_size=8)

                # Vycentrujeme kameru
                camera_scroll[0] = player.rect.centerx - SCREEN_WIDTH // 2
                camera_scroll[1] = player.rect.centery - SCREEN_HEIGHT // 2

                game_state = "playing"

            elif action == "quit":
                running = False

            menu.draw()

        # --- 2. VÝHRA (WON) ---
        elif game_state == "won":
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.MOUSEBUTTONDOWN: game_state = "menu"

            if end_bg_img:
                screen.blit(end_bg_img, (0, 0))
            else:
                screen.fill((255, 215, 0))

            time_text = font.render(f"Final Time: {final_time:.2f}s - Click to Menu", True, (255, 255, 255))

            screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 120))
            pygame.display.flip()

        # --- 3. PREHRA (LOST) ---
        elif game_state == "lost":
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.MOUSEBUTTONDOWN: game_state = "menu"

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200);
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            msg1 = large_font.render("GAME OVER", True, (255, 50, 50))
            msg2 = font.render("Time ran out. Click to try again.", True, (255, 255, 255))
            screen.blit(msg1, (SCREEN_WIDTH // 2 - msg1.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(msg2, (SCREEN_WIDTH // 2 - msg2.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            pygame.display.flip()

        # --- 4. HRANIE (PLAYING) ---
        elif game_state == "playing":
            time_left -= dt
            if time_left <= 0:
                time_left = 0
                game_state = "lost"

            player_x, player_y = player.get_player_pos()
            player_cx = int(player.rect.centerx // (CHUNK_SIZE * TILE_SIZE))
            player_cy = int(player.rect.centery // (CHUNK_SIZE * TILE_SIZE))
            wmx, wmy = player_input.get_mouse_world_pos(camera_scroll)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.MOUSEWHEEL: inventory.scroll(event.y)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: game_state = "menu"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    selected_item_id = inventory.get_selected_item()
                    if event.button == 3:  # Right Click
                        if selected_item_id == 6:  # Monster
                            inventory.remove_selected_item(1)
                            final_time = GAME_DURATION - time_left
                            save_score(final_time)
                            game_state = "won"
                        elif selected_item_id != 0:
                            if player.place_block(wmx, wmy, selected_item_id, chunks):
                                inventory.remove_selected_item(1)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                    interaction_text = ""
                    pos = player.get_player_pos()
                    for npc in npcs.values():
                        if npc.is_player_in_range(pos):
                            if not npc.gift_given:
                                inventory.add_item(6, 1)
                                npc.gift_given = True
                                interaction_text = "Dostal si Monster!"
                            else:
                                interaction_text = "Uz si dostal darcek."
                            break

            if pygame.mouse.get_pressed()[0]:
                if mining_timer <= 0:
                    dropped_id = player.destroy_block(wmx, wmy, chunks)
                    if dropped_id != 0:
                        inventory.add_item(dropped_id, 1)
                        mining_timer = MINING_SPEED
            if mining_timer > 0: mining_timer -= dt

            # Update Physics & Logic
            player_input.update(dt, camera_scroll, chunks)
            apply_physics(player, chunks, dt)
            player.update()

            for npc in npcs.values():
                apply_physics(npc, chunks, dt)
                npc.update(player.rect)

            # Camera
            target_x = player.rect.centerx - SCREEN_WIDTH // 2
            target_y = player.rect.centery - SCREEN_HEIGHT // 2
            camera_scroll[0] += (target_x - camera_scroll[0]) * 0.1
            camera_scroll[1] += (target_y - camera_scroll[1]) * 0.1

            # Generovanie nových chunkov (počas pohybu)
            for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
                for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                    target_cx = player_cx + dx
                    target_cy = player_cy + dy
                    chunk_key = (target_cx, target_cy)
                    if chunk_key not in chunks:
                        new_chunk = Chunk(target_cx, target_cy, tile_manager)
                        chunks[chunk_key] = new_chunk
                        for wx, wy in new_chunk.npc_spawn_coords:
                            if wx not in npcs:
                                npc_x = wx * TILE_SIZE + TILE_SIZE // 2
                                npc_y = (wy * TILE_SIZE) + (TILE_SIZE // 2) - (160 * PLAYER_SCALE / 2) - 10
                                npcs[wx] = NPC(npc_x, npc_y, PLAYER_SCALE, assets.get_player_paths(0))

            # Unload
            for key in list(chunks.keys()):
                if abs(key[0] - player_cx) > UNLOAD_DISTANCE or abs(key[1] - player_cy) > UNLOAD_DISTANCE:
                    del chunks[key]
            for key in list(npcs.keys()):
                ncx = int(npcs[key].rect.centerx // (CHUNK_SIZE * TILE_SIZE))
                ncy = int(npcs[key].rect.centery // (CHUNK_SIZE * TILE_SIZE))
                if abs(ncx - player_cx) > UNLOAD_DISTANCE or abs(ncy - player_cy) > UNLOAD_DISTANCE:
                    del npcs[key]

            # Draw
            screen.fill(SKY_COLOR)
            for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
                for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                    ck = (player_cx + dx, player_cy + dy)
                    if ck in chunks: chunks[ck].draw(screen, camera_scroll)

            for npc in npcs.values(): npc.draw(screen, camera_scroll)
            player.draw(screen, camera_scroll)

            # Highlight
            gx, gy = int(wmx // 32) * 32, int(wmy // 32) * 32
            mcx, mcy = int(wmx // (16 * 32)), int(wmy // (16 * 32))
            if (mcx, mcy) in chunks:
                if is_player_near_block(player_x, player_y, gx + 16, gy + 16, float(CURRENT_PLAYER_REACH)):
                    screen.blit(highlight_surf, (gx - camera_scroll[0], gy - camera_scroll[1]))

            # UI
            slot_size = 50;
            padding = 5
            start_x = (SCREEN_WIDTH - (len(inventory.hotbar) * (slot_size + padding))) // 2
            start_y = SCREEN_HEIGHT - slot_size - 20
            for i, slot in enumerate(inventory.hotbar):
                x = start_x + i * (slot_size + padding)
                col = (255, 215, 0) if i == inventory.selected_index else (100, 100, 100)
                pygame.draw.rect(screen, col, (x, start_y, slot_size, slot_size), 3)
                pygame.draw.rect(screen, (50, 50, 50), (x + 3, start_y + 3, slot_size - 6, slot_size - 6))
                if slot['id'] != 0:
                    tex = tile_manager.get_texture(slot['id'], 0, False)
                    if tex: screen.blit(pygame.transform.scale(tex, (32, 32)), (x + 9, start_y + 9))
                    if slot['count'] > 1:
                        screen.blit(font.render(str(slot['count']), True, (255, 255, 255)), (x + 35, start_y + 30))

            info = f"Time: {int(time_left // 60):02}:{int(time_left % 60):02} | FPS: {int(clock.get_fps())}"
            screen.blit(font.render(info, True, (0, 0, 0) if time_left > 30 else (255, 0, 0)), (10, 10))
            if interaction_text:
                ts = font.render(interaction_text, True, (0, 0, 0))
                screen.blit(ts, (SCREEN_WIDTH // 2 - ts.get_width() // 2, SCREEN_HEIGHT - 100))

            pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()