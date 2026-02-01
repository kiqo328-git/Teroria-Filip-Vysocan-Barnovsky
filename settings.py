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

# --- Konfigurácia jaskýň (Bez zmeny) ---
CAVE_FREQ = 0.10         
CAVE_THRESHOLD = 0.4     
MAX_CAVE_DEPTH = 300.0   
MAX_THRESHOLD_INCREASE = 0.2 

# FBM (Octaves) pre organickejší a Perlin-like vzhľad
OCTAVES = 2
LACUNARITY = 2.0  
GAIN = 0.5        


PLAYER_SCALE = 0.4

PLAYER_SKINS = {0:{"head":"male_head.png", "arm":"male_arm.png", "body": "male_body.png", "leg":"male_leg.png"},}

CURRENT_PLAYER_REACH = 5 * TILE_SIZE

# --- Konfigurácia NPC (UPRAVENÉ: Frekvencia pre jednoduchosť, Vzdialenosť pre kontrolu) ---
NPC_INTERACT_RANGE = 4 * TILE_SIZE # Dosah interakcie (4 dlaždice)
NPC_SPAWN_FREQ = 0.05 # VYŠŠIA frekvencia (0.05) - pre rýchle zmeny šumu (žiadne série)
NPC_SPAWN_THRESHOLD = 0.80 # ZNÍŽENÝ prah (0.80) - pre väčšiu šancu na spawn, ak je to možné.
MIN_NPC_DIST = 300 # UPRAVENÉ: Minimálna vzdialenosť (v dlaždiciach) medzi NPC. (Cieľ 200-400)