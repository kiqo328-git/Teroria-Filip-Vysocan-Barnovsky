import pygame
from settings import TILE_SIZE, CHUNK_SIZE
from world_gen import generate_chunk_data, get_height_data

class Chunk:
    def __init__(self, cx, cy, tile_manager):
        self.cx = cx
        self.cy = cy
        self.tile_manager = tile_manager

        self.surface_heights = get_height_data(cx)
        # ZMENA: generate_chunk_data teraz vracia aj npc_spawn_coords
        self.layer_fg, self.layer_bg, self.npc_spawn_coords = generate_chunk_data(cx, cy, self.surface_heights)

        self.image = pygame.Surface((CHUNK_SIZE * TILE_SIZE, CHUNK_SIZE * TILE_SIZE))
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = cx * CHUNK_SIZE * TILE_SIZE
        self.rect.y = cy * CHUNK_SIZE * TILE_SIZE

        self.needs_update = True

    def is_in_chunk(self, world_x, world_y):
        return self.rect.collidepoint(world_x, world_y)

    def get_block_at(self, world_x, world_y):
        local_x = int((world_x - self.rect.x) // TILE_SIZE)
        local_y = int((world_y - self.rect.y) // TILE_SIZE)

        if 0 <= local_x < CHUNK_SIZE and 0 <= local_y < CHUNK_SIZE:
            return self.layer_fg[local_y][local_x]
        return 0

    def destroy_block_at(self, world_x, world_y):
        local_x = int((world_x - self.rect.x) // TILE_SIZE)
        local_y = int((world_y - self.rect.y) // TILE_SIZE)

        if 0 <= local_x < CHUNK_SIZE and 0 <= local_y < CHUNK_SIZE:
            block_id = self.layer_fg[local_y][local_x]

            if block_id != 0 and block_id != 4:
                self.layer_fg[local_y][local_x] = 0
                self.needs_update = True
                return block_id

        return 0

    def render(self):
        if not self.needs_update:
            return

        self.image.fill((0, 0, 0))

        for y in range(CHUNK_SIZE):
            for x in range(CHUNK_SIZE):
                world_x = self.cx * CHUNK_SIZE + x
                world_y = self.cy * CHUNK_SIZE + y
                hash_val = (abs(world_x) * 73856093) ^ (abs(world_y) * 19349663)

                pos_x = x * TILE_SIZE
                pos_y = y * TILE_SIZE

                # Pozadie
                bg_id = self.layer_bg[y][x]
                if bg_id != 0:
                    tex = self.tile_manager.get_texture(bg_id, hash_val, True)
                    if tex: self.image.blit(tex, (pos_x, pos_y))

                # Popredie
                fg_id = self.layer_fg[y][x]
                if fg_id != 0:
                    tex = self.tile_manager.get_texture(fg_id, hash_val, False)
                    if tex: self.image.blit(tex, (pos_x, pos_y))

        self.needs_update = False

    def draw(self, screen, camera_offset):
        if self.needs_update:
            self.render()

        screen_pos = (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1])
        screen_rect = screen.get_rect()

        if screen_rect.colliderect(pygame.Rect(screen_pos[0], screen_pos[1], self.rect.width, self.rect.height)):
            screen.blit(self.image, screen_pos)