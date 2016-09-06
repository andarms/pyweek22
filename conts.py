import pygame as pg

TILE_SIZE = 32
TS2 = TILE_SIZE*2
GRID = (160, 96)
SCREEN_SIZE = (1024, 768)


MAX_ROOM_W = 20
MAX_ROOM_H = 15
MIN_ROOM_W = 15
MIN_ROOM_H = 8

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
BULLETS_GROUP = pg.sprite.Group()
