import pygame

# --- Konfigurácia Obrazovky ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# --- Konfigurácia Sveta ---
TILE_SIZE = 32
CHUNK_SIZE = 16

# --- Farby pre generovanie textúr ---
COLORS = {
    "Air": (0, 0, 0),
    "Grass": (34, 139, 34),
    "Dirt": (139, 69, 19),
    "Stone": (128, 128, 128),
    "Bedrock": (50, 50, 50)
}

# Farba oblohy
SKY_COLOR = (135, 206, 235)