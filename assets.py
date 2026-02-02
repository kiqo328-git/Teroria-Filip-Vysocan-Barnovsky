import pygame
import os
from settings import *

class AssetManager:
    def __init__(self):
        # Úložisko textúr: {block_id: [obrazok_var_0, obrazok_var_1, ...]}
        self.textures = {}
        self.dark_textures = {}

        # Spustíme generovanie hneď pri štarte
        self.load_and_bake()

    def load_and_bake(self):
        print("--- AssetManager: Generujem textúry a 'pečiem' tmavé pozadia ---")

        for block_id, data in BLOCKS.items():
            if block_id == 0: continue

            self.textures[block_id] = []
            self.dark_textures[block_id] = []

            name = data["name"]
            filename_data = data.get("file") # Môže to byť string alebo list

            if filename_data:
                # Zistíme, či ide o jeden súbor alebo zoznam súborov
                files_to_load = []
                if isinstance(filename_data, list):
                    files_to_load = filename_data
                else:
                    files_to_load = [filename_data]

                # Načítame všetky súbory pre tento blok
                for fname in files_to_load:
                    path = os.path.join(ASSETS_DIR, fname)
                    try:
                        # Načítanie obrázka
                        img = pygame.image.load(path).convert_alpha()
                        img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))

                        # Uložíme do zoznamu
                        self.textures[block_id].append(img)

                        # Vytvorenie tmavej verzie
                        dark_img = img.copy()
                        dark_overlay = pygame.Surface((TILE_SIZE, TILE_SIZE))
                        dark_overlay.fill((100, 100, 100))
                        dark_img.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_MULT)

                        self.dark_textures[block_id].append(dark_img)
                        print(f"Blok '{name}': načítaný variant '{fname}'")

                    except FileNotFoundError:
                        print(f"CHYBA: Súbor '{fname}' sa nenašiel v priečinku '{ASSETS_DIR}'!")
                        self._create_fallback_single(block_id)
            else:
                print(f"VAROVANIE: Blok '{name}' nemá definovaný súbor!")
                self._create_fallback_single(block_id)

    def _create_fallback_single(self, block_id):
        """Vytvorí jeden ružový štvorec ako fallback pre chýbajúci súbor."""
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill((255, 0, 255))  # Ružová pre chybu
        self.textures[block_id].append(surf)
        self.dark_textures[block_id].append(surf)

    def get_player_paths(self, index):
        if index not in PLAYER_SKINS:
            print(f"POZOR: Skin index {index} neexistuje, načítavam 0.")
            index = 0
        raw_skin = PLAYER_SKINS[index]
        full_paths = {}
        for part, filename in raw_skin.items():
            full_paths[part] = os.path.join(ASSETS_DIR, filename)
        return full_paths