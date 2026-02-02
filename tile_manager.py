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

        # Získame zoznam načítaných textúr z AssetManager
        # Ak blok neexistuje v assets (napr. vzduch alebo chyba), vrátime None
        if block_id not in self.assets.textures:
            return None

        textures_list = self.assets.textures[block_id]
        if not textures_list:
            return None

        # Dynamicky zistíme počet skutočne načítaných variantov
        count = len(textures_list)

        # Výber variantu pomocou modula
        # hash % pocet_obrazkov zaistí, že nikdy nevyjdeme z rozsahu zoznamu
        variant_index = variant_hash % count

        if is_background:
            return self.assets.dark_textures[block_id][variant_index]
        else:
            return self.assets.textures[block_id][variant_index]