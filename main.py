import pygame
import sys
from settings import *
from assets import AssetManager
from tile_manager import TileManager
from chunk import Chunk
from physics import check_collisions


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
    player = Player()

    # Slovník pre chunky: kľúč je (cx, cy)
    chunks = {}

    camera_scroll = [0, 0]

    # Koľko chunkov okolo hráča sa má vykresliť/generovať
    # 2 chunky na každú stranu (tj. cca 5x5 chunkov aktívnych)
    RENDER_DISTANCE = 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

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

        # Update hráča
        player.update()
        check_collisions(player, chunks)

        # Kamera
        target_x = player.rect.centerx - SCREEN_WIDTH // 2
        target_y = player.rect.centery - SCREEN_HEIGHT // 2
        camera_scroll[0] += (target_x - camera_scroll[0]) * 0.1
        camera_scroll[1] += (target_y - camera_scroll[1]) * 0.1

        # Vykresľovanie
        screen.fill(SKY_COLOR)

        # Vykresliť len viditeľné chunky (optimalizácia)
        # Prejdeme slovník, ale vykreslíme len tie blízko hráča
        for dy in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dx in range(-RENDER_DISTANCE - 1, RENDER_DISTANCE + 2):
                cx = player_cx + dx
                cy = player_cy + dy
                if (cx, cy) in chunks:
                    chunks[(cx, cy)].draw(screen, camera_scroll)

        player.draw(screen, camera_scroll)

        # UI
        info_text = f"FPS: {int(clock.get_fps())} | Chunk: {player_cx}, {player_cy}"
        screen.blit(pygame.font.SysFont("Arial", 18).render(info_text, True, (0, 0, 0)), (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()