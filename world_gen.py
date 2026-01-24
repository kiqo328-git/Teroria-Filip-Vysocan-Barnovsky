import math
from settings import CHUNK_SIZE
from numba import njit

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
def generate_chunk_data(cx, cy):
    """
    Vygeneruje dáta pre chunk na súradniciach cx, cy.
    """
    layer_fg = [[0] * CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    layer_bg = [[0] * CHUNK_SIZE for _ in range(CHUNK_SIZE)]

    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            # Globálne súradnice
            world_x = cx * CHUNK_SIZE + x
            world_y = cy * CHUNK_SIZE + y

            # --- 1. Povrch Terénu (Hory a doliny) ---
            # Použijeme viac sínusoviek pre zaujímavejší terén
            base_height = math.sin(world_x * 0.05) * 10  # Veľké kopce
            detail_height = math.sin(world_x * 0.2) * 2  # Malé hrbolčeky

            # Hladina zeme (Surface Level)
            # +10 posunie zem nižšie, aby sme mali miesto na hlavou
            surface_level = int(base_height + detail_height + 12)

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
                # Tráva (ak to nie je vchod do jaskyne)
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
                    elif world_y > surface_level + 40:
                        layer_fg[y][x] = 4  # Bedrock (úplne dole, ak chceš dno)
                    else:
                        layer_fg[y][x] = 2  # Stone

    return layer_fg, layer_bg