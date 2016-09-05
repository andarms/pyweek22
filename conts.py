import pygame as pg

TILE_SIZE = 32
GRID = (160, 96)
SCREEN_SIZE = (960, 600)


MAX_ROOM_W = 25
MAX_ROOM_H = 18
MIN_ROOM_W = 15
MIN_ROOM_H = 12

CONTROLS = {
    pg.K_w:  "UP",
    pg.K_s: "DOWN",
    pg.K_a:  "LEFT",
    pg.K_d: "RIGHT"
}

DIR_VECTORS = {
    "UP":  (0, -1),
    "DOWN":  (0, 1),
    "LEFT":  (-1, 0),
    "RIGHT":  (1, 0)
}


# Initialization
pg.init()
SCREEN = pg.display.set_mode(SCREEN_SIZE)
SCREEN_RECT = SCREEN.get_rect()
