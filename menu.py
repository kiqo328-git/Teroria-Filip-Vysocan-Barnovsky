import pygame
import sys
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_DIR

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 40)
        self.small_font = pygame.font.SysFont("Arial", 20)
        
        # Load background image
        self.background_image = None
        bg_path = os.path.join(ASSETS_DIR, "menu_background.png")
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert()
                self.background_image = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception as e:
                print(f"Error loading menu background: {e}")
        else:
            print(f"Menu background not found at {bg_path}. Using default color.")

        # UI Configuration (Upravte podľa potreby)
        self.title_text = "" # Ak je názov na obrázku, dajte ""
        
        # Pozícia tlačidiel
        self.button_width = 250
        self.button_height = 60
        self.button_gap = 20
        self.start_y = SCREEN_HEIGHT // 2 + 120 # Posunuté ešte nižšie
        self.center_x = SCREEN_WIDTH // 2 

        # Farby
        self.btn_color_normal = (0, 0, 0, 200) # Tmavšia a menej priehľadná čierna
        self.btn_color_hover = (40, 40, 40, 230) # Takmer nepriehľadná pri nabehnutí
        self.text_color = (255, 255, 255)
        self.border_color = (200, 200, 200) # Farba okraja tlačidiel

        self.buttons = [
            {"text": "Nový Svet", "action": "game", "rect": None},
            {"text": "Ukončiť Hru", "action": "quit", "rect": None}
        ]
        
        self._resize_buttons()

    def _resize_buttons(self):
        for i, button in enumerate(self.buttons):
            y = self.start_y + i * (self.button_height + self.button_gap)
            rect = pygame.Rect(self.center_x - self.button_width // 2, y, self.button_width, self.button_height)
            button["rect"] = rect

    def draw(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill((50, 50, 50))
        
        # Title
        if self.title_text:
            title_surf = self.font.render(self.title_text, True, (255, 255, 255))
            # Vykreslenie tieňa pre text
            shadow_surf = self.font.render(self.title_text, True, (0, 0, 0))
            self.screen.blit(shadow_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2 + 2, 100 + 2))
            self.screen.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 100))
        
        # Buttons Setup for transparent drawing
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            color = self.btn_color_normal
            if button["rect"].collidepoint(mouse_pos):
                color = self.btn_color_hover
            
            # Draw rounded rect (or simple rect) on transparent surface
            pygame.draw.rect(s, color, button["rect"], border_radius=10)
            
            # Border
            pygame.draw.rect(s, self.border_color, button["rect"], 2, border_radius=10)
            
            text_surf = self.small_font.render(button["text"], True, self.text_color)
            text_rect = text_surf.get_rect(center=button["rect"].center)
            s.blit(text_surf, text_rect)
        
        self.screen.blit(s, (0,0))
            
        pygame.display.flip()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    for button in self.buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            return button["action"]
        return None
