import math
from settings import CHUNK_SIZE, SEED, FREQ, MULTIPLIER, BASE_HEIGHT
import random
import numpy as np
from numba import njit

@njit(fastmath=True)
def get_height_data(cx):
    heights = np.zeros(CHUNK_SIZE, dtype=np.float32)

    scale = 1.0 / FREQ

    for i in range(CHUNK_SIZE):
        world_x = cx * CHUNK_SIZE + i
        x0 = (world_x // scale) * scale
        x1 = x0 + scale

        random.seed(int(SEED + x0))
        v0 = random.random()

        random.seed(int(SEED + x1))
        v1 = random.random()

        t = (world_x - x0) / scale

        t = t * t * (3 - 2 * t)

        noise_value = v0 * (1 - t) + v1 * t

        heights[i] = noise_value * MULTIPLIER + BASE_HEIGHT

    return heights

@njit(fastmath=True)
def get_cave_noise(wx, wy):
    """
    Vytvorí 'hustotu' materiálu na danej súradnici pomocou sínusov.
    Ak je hodnota nízka, vznikne jaskyňa.
    """
    # Kombinácia vĺn s rôznou frekvenciou pre organický tvar
    # 0.05 určuje veľkosť jaskýň, 0.5 určuje "šum"
    val = math.sin(wx * 0.06) + math.cos(wy * 0.06)
    val += math.sin(wx * 0.15 + wy * 0.15) * 0.4
    return val

@njit(fastmath=True)
def generate_chunk_data(cx, cy, height_data):
    """
    Vygeneruje dáta pre chunk na súradniciach cx, cy.
    """
    layer_fg = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=np.int8)
    layer_bg = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=np.int8)

    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            # Globálne súradnice
            world_x = cx * CHUNK_SIZE + x
            world_y = cy * CHUNK_SIZE + y

            surface_level = int(height_data[x])

            # --- 2. Jaskyne (Matematické tunely) ---
            cave_val = get_cave_noise(world_x, world_y)
            # Ak je cave_val < -0.8, vznikne diera (jaskyňa)
            is_cave = (cave_val < -0.8)

            # --- 3. Osádzanie Blokov ---

            # -- POZADIE (Vždy vyplnené pod úrovňou terénu) --
            if world_y >= surface_level:
                # Tesne pod povrchom hlina, hlbšie kameň
                if world_y < surface_level + 5:
                    layer_bg[y][x] = 3  # Dirt
                else:
                    layer_bg[y][x] = 2  # Stone
            else:
                layer_bg[y][x] = 0  # Vzduch

            # -- POPREDIE (Pevné bloky) --
            if world_y < surface_level:
                layer_fg[y][x] = 0  # Vzduch nad zemou

            elif world_y == surface_level:
                if not is_cave:
                    layer_fg[y][x] = 1  # Grass
                else:
                    layer_fg[y][x] = 0  # Vchod do jaskyne

            else:
                # Pod zemou
                if is_cave:
                    layer_fg[y][x] = 0  # Jaskyňa (vzduch)
                else:
                    # Pevná hmota
                    if world_y < surface_level + 5:
                        layer_fg[y][x] = 3  # Dirt
                    elif world_y > surface_level + 500:
                        layer_fg[y][x] = 4  # Bedrock
                    else:
                        layer_fg[y][x] = 2  # Stone

    return layer_fg, layer_bg