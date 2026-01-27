import pygame
from settings import PLAYER_SCALE


class BodyPart(pygame.sprite.Sprite):
    def __init__(self, image_path, scale):
        super().__init__()
        try:
            original_image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            original_image = pygame.Surface((20, 60))
            original_image.fill((255, 0, 0))
        w = original_image.get_width()
        h = original_image.get_height()
        self.image = pygame.transform.scale(original_image, (int(w * scale), int(h * scale)))
        self.rect = self.image.get_rect()


class Body(BodyPart):
    def __init__(self, scale, path): super().__init__(path, scale)


class Leg(BodyPart):
    def __init__(self, scale, path): super().__init__(path, scale)


class Head(BodyPart):
    def __init__(self, scale, path): super().__init__(path, scale)


class Arm(BodyPart):
    def __init__(self, scale, path): super().__init__(path, scale)


class CharacterBody:
    def __init__(self, x, y, scale, skin, isLocal=True):
        self.scale = scale
        self.facing_right = False

        # --- HITBOX ---
        # Tento Rect definuje fyzické telo.
        # Ak je nastavený správne (výška 56), tak pri kolíziách v physics.py
        # sa bude kontrolovať priestor od nôh až po hlavu.
        collider_width = 50 * scale
        collider_height = 160 * scale

        self.rect = pygame.Rect(x, y, int(collider_width), int(collider_height))
        self.rect.center = (x, y)

        if isLocal:
            self.velocity = pygame.math.Vector2(0, 0)
            self.speed = 350
            self.jump_force = -12
            self.gravity = 0.5  # Iba hodnota, logiku rieši physics.py
            self.max_gravity = 15  # Iba hodnota
            self.grounded = False

        self.sprites = pygame.sprite.Group()
        self.torso = Body(scale, skin["body"])
        self.head = Head(scale, skin["head"])
        self.back_leg = Leg(scale, skin["leg"])
        self.front_leg = Leg(scale, skin["leg"])
        self.back_arm = Arm(scale, skin["arm"])
        self.front_arm = Arm(scale, skin["arm"])

        self.sprites.add(self.back_arm)
        self.sprites.add(self.back_leg)
        self.sprites.add(self.torso)
        self.sprites.add(self.head)
        self.sprites.add(self.front_leg)
        self.sprites.add(self.front_arm)

        self.sync_sprites_to_collider()

    def sync_sprites_to_collider(self):
        """Prilepí obrázky na hitbox (rect)"""
        self.torso.rect.center = self.rect.center
        center_x = self.torso.rect.centerx
        legs_y_pos = self.torso.rect.bottom

        self.back_leg.rect.midtop = (center_x, legs_y_pos)
        self.front_leg.rect.midtop = (center_x, legs_y_pos)
        self.head.rect.midbottom = self.torso.rect.midtop

        shoulder_y = self.torso.rect.top + (6 * self.scale)
        shoulder_offset = 2 * self.scale
        if not self.facing_right:
            shoulder_x = center_x - shoulder_offset
        else:
            shoulder_x = center_x + shoulder_offset
        shoulder_pos = (shoulder_x, shoulder_y)

        self.back_arm.rect.midtop = shoulder_pos
        self.front_arm.rect.midtop = shoulder_pos

    def flip(self):
        for sprite in self.sprites:
            sprite.image = pygame.transform.flip(sprite.image, True, False)
        self.sync_sprites_to_collider()

    def update_rotation(self, facing_right):
        if self.facing_right != facing_right:
            self.flip()
            self.facing_right = facing_right

    def get_facing(self):
        return self.facing_right

    def set_player_velocity_x(self, velocity_input):
        self.velocity.x = velocity_input * self.speed

    def jump(self):
        self.velocity.y = self.jump_force
        self.grounded = False

    def update(self):
        # Iba synchronizácia vizuálu
        self.sync_sprites_to_collider()
        self.sprites.update()

    def draw(self, screen, camera_scroll=[0, 0]):
        # Debug Hitbox (ak chceš vidieť či sedia nohy a hlava)
        # debug_rect = self.rect.copy()
        # debug_rect.x -= camera_scroll[0]
        # debug_rect.y -= camera_scroll[1]
        # pygame.draw.rect(screen, (0, 255, 0), debug_rect, 1)

        for sprite in self.sprites:
            offset_pos = (
                sprite.rect.x - camera_scroll[0],
                sprite.rect.y - camera_scroll[1]
            )
            screen.blit(sprite.image, offset_pos)