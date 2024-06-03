import pygame as pg
vec = pg.math.Vector2

# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
LIGHT_RED = (150, 0, 0)
LIGHT_GREEN = (0, 150, 0)
BLUE = (0, 0, 255)
TRANSPARENT = (0, 0, 0, 255)
# game settings
WIDTH = 1024   # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 768  # 16 * 48 or 32 * 24 or 64 * 12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN

TILESIZE = 64 #32 # Can increase/decrease tile size to change map view, increase = less visible (i.e. exploring a maze)
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

WALL_IMG = "tileGreen_39.png"

# Player settings
PLAYER_SPEED = 250
PLAYER_IMAGE = "manBlue_gun.png"
PLAYER_ROTATION_SPEED = 250
PLAYER_HIT_RECT = pg.Rect(0, 0, 32, 32)
WEAPON_OFFSET = vec(25, 10)
PLAYER_HEALTH = 100
MIN_SAFE_DIST = 450 # should be > MAX DETECT_RADIUS of ALL MOBS <- prevent spawn and chase

# Mob settings
MOB = {}
MOB["zombie"] = {
    "img": "duckDolphin.png",
    "speeds": [100, 125, 150, 175, 200],
    "hit_rect": pg.Rect(0, 0, 32, 32),
    "health": 100,
    "damage": 10,
    "knockback": 20,
    "avoid_radius": 50,
    "detect_radius": 200,
    "max": 20
}

MOB["piggy"] = {
    "img": "piggy_scaled.png",
    "speeds": [100, 125, 150, 175, 200],
    "hit_rect": pg.Rect(0, 0, 32, 32),
    "health": 100,
    "damage": 10,
    "knockback": 20,
    "avoid_radius": 50,
    "detect_radius": 100,
    "max": 20
}

# Weapon settings
BULLET_IMG = "bullet.png"
WEAPONS = {}
WEAPONS["pistol"] = {
                    "bullet_speed": 500,
                    "bullet_lifetime": 1000,
                    "rate": 150,
                    "kickback": 0,
                    "spread": 5,
                    "damage": 10,
                    "bullet_size": "lg",
                    "bullet_count": 1
                }
WEAPONS["shotgun"] = {
                    "bullet_speed": 400,
                    "bullet_lifetime": 500,
                    "rate": 300,
                    "kickback": 0,
                    "spread": 20,
                    "damage": 5,
                    "bullet_size": "sm",
                    "bullet_count": 12
                }
WEAPONS["bfg"] = {
                    "bullet_speed": 500,
                    "bullet_lifetime": 10000,
                    "rate": 1500,
                    "kickback": 0,
                    "spread": 0,
                    "damage": 100000,
                    "bullet_size": "os",
                    "bullet_count": 1
                }

# Effects
MUZZLE_FLASHES = ["whitePuff15.png", "whitePuff16.png", "whitePuff17.png", "whitePuff18.png"]
FLASH_DURATION = 40
SPLAT = "splat_green.png"
DAMAGE_ALPHA = [i for i in range(0, 255, 25)]
NIGHT_COLOR = (20, 20, 20)
LIGHT_RADIUS = (500, 500)
LIGHT_MASK = "light_350_med.png"

# Layers
WALL_LAYER = 1
ITEMS_LAYER = 1
PLAYER_LAYER = 2
MOB_LAYER = 2
BULLET_LAYER = 3
OBSTACLE_LAYER = 3
EFFECTS_LAYER = 4

# Items
ITEM_IMGS = {
            "health": "health_pack.png",
            "shotgun": "obj_shotgun.png"
            }
HEALTH_PACK_AMOUNT = 20
BOB_RANGE = 15
BOB_SPEED = 0.4

# Sounds
BG_MUSIC = "riff_1.ogg"
PLAYER_HIT_SOUNDS = ["pain/8.wav", "pain/9.wav", "pain/10.wav", "pain/11.wav"]
ZOMBIE_MOAN_SOUNDS = ["brains2.wav", "brains3.wav", "zombie-roar-1.wav", "zombie-roar-2.wav", "zombie-roar-3.wav", "zombie-roar-5.wav", "zombie-roar-6.wav", "zombie-roar-7.wav"]
ZOMBIE_HIT_SOUNDS = ["splat-15.wav"]
WEAPON_SOUNDS_GUN = {
                    "pistol": ["pistol.wav"],
                    "shotgun": ["shotgun.wav"],
                    "bfg": ["sfx_weapon_singleshot2.wav"] 
                }
EFFECTS_SOUNDS = {
                    "level_start": "level_start.wav",
                    "health_up": "health_pack.wav",
                    "gun_pickup": "gun_pickup.wav"
                }