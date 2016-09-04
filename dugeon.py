import math
import random

import pygame as pg

from conts import *
from actors import Player


def get_random_point_in_circle(w, h):
    """  based on
    http://www.gamasutra.com/blogs/AAdonaac/20150903/252889/Procedural_Dungeon_Generation_Algorithm.php
    which is based on http://tinykeep.com/dungen/
    """
    t = 2*math.pi*random.random()
    u = random.random()*2
    r = None
    if u > 1:
        r = 2-u
    else:
        r = u
    x = w*r*math.cos(t)
    y = h*r*math.sin(t)
    x = math.floor(((x + TILE_SIZE - 1)/TILE_SIZE))*TILE_SIZE
    y = math.floor(((y + TILE_SIZE - 1)/TILE_SIZE))*TILE_SIZE
    return [x, y]


class Cell():

    """docstring for RandRoom"""

    def __init__(self):
        self.pos = [0, 0]
        self.pos[0] = GRID[0]*TILE_SIZE/4
        self.pos[1] = GRID[0]*TILE_SIZE/4
        x, y = get_random_point_in_circle(40*TILE_SIZE, TILE_SIZE)
        self.pos[0] += x
        self.pos[1] += y
        w = random.randint(2, MAX_ROOM_W)
        h = random.randint(2, MAX_ROOM_H)
        self.color = [100, 100, 100]
        self.image = pg.Surface((w*TILE_SIZE, h*TILE_SIZE))
        self.image.fill(self.color)
        self.rect = self.image.get_rect(topleft=self.pos)
        self.seleted = False

    def render(self, surface):
        surface.blit(self.image, self.rect)


class Dugeon(object):

    """docstring for Dugeon"""

    def __init__(self):
        super(Dugeon, self).__init__()
        self.cells_count = 100
        self.show_paths = True
        self.cells = []
        while(len(self.cells) < self.cells_count):
            c = Cell()
            self.cells.append(c)
        area, min_x, min_y = self.separate_cells(self.cells)
        self.rooms = self.select_main_rooms(self.cells)
        self.paths = self.connet_rooms(self.rooms)
        # self.make_hallways(self.cells)

        self.image = pg.Surface(
            (area[0]+MAX_ROOM_W*TILE_SIZE, area[1]+MAX_ROOM_H*TILE_SIZE))
        self.rect = self.image.get_rect()
        self.clip_rooms(min_x, min_y)

        self.player = Player([0, 0])
        self.viewport = Viewport()
        self.viewport.update(self.player, self.rect)

    def separate_cells(self, cells):
        """based on http://fisherevans.com/blog/post/dungeon-generation
        """
        touching = True
        interation = 0
        min_x = 0
        max_x = 0
        min_y = 0
        max_y = 0
        while touching:
            touching = False
            for i in range(len(cells)):
                a = cells[i]
                for j in range(i+1, len(cells)):
                    b = cells[j]
                    if a.rect.colliderect(b.rect):
                        touching = True
                        dx = min(
                            a.rect.right-b.rect.left+TILE_SIZE,
                            a.rect.left-b.rect.right-TILE_SIZE)
                        dy = min(
                            a.rect.bottom-b.rect.top+TILE_SIZE,
                            a.rect.top-b.rect.bottom-TILE_SIZE)
                        if (abs(dx) < abs(dy)):
                            dy = 0
                        else:
                            dx = 0

                        dxa = -dx / 2
                        dxb = dx + dxa
                        dya = -dy / 2
                        dyb = dy + dya

                        dxa = math.floor(
                            ((dxa + TILE_SIZE - 1)/TILE_SIZE))*TILE_SIZE
                        dxb = math.floor(
                            ((dxb + TILE_SIZE - 1)/TILE_SIZE))*TILE_SIZE
                        dya = math.floor(
                            ((dya + TILE_SIZE - 1)/TILE_SIZE))*TILE_SIZE
                        dyb = math.floor(
                            ((dyb + TILE_SIZE - 1)/TILE_SIZE))*TILE_SIZE

                        a.pos[0] += dxa
                        a.pos[1] += dya
                        b.pos[0] += dxb
                        b.pos[1] += dyb
                        min_x = min(min_x, a.pos[0], b.pos[0])
                        min_y = min(min_y, a.pos[1], b.pos[1])
                        max_x = max(max_x, a.pos[0], b.pos[0])
                        max_y = max(max_y, a.pos[1], b.pos[1])
                        a.rect.topleft = a.pos
                        b.rect.topleft = b.pos
        area = ((max_x-min_x), (max_y-min_y))
        print(area, abs(min_x), abs(min_y))
        return area, min_x, min_y

    def select_main_rooms(self, cells):
        seleted = []
        for room in cells:
            if(room.rect.w > MIN_ROOM_W*TILE_SIZE
                    and room.rect.h > MIN_ROOM_H*TILE_SIZE):
                room.image.fill([random.randint(0, 255) for _ in range(3)])
                room.seleted = True
                seleted.append(room)
        print("Rooms selected as main rooms %s" % len(seleted))
        return seleted

    def connet_rooms(self, rooms):
        paths = []
        for i in range(len(rooms)):
            a = rooms[i]
            for j in range(i+1, len(rooms)):
                skip = False
                b = rooms[j]
                ab_dist = math.pow(a.rect.centerx-b.rect.centerx, 2) + \
                    math.pow(a.rect.centery-b.rect.centery, 2)
                for k in range(len(rooms)):
                    if(k == i or k == j):
                        continue
                    c = rooms[k]
                    ac_dist = math.pow(a.rect.centerx-c.rect.centerx, 2) + \
                        math.pow(a.rect.centery-c.rect.centery, 2)

                    bc_dist = math.pow(b.rect.centerx-c.rect.centerx, 2) + \
                        math.pow(b.rect.centery-c.rect.centery, 2)

                    if(ac_dist < ab_dist and bc_dist < ab_dist):
                        skip = True
                if not skip:
                    ps = self.create_path(a.rect.center, b.rect.center)
                    paths += ps
        return paths

    def create_path(self, p1, p2):
        if(p1[0] < p2[0]):
            a = p1
            b = p2
        else:
            a = p2
            b = p1
        x, y = a
        dx = b[0] - x
        dy = b[1] - y
        t2 = TILE_SIZE/2
        # w = random.randint(TILE_SIZE, TILE_SIZE*3)
        # h = random.randint(TILE_SIZE, TILE_SIZE*3)
        w = TILE_SIZE*3
        h = TILE_SIZE*3
        if(random.randint(0, 1) == 1):
            r1 = pg.Rect(x, y, dx+w, h)
            r2 = pg.Rect(x+dx, y, w, dy)
        else:
            r1 = pg.Rect(x, (y-TILE_SIZE)+dy, dx+w, h)
            r2 = pg.Rect(x, y, w, dy)
        return [r1, r2]

    def make_hallways(self, rooms):
        for r in self.cells:
            if r.seleted:
                continue
            if r.rect.collidelist(self.paths) > 0:
                r.image.fill([100, 100, 100])
                r.seleted = True
        print("main rooms %s" % len(self.rooms))

    def clip_rooms(self, min_x, min_y):
        for r in self.rooms:
            r.pos[0] += abs(min_x)
            r.pos[1] += abs(min_y)
            r.rect = r.pos
        for p in self.paths:
            p.left += abs(min_x)
            p.top += abs(min_y)

    def handle_input(self, event):
        self.player.handle_input(event)

    def update(self, dt):
        self.player.update(dt)
        self.viewport.update(self.player, self.rect)

    def render(self, surface):
        self.image.fill((0, 0, 0))
        if self.show_paths:
            for p in self.paths:
                pg.draw.rect(self.image, (200, 100, 100), p)
        for c in self.cells:
            if c.seleted:
                c.render(self.image)
        self.player.render(self.image)
        surface.blit(self.image, (0, 0), self.viewport)


class Viewport(object):

    """docstring for viewport"""

    def __init__(self):
        self.rect = SCREEN_RECT.copy()

    def update(self, player, screen_rect):
        self.rect.center = player.rect.center
        self.rect.clamp_ip(screen_rect)
