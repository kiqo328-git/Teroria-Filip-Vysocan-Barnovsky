import pygame


class PlayerInput:
    def __init__(self, player):
        self.player = player

    def update(self, dt):
        keys = pygame.key.get_pressed()

        # Reset X velocity pred spracovaním vstupu
        self.player.set_player_velocity_x(0)

        # Aplikovanie Delta Time do vstupu (ako si chcel)
        # dt je čas v sekundách (napr. 0.016 pri 60 FPS)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.player.get_facing() is not False:
                self.player.update_rotation(False)

            # Násobíme -1 * dt
            self.player.set_player_velocity_x(-1 * dt)

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.player.get_facing() is not True:
                self.player.update_rotation(True)

            # Násobíme 1 * dt
            self.player.set_player_velocity_x(1 * dt)

        # Skok - kontrolujeme self.player.grounded
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.player.grounded:
            self.player.jump()