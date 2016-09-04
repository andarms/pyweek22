import pygame as pg

from conts import *


class Player(pg.sprite.Sprite):

    """docstring for Player"""

    def __init__(self, pos):
        super(Player, self).__init__()
        self.pos = pos
        self.image = pg.Surface((20, 20))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(topleft=self.pos)
        self.direction = None
        self.speed = 200

    def handle_input(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in CONTROLS:
                self.direction = CONTROLS[event.key]
            else:
                self.direction = None

        # if event.type == pg.KEYUP:

    def update(self, dt):
        if self.direction:
            v = DIR_VECTORS[self.direction]
            self.pos[0] += v[0]*self.speed*dt
            self.pos[1] += v[1]*self.speed*dt
            self.rect.topleft = self.pos

    def render(self, surface):
        surface.blit(self.image, self.rect)
