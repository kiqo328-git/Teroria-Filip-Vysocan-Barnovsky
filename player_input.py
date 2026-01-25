import pygame


class PlayerInput:
    def __init__(self, body):
        self.body = body
        self._prev_keys = pygame.key.get_pressed()

    def process_event(self, event):
        # Mouse wheel hotbar change
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # scroll up
                # scroll up -> -1 (wrap handled in InventoryManager)
                if hasattr(self.body, 'hotbar') and hasattr(self.body, 'hotbar_index'):
                    # If CharacterBody uses InventoryManager, call its scroll
                    try:
                        # prefer an InventoryManager on the body if present
                        if hasattr(self.body, 'inventory') and self.body.inventory is not None:
                            self.body.inventory.scroll(-1)
                            self.body.set_hotbar_index(self.body.inventory.index)
                        else:
                            new_i = max(0, self.body.hotbar_index - 1)
                            self.body.set_hotbar_index(new_i)
                    except Exception:
                        pass
            elif event.button == 5:  # scroll down
                try:
                    if hasattr(self.body, 'inventory') and self.body.inventory is not None:
                        self.body.inventory.scroll(1)
                        self.body.set_hotbar_index(self.body.inventory.index)
                    else:
                        new_i = self.body.hotbar_index + 1
                        self.body.set_hotbar_index(new_i)
                except Exception:
                    pass

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

        # Place block: Q key (one-shot)
        if (keys[pygame.K_q] and not self._prev_keys[pygame.K_q]):
            if hasattr(self.body, 'trigger_place'):
                self.body.trigger_place()

        # Mining: hold E
        self.body.set_mining(keys[pygame.K_e])

        self._prev_keys = keys
