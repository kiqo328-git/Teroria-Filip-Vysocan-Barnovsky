import pygame
from settings import PLAYER_SCALE, NPC_INTERACT_RANGE, TILE_SIZE, CURRENT_PLAYER_REACH,CHUNK_SIZE
from calculation import is_player_near_block


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

        collider_width = 50 * scale
        collider_height = 160 * scale

        self.rect = pygame.Rect(x, y, int(collider_width), int(collider_height))
        self.rect.center = (x, y)

        if isLocal:
            self.velocity = pygame.math.Vector2(0, 0)
            self.speed = 350
            self.jump_force = -12
            self.gravity = 0.5
            self.max_gravity = 15
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

        for sprite in self.sprites:
            offset_pos = (
                sprite.rect.x - camera_scroll[0],
                sprite.rect.y - camera_scroll[1]
            )
            screen.blit(sprite.image, offset_pos)

    def destroy_block(self, xPos, yPos, chunks):
        tile_col = int(xPos // TILE_SIZE)
        tile_row = int(yPos // TILE_SIZE)

        block_center_x = (tile_col * TILE_SIZE) + (TILE_SIZE / 2)
        block_center_y = (tile_row * TILE_SIZE) + (TILE_SIZE / 2)

        target_cx = int(block_center_x // (CHUNK_SIZE * TILE_SIZE))
        target_cy = int(block_center_y // (CHUNK_SIZE * TILE_SIZE))

        chunk_key = (target_cx, target_cy)

        p_center_x, p_center_y = self.get_player_pos()

        if chunk_key in chunks:
            if is_player_near_block(p_center_x, p_center_y, block_center_x, block_center_y,
                                    float(CURRENT_PLAYER_REACH)):

                destroyed_id = chunks[chunk_key].destroy_block_at(block_center_x, block_center_y)

                if destroyed_id != 0:
                    pass
                    #print(f"Zniceny blok ID: {destroyed_id}")
            else:
                pass

    def get_player_pos(self):
        return (self.rect.centerx, self.rect.centery)


# --- NOVÁ TRIEDA NPC ---
class NPC(CharacterBody):
    def __init__(self, x, y, scale, skin, name="Obchodník"):
        # NPC je nehybné, nepotrebuje fyziku (isLocal=False)
        super().__init__(x, y, scale, skin, isLocal=False)
        self.name = name
        self.is_interactable = True
        self.interaction_range = NPC_INTERACT_RANGE

    def update(self, player_rect):
        """NPC logiku riadi main.py, vrátane otáčania k hráčovi."""
        self.sync_sprites_to_collider()
        self.face_target(player_rect)
        self.sprites.update()

    def face_target(self, target_rect):
        """Otáča NPC smerom k hráčovi (target_rect)."""
        player_x = target_rect.centerx
        npc_x = self.rect.centerx

        # Určí, ktorým smerom je hráč
        facing_right_new = player_x > npc_x

        # Ak sa smer zmenil, otočí vizuál
        if self.facing_right != facing_right_new:
            self.flip()
            self.facing_right = facing_right_new

    def interact(self):
        """Logika interakcie s NPC (simulácia)."""
        return f"NPC {self.name}: Ahoj, svetobežník! Chceš niečo kúpiť?"

    def is_player_in_range(self, player_center_pos):
        """Kontroluje, či je hráč v dosahu interakcie."""
        px, py = player_center_pos
        dx = self.rect.centerx - px
        dy = self.rect.centery - py
        # Používame vzdialenosť (na druhú) pre rýchlejší výpočet bez odmocniny
        return (dx * dx + dy * dy) <= (self.interaction_range * self.interaction_range)