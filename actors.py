import math
from itertools import cycle

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
        self.layer = 8

        # movement
        self.direction = None
        self.direction_stack = []
        self.face_direction = "RIGHT"
        self.old_direction = self.face_direction
        self.speed = 300

        # Armo
        self.pattern = BulletML.FromDocument(open("threefire.xml", "rU"))
        self.bullets = []
        self.cooldowntime = 0.3
        self.cooldown = self.cooldowntime
        self.cooled = False

        frames = self.get_frames("hero")
        self.idelframes = {}
        self.frames = self.make_frame_dict(frames)
        self.walkframes = None
        self.animate_timer = 0.0
        self.animate_fps = 10.0

        self.image = frames[0][0]
        self.rect = self.image.get_rect(topleft=self.pos)
        self.hit_rect = pg.Rect(0, 0, 10, 10)
        self.hit_rect.center = self.rect.center

    def make_frame_dict(self, frames):
        frame_dict = {}
        self.idelframes['RIGHT'] = frames[0][0]
        frame_dict["RIGHT"] = cycle(frames[0])
        left = []
        for frame in frames[0]:
            left.append(
                pg.transform.flip(frame, True, False))
        self.idelframes['LEFT'] = left[0]
        frame_dict["LEFT"] = cycle(left)
        return frame_dict

    def get_frames(self, spritesheet):
        sheet = GFX[spritesheet]
        all_frames = split_sheet(sheet, (48, 128), 4, 1)
        return all_frames

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
            door.open()

    def change_face_direction(self, angle):
        # to not convert  to degrees
        if abs(angle) > 1.5:
            self.face_direction = "LEFT"
        else:
            self.face_direction = "RIGHT"

    def shoot(self):
        if self.cooled:
            bullet = SimpleBullet.FromDocument(
                self.pattern, self.x, self.y, target=self.cursor)
            self.bullets.extend([bullet])
            bullet.vanished = True
            bullet.kill()

    def animate(self, now=0):
        now = pg.time.get_ticks()
        if self.face_direction != self.old_direction:
            self.walkframes = self.frames[self.face_direction]
            self.old_direction = self.face_direction
            self.dirty = 1
        if self.dirty or now-self.animate_timer > 1000/self.animate_fps:
            if self.direction_stack:
                self.image = next(self.walkframes)
                self.animate_timer = now
                self.dirty = 0
            else:
                self.image = self.idelframes[self.face_direction]

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

        # Bullets
        if(self.bullets):
            for bullet in self.bullets:
                self.bullets.extend(bullet.step())
                bullet.update(dt)
        self.cooldown -= dt
        if self.cooldown < 0:
            self.cooled = True

        # Direction
        x = self.cursor.rect.left - self.rect.left
        y = self.cursor.rect.top - self.rect.top
        self.angle = math.atan2(y, x)
        self.change_face_direction(self.angle)

        self.animate()

    def render(self, surface):
        surface.blit(self.image, self.rect)
        for b in self.bullets:
            if not b.vanished:
                surface.blit(b.image, (b.x, b.y))


class Enemie(pg.sprite.DirtySprite):

    """docstring for Enemie"""

    def __init__(self, pos):
        super(Enemie, self).__init__()
        self.x, self.y = pos
        self.cooldowntime = 0.7
        self.cooldown = self.cooldowntime
        self.cooled = True
        self.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((255, 0, 255))
        self.image.convert()
        self.rect = self.image.get_rect(topleft=pos)
        self.hit_rect = self.rect.copy()
        self.hit_rect.center = self.rect.center
        self.pattern = BulletML.FromDocument(open("threefire.xml", "rU"))
        self.bullets = []
        self.lifetime = 10

    def update(self, dt, player):
        self.lifetime -= dt
        if self.lifetime < 0:
            for b in self.bullets:
                b.vanished = True
                b.kill()
                del(b)
            self.kill()
            del(self)
            return

        if self.cooled:
            bullet = SimpleBullet.FromDocument(
                self.pattern, self.x, self.y, target=player)
            self.bullets.extend([bullet])
            bullet.vanished = True
            bullet.kill()
            self.cooled = False

        self.cooldown -= dt
        if self.cooldown < 0:
            self.cooled = True
            self.cooldown = self.cooldowntime

        if(self.bullets):
            for bullet in self.bullets:
                self.bullets.extend(bullet.step())
                bullet.update(dt)


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
        self.lifetime = 5
        # self.speed = 450
        # self.dx = math.cos(angle) * self.speed
        # self.dy = math.sin(angle) * self.speed
        # self.dirty = 2
        self.layer = 9

    def update(self, dt):
        self.time += dt
        self.rect.topleft = self.x, self.y
        if self.time > self.lifetime:
            self.kill()
            self.vanished = True
            del(self)
