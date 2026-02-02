import pygame
import sys
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, ASSETS_DIR, MENU_BG_COLOR

LEADERBOARD_FILE = "leaderboard.txt"


class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 40)
        self.small_font = pygame.font.SysFont("Arial", 20)
        self.score_font = pygame.font.SysFont("Consolas", 24, bold=True)

        self.view = "main"

        # Load background image
        self.background_image = None
        bg_path = os.path.join(ASSETS_DIR, "menu_background.png")
        if os.path.exists(bg_path):
            try:
                img = pygame.image.load(bg_path).convert()
                self.background_image = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception as e:
                print(f"Error loading menu background: {e}")

        self.button_width = 250
        self.button_height = 60
        self.button_gap = 20
        self.start_y = SCREEN_HEIGHT // 2
        self.center_x = SCREEN_WIDTH // 2

        self.btn_color_normal = (0, 0, 0, 200)
        self.btn_color_hover = (40, 40, 40, 230)
        self.text_color = (255, 255, 255)
        self.border_color = (200, 200, 200)

        self.main_buttons = [
            {"text": "Nový Svet", "action": "game", "rect": None},
            {"text": "Tabuľka Rekordov", "action": "leaderboard", "rect": None},
            {"text": "Ukončiť Hru", "action": "quit", "rect": None}
        ]

        self.back_button = {"text": "Späť", "action": "back", "rect": None}
        self._resize_buttons()

    def _resize_buttons(self):
        for i, button in enumerate(self.main_buttons):
            y = self.start_y + i * (self.button_height + self.button_gap)
            rect = pygame.Rect(self.center_x - self.button_width // 2, y, self.button_width, self.button_height)
            button["rect"] = rect

        rect = pygame.Rect(self.center_x - self.button_width // 2, SCREEN_HEIGHT - 100, self.button_width,
                           self.button_height)
        self.back_button["rect"] = rect

    def load_scores(self):
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                scores = [float(line.strip()) for line in f.readlines() if line.strip()]
            scores.sort()
            return scores[:10]
        except ValueError:
            return []

    def draw(self):
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
        else:
            self.screen.fill(MENU_BG_COLOR)

        # Priehľadný povrch pre UI prvky
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        mouse_pos = pygame.mouse.get_pos()

        if self.view == "main":

            for button in self.main_buttons:
                self._draw_button(s, button, mouse_pos)

        elif self.view == "leaderboard":
            # --- TU JE OPRVA: POZADIE PRE REKORDY ---
            # Nakreslíme tmavý obdĺžnik pod textom
            bg_rect = pygame.Rect(self.center_x - 200, 100, 400, 450)
            pygame.draw.rect(s, (0, 0, 0, 220), bg_rect, border_radius=15)  # Čierna s priehľadnosťou 220
            pygame.draw.rect(s, (255, 215, 0), bg_rect, 2, border_radius=15)  # Zlatý rámik

            lbl_title = self.font.render("Top Speedrun Časy", True, (255, 215, 0))
            s.blit(lbl_title, (SCREEN_WIDTH // 2 - lbl_title.get_width() // 2, 120))

            scores = self.load_scores()
            start_score_y = 180
            if not scores:
                txt = self.score_font.render("Žiadne rekordy zatiaľ.", True, (200, 200, 200))
                s.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, start_score_y))
            else:
                for i, score in enumerate(scores):
                    color = (255, 255, 255)
                    if i == 0:
                        color = (255, 215, 0)  # Zlatá
                    elif i == 1:
                        color = (192, 192, 192)  # Strieborná
                    elif i == 2:
                        color = (205, 127, 50)  # Bronzová

                    txt = self.score_font.render(f"{i + 1}. {score:.2f} s", True, color)
                    s.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, start_score_y + i * 30))

            self._draw_button(s, self.back_button, mouse_pos)

        self.screen.blit(s, (0, 0))
        pygame.display.flip()

    def _draw_button(self, surface, button, mouse_pos):
        color = self.btn_color_normal
        if button["rect"].collidepoint(mouse_pos):
            color = self.btn_color_hover

        pygame.draw.rect(surface, color, button["rect"], border_radius=10)
        pygame.draw.rect(surface, self.border_color, button["rect"], 2, border_radius=10)

        text_surf = self.small_font.render(button["text"], True, self.text_color)
        text_rect = text_surf.get_rect(center=button["rect"].center)
        surface.blit(text_surf, text_rect)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.view == "main":
                    for button in self.main_buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            if button["action"] == "leaderboard":
                                self.view = "leaderboard"
                            else:
                                return button["action"]
                elif self.view == "leaderboard":
                    if self.back_button["rect"].collidepoint(mouse_pos):
                        self.view = "main"
        return None