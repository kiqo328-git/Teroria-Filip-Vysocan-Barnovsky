import pygame
import math
from physics import check_collisions
from settings import TILE_SIZE, CHUNK_SIZE


class CharacterBody:
    def __init__(self, assets=None):
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
        # Placing blocks (one-shot)
        self.is_placing = False
        self.place_duration = 250
        self._place_timer = 0
        # Assets + hotbar
        self.assets = assets
        self.hotbar = []  # list of item ids (e.g., block ids)
        self.hotbar_index = 0
        self.inventory = None

        # Movement smoothing (Terraria-ish)
        self.accel = 0.6
        self.decel = 0.8
        self.max_speed = self.speed

        # Animation / timing
        self._time = 0
        # Callbacks for animation events (e.g., attack end)
        self._attack_end_cbs = []
        self._place_end_cbs = []
        self._mining_end_cbs = []
        self._prev_mining = False

    # --- External control API ---
    def set_move_input(self, x: float):
        self.move_input = x

    def trigger_jump(self):
        self.want_jump = True

    def trigger_attack(self):
        if not self.is_attacking:
            self.is_attacking = True
            self._attack_timer = self.attack_duration

    def register_attack_end(self, callback):
        """Register a callable to be invoked when an attack one-shot finishes."""
        if callable(callback):
            self._attack_end_cbs.append(callback)

    def register_place_end(self, callback):
        if callable(callback):
            self._place_end_cbs.append(callback)

    def trigger_place(self):
        if not self.is_placing:
            self.is_placing = True
            self._place_timer = self.place_duration

    def register_mining_end(self, callback):
        if callable(callback):
            self._mining_end_cbs.append(callback)

    def set_mining(self, v: bool):
        self.is_mining = v

    def set_hotbar(self, hotbar_list):
        self.hotbar = hotbar_list

    def set_hotbar_index(self, idx: int):
        if idx < 0:
            idx = 0
        if idx >= len(self.hotbar):
            idx = len(self.hotbar) - 1
        self.hotbar_index = idx
        # keep inventory in sync if present
        if hasattr(self, 'inventory') and self.inventory is not None:
            try:
                self.inventory.set_index(idx)
            except Exception:
                pass

    # Called every frame; `chunk_map` is passed through to collision checker
    def update(self, chunk_map, dt_ms: int = 16):
        # dt in milliseconds
        if dt_ms <= 0:
            dt_ms = 16
        dt = dt_ms / 1000.0

        # Horizontal movement smoothing towards target velocity
        target_vx = self.move_input * self.max_speed
        if abs(target_vx) > abs(self.velocity.x):
            # accelerate
            self.velocity.x += math.copysign(self.accel, target_vx - self.velocity.x)
        else:
            # decelerate toward target
            self.velocity.x += math.copysign(self.decel, target_vx - self.velocity.x)

        # clamp
        if abs(self.velocity.x) > self.max_speed:
            self.velocity.x = math.copysign(self.max_speed, self.velocity.x)

        # Jump (edge-triggered)
        if self.want_jump and self.grounded:
            self.velocity.y = self.jump_force
            self.grounded = False
        self.want_jump = False

        # Gravity
        self.velocity.y += self.gravity

        # Update facing (flip only when input directs)
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
                # fire callbacks
                for cb in list(self._attack_end_cbs):
                    try:
                        cb()
                    except Exception:
                        pass

        # placing timer
        if self.is_placing:
            self._place_timer -= dt_ms
            if self._place_timer <= 0:
                # perform placement and collect result
                result = False
                try:
                    result = self._do_place(chunk_map)
                except Exception:
                    result = False
                self.is_placing = False
                self._place_timer = 0
                for cb in list(self._place_end_cbs):
                    try:
                        # try calling with result arg, fall back to no-arg
                        cb(result)
                    except TypeError:
                        try:
                            cb()
                        except Exception:
                            pass
                    except Exception:
                        pass

        # mining end detection (transition True->False)
        if self._prev_mining and not self.is_mining:
            for cb in list(self._mining_end_cbs):
                try:
                    cb()
                except Exception:
                    pass
        self._prev_mining = self.is_mining

        # update time for animations
        self._time += dt

        # Collisions & position
        check_collisions(self, chunk_map)

    # Network-friendly state application
    def apply_state(self, state: dict):
        """Apply state received from network: expects keys like 'x','y','vx','vy','facing','is_attacking','is_mining'."""
        try:
            if 'x' in state and 'y' in state:
                self.rect.x = state['x']
                self.rect.y = state['y']
            if 'vx' in state:
                self.velocity.x = state['vx']
            if 'vy' in state:
                self.velocity.y = state['vy']
            if 'facing' in state:
                self.facing = state['facing']
            if 'is_attacking' in state:
                self.is_attacking = state['is_attacking']
            if 'is_mining' in state:
                self.is_mining = state['is_mining']
        except Exception:
            pass

    def _do_place(self, chunk_map):
        """Place selected hotbar item into the world in front of the player.

        This places a block into `layer_fg` of the target chunk if the tile is empty (0).
        """
        # determine selected item id
        item_id = None
        if hasattr(self, 'inventory') and self.inventory is not None:
            item_id = self.inventory.get_selected()
        elif 0 <= self.hotbar_index < len(self.hotbar):
            item_id = self.hotbar[self.hotbar_index]

        if not item_id or item_id == 0:
            return False

        # choose target tile in front of player (at mid height)
        dir_offset = (self.rect.width // 2 + 8) * (1 if self.facing >= 0 else -1)
        world_x = (self.rect.centerx + dir_offset)
        world_y = (self.rect.centery)

        tile_x = int(world_x // TILE_SIZE)
        tile_y = int(world_y // TILE_SIZE)

        # chunk coords and local indices
        cx = tile_x // CHUNK_SIZE
        cy = tile_y // CHUNK_SIZE
        bx = tile_x % CHUNK_SIZE
        by = tile_y % CHUNK_SIZE

        if (cx, cy) not in chunk_map:
            return False

        chunk = chunk_map[(cx, cy)]
        # ensure indices in range
        if by < 0 or by >= len(chunk.layer_fg) or bx < 0 or bx >= len(chunk.layer_fg[0]):
            return False

        # only place into empty tile
        if chunk.layer_fg[by][bx] == 0:
            chunk.layer_fg[by][bx] = item_id
            chunk.needs_update = True
            return True

        return False

    # Simple draw so existing rendering is preserved
    def draw(self, screen, camera_offset):
        draw_rect = pygame.Rect(
            self.rect.x - camera_offset[0],
            self.rect.y - camera_offset[1],
            self.rect.width,
            self.rect.height,
        )

        # Determine states for animation priority
        moving = abs(self.velocity.x) > 0.1

        # Determine hand angles (degrees)
        active_hand_angle = 35  # default hold angle
        inactive_hand_angle = 0

        # One-shot attack overrides
        if self.is_attacking:
            prog = 1.0 - (self._attack_timer / max(1, self.attack_duration))
            # swing from -60 (raised) to 30 (down) over progress
            active_hand_angle = (-60) + (90 * prog)
        elif self.is_mining:
            # loop - small oscillation
            active_hand_angle = 30 + math.sin(self._time * 20) * 15
        elif moving:
            active_hand_angle = 35 + math.sin(self._time * 8) * 6
            inactive_hand_angle = math.sin(self._time * 8) * 10
        else:
            active_hand_angle = 35
            inactive_hand_angle = 0

        # Draw order: back arm, back leg, body+head, front leg, front arm

        # Pivot-based limbs
        # Pivots relative to draw_rect
        shoulder_y = draw_rect.y + 12
        shoulder_x_left = draw_rect.x + 6
        shoulder_x_right = draw_rect.x + draw_rect.width - 6

        hip_y = draw_rect.y + draw_rect.height - 6
        hip_x_left = draw_rect.x + 6
        hip_x_right = draw_rect.x + draw_rect.width - 6

        # limb lengths
        arm_len = 22
        leg_len = 20

        # compute endpoints using angles
        def endpoint(px, py, angle_deg, length):
            a = math.radians(angle_deg)
            ex = px + math.cos(a) * length
            ey = py + math.sin(a) * length
            return (int(ex), int(ey))

        # Back arm (depends on facing)
        if self.facing >= 0:
            # facing right -> back arm is left shoulder
            back_sh_x, back_sh_y = shoulder_x_left, shoulder_y
            back_angle = inactive_hand_angle + 90  # down is 90deg
        else:
            back_sh_x, back_sh_y = shoulder_x_right, shoulder_y
            # when left-facing and active, push forward (sharper angle)
            back_angle = -active_hand_angle + 90

        back_hand = endpoint(back_sh_x, back_sh_y, back_angle, arm_len)
        pygame.draw.line(screen, (200, 150, 120), (back_sh_x, back_sh_y), back_hand, 6)
        pygame.draw.circle(screen, (180, 120, 90), back_hand, 4)

        # Back leg
        back_hip_x = hip_x_left if self.facing >= 0 else hip_x_right
        back_leg_angle = 100 + math.sin(self._time * 8) * (5 if moving else 2)
        back_foot = endpoint(back_hip_x, hip_y, back_leg_angle, leg_len)
        pygame.draw.line(screen, (100, 60, 40), (back_hip_x, hip_y), back_foot, 8)
        pygame.draw.circle(screen, (80, 40, 20), back_foot, 4)

        # Body + head
        pygame.draw.rect(screen, (255, 50, 50), draw_rect)
        pygame.draw.circle(screen, (255, 220, 180), (draw_rect.centerx, draw_rect.y + 8), 8)

        # Front leg
        front_hip_x = hip_x_right if self.facing >= 0 else hip_x_left
        front_leg_angle = 80 + math.sin(self._time * 8 + 1.0) * (8 if moving else 2)
        front_foot = endpoint(front_hip_x, hip_y, front_leg_angle, leg_len)
        pygame.draw.line(screen, (100, 60, 40), (front_hip_x, hip_y), front_foot, 8)
        pygame.draw.circle(screen, (80, 40, 20), front_foot, 4)

        # Front arm
        if self.facing >= 0:
            front_sh_x, front_sh_y = shoulder_x_right, shoulder_y
            front_angle = -active_hand_angle + 90
        else:
            front_sh_x, front_sh_y = shoulder_x_left, shoulder_y
            front_angle = inactive_hand_angle + 90

        front_hand = endpoint(front_sh_x, front_sh_y, front_angle, arm_len)
        pygame.draw.line(screen, (200, 150, 120), (front_sh_x, front_sh_y), front_hand, 6)
        pygame.draw.circle(screen, (180, 120, 90), front_hand, 4)

        # Eyes
        eye_offset_x = 6 if self.facing >= 0 else -6
        pygame.draw.circle(screen, (255, 255, 255), (draw_rect.centerx + eye_offset_x, draw_rect.y + 8), 3)
        pygame.draw.circle(screen, (255, 255, 255), (draw_rect.centerx - eye_offset_x, draw_rect.y + 8), 3)

        # Determine selected item
        item_id = None
        if hasattr(self, 'inventory') and self.inventory is not None:
            item_id = self.inventory.get_selected()
        elif 0 <= self.hotbar_index < len(self.hotbar):
            item_id = self.hotbar[self.hotbar_index]

        # Place held item at active hand end with rotation
        if item_id and self.assets is not None:
            try:
                sprite = self.assets.textures[item_id][0]
                sprite_s = pygame.transform.scale(sprite, (20, 20))

                if self.facing >= 0:
                    hand_pos = front_hand
                    hand_angle = -active_hand_angle
                else:
                    # when facing left, active is back hand (which we computed as back_hand)
                    hand_pos = back_hand
                    hand_angle = active_hand_angle

                rotated = pygame.transform.rotate(sprite_s, hand_angle)
                rrect = rotated.get_rect(center=hand_pos)
                screen.blit(rotated, rrect.topleft)
            except Exception:
                pass
