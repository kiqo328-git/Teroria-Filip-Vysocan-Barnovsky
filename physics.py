import pygame
from settings import TILE_SIZE, CHUNK_SIZE


# from tile_manager import BLOCKS # Odkomentuj, ak máš BLOCKS definované inde, alebo použi provizórne:

# Provizórna definícia, ak ju nemáš importovanú
def get_block_solidity(block_id):
    # Tu vráť True, ak je blok pevný (kameň, hlina), False ak je vzduch/voda
    # Príklad: Vzduch je 0
    return block_id != 0


def apply_physics(player, chunks):
    """
    Rieši gravitáciu, pohyb a kolízie s chunkmi.
    """

    # --- 1. GRAVITÁCIA ---
    # Aplikujeme gravitáciu priamo tu
    player.velocity.y += player.gravity

    # Maximálna rýchlosť pádu (aby nepreletel cez podlahu pri obrovskej rýchlosti)
    if player.velocity.y > player.max_gravity:
        player.velocity.y = player.max_gravity

    # Pomocná funkcia na zistenie, či je na daných súradniciach pevný blok
    def is_solid(x, y):
        cx = x // CHUNK_SIZE
        cy = y // CHUNK_SIZE
        bx = x % CHUNK_SIZE
        by = y % CHUNK_SIZE

        if (cx, cy) in chunks:
            chunk = chunks[(cx, cy)]
            # Predpokladáme, že chunk má layer_fg (popredie) s ID blokov
            # Ak používaš iný systém ukladania, uprav tento riadok:
            try:
                block_id = chunk.layer_fg[by][bx]
                # Použijeme tvoj systém na zistenie, či je blok solid
                # return BLOCKS[block_id]["solid"]
                return get_block_solidity(block_id)
            except IndexError:
                return False
        return False

    # --- 2. POHYB X (Do strán) ---
    player.rect.x += player.velocity.x

    # Výpočet rozsahov dlaždíc, ktoré hráč pretína
    # Tieto vzorce zabezpečia, že kontrolujeme celú šírku a výšku hráča
    start_x = int(player.rect.left // TILE_SIZE) - 1
    end_x = int(player.rect.right // TILE_SIZE) + 1
    start_y = int(player.rect.top // TILE_SIZE) - 1
    end_y = int(player.rect.bottom // TILE_SIZE) + 1

    for y in range(start_y, end_y + 1):
        for x in range(start_x, end_x + 1):
            if is_solid(x, y):
                tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player.rect.colliderect(tile_rect):
                    if player.velocity.x > 0:  # Išiel doprava -> narazil pravou stranou
                        player.rect.right = tile_rect.left
                        player.velocity.x = 0
                    elif player.velocity.x < 0:  # Išiel doľava -> narazil ľavou stranou
                        player.rect.left = tile_rect.right
                        player.velocity.x = 0

    # --- 3. POHYB Y (Hore/Dole) ---
    player.rect.y += player.velocity.y
    player.grounded = False  # Predpokladáme, že padáme, kým nenarazíme na zem

    # Musíme prepočítať mriežku, lebo sme sa pohli po Y
    start_x = int(player.rect.left // TILE_SIZE) - 1
    end_x = int(player.rect.right // TILE_SIZE) + 1
    start_y = int(player.rect.top // TILE_SIZE) - 1
    end_y = int(player.rect.bottom // TILE_SIZE) + 1

    for y in range(start_y, end_y + 1):
        for x in range(start_x, end_x + 1):
            if is_solid(x, y):
                tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if player.rect.colliderect(tile_rect):
                    if player.velocity.y > 0:  # Padal dole -> narazil nohami
                        player.rect.bottom = tile_rect.top
                        player.velocity.y = 0
                        player.grounded = True  # Stojíme na zemi
                    elif player.velocity.y < 0:  # Skákal hore -> narazil hlavou
                        player.rect.top = tile_rect.bottom
                        player.velocity.y = 0