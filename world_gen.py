import math
import random
from settings import CHUNK_SIZE


def generate_chunk_data(cx, cy, seed=12345):
    """
    Vygeneruje dáta pre jeden chunk (16x16).
    Vráti dve polia: layer_fg (popredie) a layer_bg (pozadie).
    """
    layer_fg = [[0] * CHUNK_SIZE for _ in range(CHUNK_SIZE)]
    layer_bg = [[0] * CHUNK_SIZE for _ in range(CHUNK_SIZE)]

    for y in range(CHUNK_SIZE):
        for x in range(CHUNK_SIZE):
            # Prepočet na globálne súradnice sveta
            world_x = cx * CHUNK_SIZE + x
            world_y = cy * CHUNK_SIZE + y

            # --- 1. Terén (Povrch) ---
            # Použijeme sínusovku na vytvorenie kopcov
            # world_x * 0.1 určuje šírku kopcov
            # * 10 určuje výšku kopcov
            # + 15 posúva zem nižšie (aby nebola úplne hore na obrazovke)
            height_val = math.sin(world_x * 0.1) * 8 + 15
            surface_level = int(height_val)

            # --- 2. Jaskyne (Noise) ---
            # Jednoduchý pseudo-náhodný šum pre diery v zemi
            random.seed(world_x * 49297 + world_y * 93821 + seed)
            cave_noise = random.random()  # Číslo od 0.0 do 1.0

            # --- 3. Rozhodovanie o bloku ---

            # --- POZADIE (BACKGROUND) ---
            # Pozadie chceme všade pod úrovňou terénu (aby v jaskyni nebolo vidieť oblohu)
            if world_y >= surface_level:
                if world_y < surface_level + 5:
                    layer_bg[y][x] = 3  # Dirt (Hlina)
                else:
                    layer_bg[y][x] = 2  # Stone (Kameň)
            else:
                layer_bg[y][x] = 0  # Vzduch (nad zemou)

            # --- POPREDIE (FOREGROUND) ---
            if world_y < surface_level:
                # Nad zemou
                layer_fg[y][x] = 0  # Air

            elif world_y == surface_level:
                # Tráva (len ak tam nie je jaskyňa)
                if cave_noise < 0.8:
                    layer_fg[y][x] = 1  # Grass
                else:
                    layer_fg[y][x] = 0  # Diera na povrchu

            else:
                # Pod zemou
                if cave_noise > 0.8:
                    # Jaskyňa (Vzduch v popredí, ale pozadie ostáva)
                    layer_fg[y][x] = 0
                else:
                    # Pevná zem
                    if world_y < surface_level + 5:
                        layer_fg[y][x] = 3  # Dirt
                    elif world_y > surface_level + 50:
                        layer_fg[y][x] = 4  # Bedrock (veľmi hlboko)
                    else:
                        layer_fg[y][x] = 2  # Stone

    return layer_fg, layer_bg