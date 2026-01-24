import pygame
from settings import TILE_SIZE, COLORS
from tile_manager import BLOCKS


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
            if block_id == 0: continue  # Vzduch preskočíme

            self.textures[block_id] = []
            self.dark_textures[block_id] = []

            name = data["name"]
            variants = data["variants"]

            for i in range(variants):
                # 1. Vygenerovanie základnej textúry (namiesto načítania PNG)
                original_img = self._generate_dummy_texture(name, i)
                self.textures[block_id].append(original_img)

                # 2. Vytvorenie tmavej verzie (Baking)
                dark_img = original_img.copy()

                # Vytvoríme tmavo-sivú vrstvu
                dark_overlay = pygame.Surface((TILE_SIZE, TILE_SIZE))
                dark_overlay.fill((100, 100, 100))  # RGB (100,100,100)

                # Aplikujeme násobenie farieb (BLEND_MULT)
                dark_img.blit(dark_overlay, (0, 0), special_flags=pygame.BLEND_MULT)

                self.dark_textures[block_id].append(dark_img)

            print(f"Blok '{name}': pripravené {variants} varianty (Popredie + Pozadie).")

    def _generate_dummy_texture(self, name, variant_index):
        """
        Vyrobí farebný štvorec s jemným šumom, aby to vyzeralo ako blok.
        """
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        base_color = COLORS.get(name, (255, 0, 255))  # Ružová ak nenájde farbu

        # Jemná variácia farby pre každý variant
        r, g, b = base_color
        offset = variant_index * 15
        r = int(max(0, min(255, r + offset)))
        g = int(max(0, min(255, g + offset)))
        b = int(max(0, min(255, b + offset)))

        surf.fill((r, g, b))

        # Nakreslíme rámik
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 1)

        # Nakreslíme malý detail do stredu - OPRAVENÉ
        center = TILE_SIZE // 2
        # Tu bola chyba: pri odpočítaní musíme dať pozor, aby sme nešli pod 0
        detail_r = max(0, r - 20)
        detail_g = max(0, g - 20)
        detail_b = max(0, b - 20)

        pygame.draw.rect(surf, (detail_r, detail_g, detail_b), (center - 4, center - 4, 8, 8))

        return surf