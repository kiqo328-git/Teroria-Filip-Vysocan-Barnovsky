import pygame
from settings import BLOCKS



class TileManager:
    def __init__(self, asset_manager):
        self.assets = asset_manager

    def get_texture(self, block_id, variant_hash, is_background):
        """
        Vráti Surface textúry.
        variant_hash: Číslo (napr. súradnica), ktoré určí, ktorý variant sa použije.
        is_background: Ak True, vráti stmavnutú verziu.
        """
        if block_id == 0:
            return None

        block_info = BLOCKS.get(block_id)
        if not block_info:
            return None

        # Výber variantu pomocou modula
        # Napr. ak má kameň 3 varianty a hash je 10, vyberie variant 10 % 3 = 1
        count = block_info["variants"]
        variant_index = variant_hash % count

        if is_background:
            return self.assets.dark_textures[block_id][variant_index]
        else:
            return self.assets.textures[block_id][variant_index]