import pygame
from numba import njit
from settings import CHUNK_SIZE, TILE_SIZE, CURRENT_PLAYER_REACH


# --- NUMBA FUNKCIA ---
# Definujeme ju tu, aby sme nemuseli importovať z main (čo by spôsobilo chybu)
@njit(fastmath=True)
def is_player_near_block(px, py, bx, by, reach):
    dx = px - bx
    dy = py - by
    return (dx * dx + dy * dy) <= (reach * reach)


class PlayerInput:
    def __init__(self, player):
        self.player = player
        self.clicking = False

    def update(self, dt, camera_scroll, chunks):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()

        # --- POHYB ---
        self.player.set_player_velocity_x(0)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.player.get_facing() is not False:
                self.player.update_rotation(False)
            self.player.set_player_velocity_x(-1 * dt)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.player.get_facing() is not True:
                self.player.update_rotation(True)
            self.player.set_player_velocity_x(1 * dt)

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.player.grounded:
            self.player.jump()

        # --- INTERAKCIA MYŠOU ---
        # Získame svetové súradnice myši
        wmx, wmy = self.get_mouse_world_pos(camera_scroll)

        if mouse_buttons[0]:
            if not self.clicking:
                # Výpočet indexu chunku
                target_cx = int(wmx // (CHUNK_SIZE * TILE_SIZE))
                target_cy = int(wmy // (CHUNK_SIZE * TILE_SIZE))

                chunk_key = (target_cx, target_cy)

                # Získame stred hráča (používame rect, je to spoľahlivejšie)
                p_center_x,p_center_y = self.player.get_player_pos()

                # --- OPRAVA PODMIENKY ---
                # 1. Kontrolujeme či chunk existuje
                # 2. Voláme funkciu so SVETOVÝMI súradnicami (wmx, wmy), nie s chunk indexmi
                if chunk_key in chunks:
                    if is_player_near_block(p_center_x, p_center_y, wmx, wmy, float(CURRENT_PLAYER_REACH)):

                        destroyed_id = chunks[chunk_key].destroy_block_at(wmx, wmy)
                        if destroyed_id != 0:
                            print(f"Zniceny blok ID: {destroyed_id}")
                    else:
                        # (Voliteľné) Tu môžeš dať print, že je hráč príliš ďaleko
                        pass

                # self.clicking = True # Odkomentuj, ak nechceš automatickú streľbu
        else:
            self.clicking = False

    def get_mouse_world_pos(self, camera_scroll):
        mx, my = pygame.mouse.get_pos()
        wx = mx + camera_scroll[0]
        wy = my + camera_scroll[1]
        return wx, wy