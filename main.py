import pygame
import sys
from settings import *
from assets import AssetManager
from tile_manager import TileManager
from chunk import Chunk
from physics import check_collisions
from character_body import CharacterBody
from player_input import PlayerInput
from inventory_manager import InventoryManager


class Player:
    def __init__(self):
        # Začneme na 0, 0
        self.rect = pygame.Rect(0, -100, 24, 56)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 6
        self.jump_force = -12
        self.gravity = 0.5
        self.grounded = False

    def update(self):
        self.velocity.y += self.gravity
        keys = pygame.key.get_pressed()

        self.velocity.x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity.x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity.x = self.speed

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.grounded:
            self.velocity.y = self.jump_force
            self.grounded = False

    def draw(self, screen, camera_offset):
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height
        )
        pygame.draw.rect(screen, (255, 50, 50), draw_rect)
        # Oči
        pygame.draw.rect(screen, (255, 255, 255), (draw_rect.x + 4, draw_rect.y + 8, 6, 6))
        pygame.draw.rect(screen, (255, 255, 255), (draw_rect.x + 14, draw_rect.y + 8, 6, 6))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Troria - Python")
    clock = pygame.time.Clock()

    assets = AssetManager()
    tile_manager = TileManager(assets)
    # Use new CharacterBody + PlayerInput separation
    # create player body with assets and a simple inventory/hotbar
    player = CharacterBody(assets)
    inventory = InventoryManager(initial=[1, 2, 3, 0, 0])
    player.inventory = inventory
    player.set_hotbar(inventory.hotbar)
    player.set_hotbar_index(inventory.index)
    player_input = PlayerInput(player)
    # transient UI messages (text, remaining_ms)
    ui_messages = []

    # register place end callback to show feedback
    def _on_place_end(result=None):
        if result:
            ui_messages.append(("Placed", 1200))
        else:
            ui_messages.append(("Can't place", 1200))

    try:
        player.register_place_end(_on_place_end)
    except Exception:
        pass

    # Slovník pre chunky: kľúč je (cx, cy)
    chunks = {}

    camera_scroll = [0, 0]

    # Koľko chunkov okolo hráča sa má vykresliť/generovať
    # 2 chunky na každú stranu (tj. cca 5x5 chunkov aktívnych)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                player_input.process_event(event)

        # --- Logika Nekonečného Sveta ---
        # Zistíme, v ktorom chunku je hráč
        player_cx = int(player.rect.centerx // (CHUNK_SIZE * TILE_SIZE))
        player_cy = int(player.rect.centery // (CHUNK_SIZE * TILE_SIZE))

        # Vygenerujeme chunky okolo hráča, ak ešte neexistujú
        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):  # trochu širšie do strán
                target_cx = player_cx + dx
                target_cy = player_cy + dy

                if (target_cx, target_cy) not in chunks:
                    chunks[(target_cx, target_cy)] = Chunk(target_cx, target_cy, tile_manager)

        # Update input & player
        player_input.update()
        dt = clock.get_time()
        player.update(chunks, dt_ms=dt)

        # Kamera
        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2
        camera_scroll[0] += (target_x - camera_scroll[0]) * 0.1
        camera_scroll[1] += (target_y - camera_scroll[1]) * 0.1

        # Vykresľovanie
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
        world_x = player.rect.centerx//32
        world_y = -player.rect.centery//32
        # UI
        info_text = (
            f"FPS: {int(clock.get_fps())} | "
            f"World: {world_x}, {world_y} | "
            f"Chunk: {player_cx}, {-player_cy} | "
            f"Seed: {SEED}"
        )
        screen.blit(pygame.font.SysFont("Arial", 18).render(info_text, True, (0, 0, 0)), (10, 10))

        # Hotbar UI (bottom-center)
        hotbar_slots = getattr(inventory, 'hotbar', [])
        slot_w = 48
        slot_h = 48
        total_w = slot_w * len(hotbar_slots)
        start_x = SCREEN_WIDTH // 2 - total_w // 2
        y = SCREEN_HEIGHT - slot_h - 10
        for i, item_id in enumerate(hotbar_slots):
            sx = start_x + i * slot_w
            rect = pygame.Rect(sx, y, slot_w - 4, slot_h - 4)
            pygame.draw.rect(screen, (200, 200, 200), rect)
            if i == inventory.index:
                pygame.draw.rect(screen, (255, 215, 0), rect, 3)
            # draw item icon if available
            if item_id and assets is not None:
                try:
                    icon = assets.textures[item_id][0]
                    icon_s = pygame.transform.scale(icon, (32, 32))
                    screen.blit(icon_s, (sx + 8, y + 8))
                except Exception:
                    pass

        # draw transient UI messages
        for i, (txt, ms) in enumerate(list(ui_messages)):
            font = pygame.font.SysFont('Arial', 20)
            surf = font.render(txt, True, (0, 0, 0))
            screen.blit(surf, (10, 40 + i * 22))
            # decrease timers
            ui_messages[i] = (txt, ms - clock.get_time())
        # remove expired
        ui_messages = [m for m in ui_messages if m[1] > 0]

        pygame.display.flip()
        # tick at end and allow dt usage above
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()