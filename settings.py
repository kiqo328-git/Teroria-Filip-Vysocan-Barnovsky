import random
import pygame

# --- Konfigurácia Obrazovky ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60 # 90 môže byť zbytočne veľa, 60 je stabilnejšie pre fyziku

# --- Konfigurácia Sveta ---
TILE_SIZE = 32
CHUNK_SIZE = 16

# --- HERNÉ MECHANIKY ---
GAME_DURATION = 300
LEADERBOARD_FILE = "leaderboard.txt"

# --- Farby ---
SKY_COLOR = (135, 206, 235)
MENU_BG_COLOR = (20, 20, 40)
COLORS = {
    "Air": (0, 0, 0),
    "Grass": (34, 139, 34),
    "Dirt": (139, 69, 19),
    "Stone": (128, 128, 128),
    "Bedrock": (50, 50, 50),
    "Vegetation": (0, 255, 0)
}

ASSETS_DIR = "assets"
END_SCREEN = "Agartha.jpg"

# --- DEFINÍCIA BLOKOV ---
BLOCKS = {
    0: {"name": "Air", "solid": False, "variants": 0, "file": None},
    1: {"name": "Grass", "solid": True, "variants": 1, "file": "dirt_grass.png"},
    2: {"name": "Stone", "solid": True, "variants": 1, "file": "stone.png"},
    3: {"name": "Dirt", "solid": True, "variants": 1, "file": "dirt.png"},
    4: {"name": "Bedrock", "solid": True, "variants": 1, "file": "greystone.png"},
    5: {
        "name": "Vegetation",
        "solid": False,
        "variants": 6,
        "file": ["grass1.png", "grass2.png", "grass3.png", "grass4.png", "rock.png", "rock_moss.png"]
    },
    6: {"name":"Monster", "solid": False, "variants": 1, "file": "white-monster.png"},
}

# --- Generovanie ---
SEED = random.randint(-999999, 999999)

FREQ = 0.05
MULTIPLIER = 20.0
BASE_HEIGHT = 10.0

RENDER_DISTANCE = 2
UNLOAD_DISTANCE = RENDER_DISTANCE + 2

# Jaskyne
CAVE_FREQ = 0.10
CAVE_THRESHOLD = 0.3
MAX_CAVE_DEPTH = 150.0
MAX_THRESHOLD_INCREASE = 0.2
OCTAVES = 2
LACUNARITY = 2.0
GAIN = 0.5

# --- NPC (Upravené na ťažšie) ---
NPC_INTERACT_RANGE = 4 * TILE_SIZE

NPC_SPAWN_FREQ = 0.02
NPC_SPAWN_THRESHOLD = 0.7
MIN_NPC_DIST = 200

VEGETATION_CHANCE = 0.15

# Postava
PLAYER_SCALE = 0.4
PLAYER_SKINS = {0: {"head": "male_head.png", "arm": "male_arm.png", "body": "male_body.png", "leg": "male_leg.png"}}
CURRENT_PLAYER_REACH = 5 * TILE_SIZE