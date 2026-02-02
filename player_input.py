import pygame
from settings import CHUNK_SIZE, TILE_SIZE, CURRENT_PLAYER_REACH


class PlayerInput:
    def __init__(self, player):
        self.player = player
        self.clicking = False

    def update(self, dt, camera_scroll, chunks):
        keys = pygame.key.get_pressed()

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

    def get_mouse_world_pos(self, camera_scroll):
        mx, my = pygame.mouse.get_pos()
        wx = mx + camera_scroll[0]
        wy = my + camera_scroll[1]
        return wx, wy