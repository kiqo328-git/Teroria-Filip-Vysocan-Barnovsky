import math
from settings import CHUNK_SIZE, SEED, FREQ, MULTIPLIER, BASE_HEIGHT, CAVE_THRESHOLD, CAVE_FREQ
from settings import MAX_CAVE_DEPTH, MAX_THRESHOLD_INCREASE, OCTAVES, LACUNARITY, GAIN
from settings import NPC_SPAWN_FREQ, NPC_SPAWN_THRESHOLD, MIN_NPC_DIST  # UPRAVENÝ IMPORT
import random
import numpy as np
from numba import njit


@njit(fastmath=True)
def smoothstep(t):
    """Kubické vyhladenie pre interpoláciu Value Noise."""
    return t * t * (3 - 2 * t)


@njit(fastmath=True)
def get_height_data(cx):
    heights = np.zeros(CHUNK_SIZE, dtype=np.float32)

    scale = 1.0 / FREQ

    for i in range(CHUNK_SIZE):
        world_x = cx * CHUNK_SIZE + i
        x0 = (world_x // scale) * scale
        x1 = x0 + scale

        # Posunutie seedu s každým volaním (ako ste žiadali)
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
def get_single_cave_noise(wx, wy, freq):
    """
    Vygeneruje 2D Value Noise (0.0 až 1.0) pre jednu oktávu.
    """
    scale = 1.0 / freq

    x0 = (wx // scale) * scale
    x1 = x0 + scale
    y0 = (wy // scale) * scale
    y1 = y0 + scale

    # Seed for 4 grid points - používame veľké prvočísla pre lepšiu distribúciu náhodných bodov
    s00 = int(SEED + x0 * 73856093 + y0 * 19349663)
    s10 = int(SEED + x1 * 73856093 + y0 * 19349663)
    s01 = int(SEED + x0 * 73856093 + y1 * 19349663)
    s11 = int(SEED + x1 * 73856093 + y1 * 19349663)

    # Get random values from seeds - Posun random seed pri každom volaní
    random.seed(s00)
    v00 = random.random()
    random.seed(s10)
    v10 = random.random()
    random.seed(s01)
    v01 = random.random()
    random.seed(s11)
    v11 = random.random()

    # Interpolation factors
    tx = (wx - x0) / scale
    ty = (wy - y0) / scale

    # Smooth the interpolation
    tx = smoothstep(tx)
    ty = smoothstep(ty)

    # Bilinear Interpolation (Lerp)
    v_top = v00 * (1 - tx) + v10 * tx
    v_bottom = v01 * (1 - tx) + v11 * tx

    noise_value = v_top * (1 - ty) + v_bottom * ty
    return noise_value


@njit(fastmath=True)
def get_fbm_cave_noise(wx, wy):
    """
    Vypočíta šum ako fraktálny Brownov pohyb (FBM) - simulácia Perlin-like noise.
    """
    total = 0.0
    amplitude = 1.0
    frequency = CAVE_FREQ
    max_value = 0.0  # Na normalizáciu výsledku do [0, 1]

    for i in range(OCTAVES):
        total += get_single_cave_noise(wx, wy, frequency) * amplitude
        max_value += amplitude
        amplitude *= GAIN
        frequency *= LACUNARITY

    # Normalizácia
    if max_value > 0.0:
        return total / max_value
    return 0.5


@njit(fastmath=True)
def get_npc_spawn_noise(wx):
    """
    Vygeneruje 1D Value Noise pre spawnovanie NPC na povrchu.
    """
    freq = NPC_SPAWN_FREQ
    scale = 1.0 / freq

    x0 = (wx // scale) * scale
    x1 = x0 + scale

    # Seed for 2 grid points (1D)
    s0 = int(SEED * 2 + x0 * 73856093)  # Použijeme iný násobiteľ pre odlišný vzor od jaskýň
    s1 = int(SEED * 2 + x1 * 73856093)

    random.seed(s0)
    v0 = random.random()
    random.seed(s1)
    v1 = random.random()

    # Interpolation factor
    t = (wx - x0) / scale
    t = smoothstep(t)

    noise_value = v0 * (1 - t) + v1 * t
    return noise_value


@njit(fastmath=True)
def generate_chunk_data(cx, cy, height_data):
    """
    Vygeneruje dáta pre chunk na súradniciach cx, cy.
    """
    layer_fg = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=np.int8)
    layer_bg = np.zeros((CHUNK_SIZE, CHUNK_SIZE), dtype=np.int8)
    npc_spawn_coords = []

    # NOVÉ: Lokálny manažment minimálnej vzdialenosti
    last_spawn_x = -1  # Lokálny stav pre X-súradnicu posledného spawnutého NPC

    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            # Globálne súradnice
            world_x = cx * CHUNK_SIZE + x
            world_y = cy * CHUNK_SIZE + y

            surface_level = int(height_data[x])

            # --- 1. NPC Spawnovanie (Iba na povrchu) ---
            if world_y == surface_level:
                npc_noise = get_npc_spawn_noise(world_x)

                # NOVÁ PODMIENKA: Ak je hluk dostatočne vysoký A NPC nebolo spawnuté v blízkej vzdialenosti
                if npc_noise > NPC_SPAWN_THRESHOLD and (world_x - last_spawn_x) >= MIN_NPC_DIST:

                    # Pre istotu, aby sa NPC spawnovalo len raz v bloku
                    if world_x > last_spawn_x:
                        npc_spawn_coords.append((world_x, world_y))
                        last_spawn_x = world_x

            # --- 2. Jaskyne (Procedurálny šum FBM s vplyvom hĺbky) ---

            # Hĺbka pod povrchom (0 na povrchu)
            depth = max(0.0, world_y - surface_level)

            # Výpočet koeficientu zväčšenia (0.0 až 1.0)
            scale = min(1.0, depth / MAX_CAVE_DEPTH)

            # Dynamický Prah (pre väčšie/častejšie jaskyne v hĺbke)
            current_threshold = CAVE_THRESHOLD + (MAX_THRESHOLD_INCREASE * scale)

            # Volanie noise funkcie FBM
            cave_val = get_fbm_cave_noise(world_x, world_y)

            # Ak je hodnota šumu nižšia ako prah, vytvoríme jaskyňu.
            is_cave = (cave_val < current_threshold)

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
                # Ak je to povrch, a nie je tu jaskyňa
                if not is_cave:
                    layer_fg[y][x] = 1  # Grass
                else:
                    layer_fg[y][x] = 0  # Vchod do jaskyne (Ak je na povrchu diera, je tam vzduch)

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

    return layer_fg, layer_bg, npc_spawn_coords