import pygame
from physics import check_collisions


class CharacterBody:
    def __init__(self):
        self.rect = pygame.Rect(0, -100, 24, 56)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 6
        self.jump_force = -12
        self.gravity = 0.5
        self.grounded = False

        # Input/state (externally set)
        self.move_input = 0.0
        self.want_jump = False

        # Facing: 1 = right, -1 = left
        self.facing = 1

        # Action booleans
        self.is_attacking = False
        self.attack_duration = 300  # ms
        self._attack_timer = 0

        self.is_mining = False

    # --- External control API ---
    def set_move_input(self, x: float):
        self.move_input = x

    def trigger_jump(self):
        self.want_jump = True

    def trigger_attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self._attack_timer = self.attack_duration

    def set_mining(self, v: bool):
        self.is_mining = v

    # Called every frame; `chunk_map` is passed through to collision checker
    def update(self, chunk_map, dt_ms: int = 16):
        # Horizontal movement
        self.velocity.x = self.move_input * self.speed

        # Jump (edge-triggered)
        if self.want_jump and self.grounded:
            self.velocity.y = self.jump_force
            self.grounded = False
        self.want_jump = False

        # Gravity
        self.velocity.y += self.gravity

        # Update facing
        if self.move_input > 0:
            self.facing = 1
        elif self.move_input < 0:
            self.facing = -1

        # Update one-shot attack timer
        if self.is_attacking:
            self._attack_timer -= dt_ms
            if self._attack_timer <= 0:
                self.is_attacking = False
                self._attack_timer = 0

        # Collisions & position
        check_collisions(self, chunk_map)

    # Simple draw so existing rendering is preserved
    def draw(self, screen, camera_offset):
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height,
        )
        pygame.draw.rect(screen, (255, 50, 50), draw_rect)
        # Eyes (flip based on facing)
        if self.facing >= 0:
            eye_x = draw_rect.x + 14
            eye_x2 = draw_rect.x + 4
        else:
            eye_x = draw_rect.x + 4
            eye_x2 = draw_rect.x + 14

        pygame.draw.rect(screen, (255, 255, 255), (eye_x2, draw_rect.y + 8, 6, 6))
        pygame.draw.rect(screen, (255, 255, 255), (eye_x, draw_rect.y + 8, 6, 6))
