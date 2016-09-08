import math

import pygame as pg
from bulletml import Bullet, BulletML

from conts import *

TILES = split_sheet(GFX['weapons'], (64, 64), 3, 2)


class SimpleBullet(Bullet, pg.sprite.DirtySprite):

    """docstring for Bullet"""

    def __init__(self, x=0, y=0, direction=0, speed=0, target=None,
                 actions=(), rank=0.5, tags=(), appearance=None,
                 radius=0.5):
        self.radius = 2
        self.speed = speed
        Bullet.__init__(self, x, y, direction, self.speed, target,
                        actions, rank, tags, appearance,
                        self.radius)
        pg.sprite.DirtySprite.__init__(self, BULLETS_GROUP)

        self.color = (255, 255, 0)
        w, h = (20, 20)
        self.image = pg.Surface((w, h))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = self.x, self.y
        self.time = 0.0
        self.lifetime = 3
        self.layer = 9

    def update(self, dt):
        self.time += dt
        self.rect.topleft = self.x, self.y
        if self.time > self.lifetime:
            self.kill()
            self.vanished = True
            del(self)


class SimpleWeapon(pg.sprite.DirtySprite):

    """docstring for SimpleWeapon"""

    def __init__(self, pos):
        super(SimpleWeapon, self).__init__()
        self.frames = {
            "LEFT": pg.transform.flip(TILES[0][0], True, False),
            "RIGHT": TILES[0][0]
        }
        self.relative_x = 16
        self.x, self.y = pos
        self.image = self.frames["RIGHT"]
        self.rect = self.image.get_rect(topleft=pos)
        DECORATOR_GROUP.add(self)
        self.dirty = 2

        self.pattern = BulletML.FromDocument(open("threefire.xml", "rU"))
        self.bullets = []
        self.cooldowntime = 0.3
        self.cooldown = self.cooldowntime
        self.cooled = False

    def shoot(self, target):
        if self.cooled:
            bullet = SimpleBullet.FromDocument(
                self.pattern, self.rect.centerx,
                self.rect.centery+4, target=target)
            self.bullets.extend([bullet])
            bullet.vanished = True
            bullet.kill()

    def update(self, dt, pos, direction):
        self.image = self.frames[direction]
        self.rect.topleft = pos
        if direction == "LEFT":
            self.rect.left = pos[0]-self.relative_x
        self.x, self.y = self.rect.topleft

        # Bullets
        if(self.bullets):
            for bullet in self.bullets:
                self.bullets.extend(bullet.step())
                bullet.update(dt)
        self.cooldown -= dt
        if self.cooldown < 0:
            self.cooled = True

    def draw(self, surface):
        surface.blit(self.image, self.rect)
