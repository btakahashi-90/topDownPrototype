import pygame as pg
from settings import *

# HUD Functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.7:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

def draw_osr_gauge(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    col = BLUE
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2) 

def draw_inventory_boxes(surf, x, y):
    # TODO add inventory list parameter, create for loop to add each item into its own box and shift y down
    # TODO add sprites into box center - need a sprite for pistol...
    # TODO ENUMERATE when creating boxes, use index to label boxes for weapon switching?
    # TODO test box coloring to indicate selected weapon
    rect_to_draw = pg.Rect(x, y, 50, 50)
    pg.draw.rect(surf, WHITE, rect_to_draw, 2, 3)
