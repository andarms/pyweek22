import pygame as pg

from conts import *


def wall_collide(left, right):
    return left.hit_rect.colliderect(right.rect)


class Player(pg.sprite.DirtySprite):

    """docstring for Player"""

    def __init__(self, pos):
        super(Player, self).__init__()
        self.pos = [pos[0], pos[1]]
        self.image = pg.Surface((20, 20))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(topleft=self.pos)
        self.hit_rect = self.rect.copy()
        self.hit_rect.midbottom = self.rect.midbottom
        self.speed = 200
        self.direction = None
        self.direction_stack = []

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

    def check_collitions(self, walls):
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

    def handle_input(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in CONTROLS:
                self.add_direction(CONTROLS[event.key])

        if event.type == pg.KEYUP:
            if event.key in CONTROLS:
                self.pop_direction(CONTROLS[event.key])

    def update(self, dt, walls):
        if self.direction_stack:
            direction_vector = DIR_VECTORS[self.direction]
            self.rect.x += direction_vector[0] * self.speed * dt
            self.rect.y += direction_vector[1] * self.speed * dt
            self.hit_rect.center = self.rect.center
        self.check_collitions(walls)

    def render(self, surface):
        surface.blit(self.image, self.rect)
