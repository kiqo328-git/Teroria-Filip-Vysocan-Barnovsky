import pygame
import sys
from settings import *
from assets import AssetManager
from tile_manager import TileManager
from chunk import Chunk
from physics import apply_physics
from character_body import CharacterBody
from player_input import PlayerInput


# from inventory_manager import InventoryManager # Zatiaľ zakomentované, ak nemáš súbor

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Troria - Python")
    clock = pygame.time.Clock()

    assets = AssetManager()
    tile_manager = TileManager(assets)

    # Vytvorenie hráča (Skin index 0)
    # y = -200 aby sa spawnol vo vzduchu a padol na zem
    player = CharacterBody(0, -200, PLAYER_SCALE, assets.get_player_paths(0))

    # Inicializácia Input Systemu
    player_input = PlayerInput(player)

    # Slovník pre chunky: kľúč je (cx, cy)
    chunks = {}

    camera_scroll = [0, 0]

    running = True
    while running:
        # 1. Výpočet Delta Time (v sekundách)
        # Toto je dôležité pre plynulý pohyb v player_input
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- GENERÁCIA CHUNKOV ---
        player_cx = int(player.rect.centerx // (CHUNK_SIZE * TILE_SIZE))
        player_cy = int(player.rect.centery // (CHUNK_SIZE * TILE_SIZE))

        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                target_cx = player_cx + dx
                target_cy = player_cy + dy

                if (target_cx, target_cy) not in chunks:
                    chunks[(target_cx, target_cy)] = Chunk(target_cx, target_cy, tile_manager)

        # --- LOGIKA A FYZIKA ---

        # 1. Input (nastaví velocity.x a rieši skok)
        player_input.update(dt)

        # 2. FYZIKA (Gravitácia + Kolízie + Pohyb)
        # Toto teraz urobí všetku ťažkú prácu
        apply_physics(player, chunks)

        # 3. Update Vizuálu (prilepí ruky/nohy na novú pozíciu)
        player.update()

        # --- KAMERA ---
        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2
        camera_scroll[0] += (target_x - camera_scroll[0]) * 0.1
        camera_scroll[1] += (target_y - camera_scroll[1]) * 0.1

        # --- VYKRESLĽOVANIE ---
        screen.fill(SKY_COLOR)

        # Vykreslenie chunkov
        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                cx = player_cx + dx
                cy = player_cy + dy
                if (cx, cy) in chunks:
                    chunks[(cx, cy)].draw(screen, camera_scroll)

        # Mazanie starých chunkov
        for key in list(chunks.keys()):
            cx, cy = key
            dist_x = abs(cx - player_cx)
            dist_y = abs(cy - player_cy)

            if dist_x > UNLOAD_DISTANCE or dist_y > UNLOAD_DISTANCE:
                del chunks[key]

        # Vykreslenie hráča
        player.draw(screen, camera_scroll)

        # --- UI (Tvoj formát) ---
        world_x = player.rect.centerx // 32
        world_y = -player.rect.centery // 32

        info_text = (
            f"FPS: {int(clock.get_fps())} | "
            f"World: {world_x}, {world_y} | "
            f"Chunk: {player_cx}, {-player_cy} | "
            f"Seed: {SEED}"
        )
        screen.blit(pygame.font.SysFont("Arial", 18).render(info_text, True, (0, 0, 0)), (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()