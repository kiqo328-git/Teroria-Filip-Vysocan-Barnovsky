import pygame


class PlayerInput:
    def __init__(self, body):
        self.body = body
        self._prev_keys = pygame.key.get_pressed()
        self.hotbar_index = 0

    def process_event(self, event):
        # Mouse wheel hotbar change
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # scroll up
                self.hotbar_index = max(0, self.hotbar_index - 1)
            elif event.button == 5:  # scroll down
                self.hotbar_index = self.hotbar_index + 1

    def update(self):
        keys = pygame.key.get_pressed()

        move = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move = 1
        self.body.set_move_input(move)

        # Jump: detect rising edge
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and not (
            self._prev_keys[pygame.K_SPACE] or self._prev_keys[pygame.K_w]
        ):
            self.body.trigger_jump()

        # Attack: rising edge on F
        if keys[pygame.K_f] and not self._prev_keys[pygame.K_f]:
            self.body.trigger_attack()

        # Mining: hold E
        self.body.set_mining(keys[pygame.K_e])

        self._prev_keys = keys
