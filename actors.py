import math

import pygame as pg
from bulletml import Bullet, BulletML

from conts import *


def wall_collide(left, right):
    return left.hit_rect.colliderect(right.rect)


class Player(pg.sprite.DirtySprite):

    """docstring for Player"""

    def __init__(self, pos, *groups):
        super(Player, self).__init__(*groups)
        self.pos = [pos[0], pos[1]]
        self.x, self.y = self.pos
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((0, 255, 255))
        self.image.convert()
        self.rect = self.image.get_rect(topleft=self.pos)
        self.hit_rect = self.rect.copy()
        self.hit_rect.midbottom = self.rect.midbottom
        self.speed = 200
        self.direction = None
        self.direction_stack = []

        self.layer = 8
        self.cooldowntime = 0.3
        self.cooldown = self.cooldowntime
        self.cooled = False

        self.face_direction = "down"
        self.rot_speed = 6 * math.pi / 180

        self.pattern = BulletML.FromDocument(open("threefire.xml", "rU"))
        self.bullets = []

    def add_direction(self, direction):
        """
        Add direction to the sprite's direction stack and change current
        direction.
        """
        if direction in self.direction_stack:
            self.direction_stack.remove(direction)
        self.direction_stack.append(direction)
        self.direction = direction

    def pop_direction(self, direction):
        """
        Remove direction from direction stack and change current direction
        to the top of the stack (if not empty).
        """
        if direction in self.direction_stack:
            self.direction_stack.remove(direction)
        if self.direction_stack:
            self.direction = self.direction_stack[-1]

    def check_collitions(self, walls, doors):
        wall = pg.sprite.spritecollideany(self, walls, wall_collide)
        if wall:
            if self.direction == "LEFT":
                self.hit_rect.left = wall.rect.right
            elif self.direction == "RIGHT":
                self.hit_rect.right = wall.rect.left
            elif self.direction == "UP":
                self.hit_rect.top = wall.rect.bottom
            elif self.direction == "DOWN":
                self.hit_rect.bottom = wall.rect.top
            self.rect.center = self.hit_rect.center
            self.collide = True
        else:
            self.collide = False
        door = pg.sprite.spritecollideany(self, doors, wall_collide)
        if(door):
            door.room.spaw_enemies()

    def change_face_direction(self, angle):
        if self.direction == "UP" or self.direction == "DOWN":
            if angle > 0:
                self.face_direction = "DOWN"
            else:
                self.face_direction = "UP"

        if self.direction == "LEFT" or self.direction == "RIGHT":
            if abs(angle) > 90:
                self.face_direction = "LEFT"
            else:
                self.face_direction = "RIGTH"

    def shoot(self):
        if self.cooled:
            # x1 = y1 = 0
            # x2 = self.cursor.rect.left - self.rect.left
            # y2 = self.cursor.rect.top - self.rect.top
            # angle = math.atan2(y2, x2)
            # b = Bullet(self.rect.center, angle)
            # # for i in range(0, 180, 20):
            # #     Bullet(self.rect.center, math.radians(i))
            # self.cooldown = self.cooldowntime
            # self.cooled = False
            bullet = SimpleBullet.FromDocument(
                self.pattern, self.x, self.y, target=self.cursor)
            self.bullets.extend([bullet])
            bullet.vanished = True

    def handle_input(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in CONTROLS:
                self.add_direction(CONTROLS[event.key])

        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.shoot()

        if event.type == pg.KEYUP:
            if event.key in CONTROLS:
                self.pop_direction(CONTROLS[event.key])

    def update(self, dt, walls, doors, cursor):
        self.cursor = cursor
        if self.direction_stack:
            direction_vector = DIR_VECTORS[self.direction]
            self.rect.x += direction_vector[0] * self.speed * dt
            self.rect.y += direction_vector[1] * self.speed * dt
            self.hit_rect.center = self.rect.center
        self.check_collitions(walls, doors)
        self.x, self.y = self.hit_rect.center
        if(self.bullets):
            for bullet in self.bullets:
                self.bullets.extend(bullet.step())
        self.cooldown -= dt
        if self.cooldown < 0:
            self.cooled = True

        # self.change_face_direction(angle)
        for b in self.bullets:
            b.update(dt)

    def render(self, surface):
        surface.blit(self.image, self.rect)
        for b in self.bullets:
            if not b.vanished:
                surface.blit(b.image, (b.x, b.y))


class Enemie(pg.sprite.Sprite):

    """docstring for Enemie"""

    def __init__(self, pos):
        super(Enemie, self).__init__()
        self.x, y = pos
        self.cooldowntime = 0.3
        self.cooldown = self.cooldowntime
        self.cooled = False
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 0, 255))
        self.image.convert()
        self.rect = self.image.get_rect(topleft=pos)
        self.hit_rect = self.rect.copy()
        self.hit_rect.midbottom = self.rect.midbottom

    def update(self, dt, player):
        if cooled:
            bullet = SimpleBullet.FromDocument(
                self.pattern, self.x, self.y, target=player)
            self.bullets.extend([bullet])
            bullet.vanished = True

        self.cooldown -= dt
        if self.cooldown < 0:
            self.cooled = True

        if(self.bullets):
            for bullet in self.bullets:
                self.bullets.extend(bullet.step())

    def render(self, surface):
        surface.blit(self.image, self.rect)
        for b in self.bullets:
            if not b.vanished:
                surface.blit(b.image, (b.x, b.y))


class SimpleBullet(Bullet):

    """docstring for Bullet"""

    def __init__(self, x=0, y=0, direction=0, speed=0, target=None,
                 actions=(), rank=0.5, tags=(), appearance=None,
                 radius=0.5):
        self.radius = 2
        self.speed = speed
        super(SimpleBullet, self).__init__(x, y, direction, self.speed, target,
                                           actions, rank, tags, appearance,
                                           self.radius)

        self.color = (255, 255, 0)
        w, h = (20, 20)
        self.image = pg.Surface((w, h))
        self.image.fill(self.color)
        self.image.convert()
        self.time = 0.0
        self.lifetime = 5
        # self.speed = 450
        # self.dx = math.cos(angle) * self.speed
        # self.dy = math.sin(angle) * self.speed
        # self.dirty = 2
        self.layer = 9

    def update(self, dt):
        self.time += dt
        if self.time > self.lifetime:
            # self.kill()
            self.vanished = True
