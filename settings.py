import random

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

ASSETS_DIR = "assets"

BLOCKS = {
    0: {"name": "Air", "solid": False, "variants": 0, "file": None},
    1: {"name": "Grass", "solid": True, "variants": 1, "file": "dirt_grass.png"},
    2: {"name": "Stone", "solid": True, "variants": 1, "file": "stone.png"},
    3: {"name": "Dirt", "solid": True, "variants": 1, "file": "dirt.png"},
    4: {"name": "Bedrock", "solid": True, "variants": 1, "file": "greystone.png"},
}

SEED = random.randint(-999999, 999999)

FREQ = 0.05
MULTIPLIER = 20.0
BASE_HEIGHT = 10.0

RENDER_DISTANCE = 2
UNLOAD_DISTANCE = RENDER_DISTANCE + 2

PLAYER_SCALE = 0.4

PLAYER_SKINS = {0:{"head":"male_head.png", "arm":"male_arm.png", "body": "male_body.png", "leg":"male_leg.png"},}