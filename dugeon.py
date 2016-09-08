import math
import random


import pygame as pg

from conts import *
from actors import Player, Enemie


TILES = split_sheet(GFX['tiles'], (128, 128), 6, 6)


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
    x = math.floor(((x + TS2 - 1)/TS2))*TS2
    y = math.floor(((y + TS2 - 1)/TS2))*TS2
    return [x, y]


class Cursor(pg.sprite.DirtySprite):

    """docstring for Wall"""

    def __init__(self, pos,  *groups):
        super(Cursor, self).__init__(*groups)
        self.pos = pos
        self.image = pg.Surface((20, 20))
        self.image.fill((255, 255, 255))

        self.rect = self.image.get_rect(topleft=self.pos)
        self.layer = 1
        self.angle = 0
        self.x, self.y = 0, 0

    def update(self, viewport):
        x1, y1 = pg.mouse.get_pos()
        x2, y2 = viewport.rect.topleft
        self.rect.center = (x1+x2, y1+y2)
        self.x, self.y = self.rect.topleft


class Wall(pg.sprite.DirtySprite):

    """docstring for Wall"""

    def __init__(self, pos, i, j, w, h, *groups):
        super(Wall, self).__init__(*groups)
        self.pos = pos
        # indixes for the wall matriz
        self.i = i
        self.j = j

        if (i == 0 and j == 0):
            self.image = TILES[1][0]
        elif i < w-1 and j == 0:
            self.image = TILES[1][1]
        elif i == w - 1 and j == 0:
            self.image = TILES[1][2]
        elif j > 0 and j < h-1 and i == 0:
            self.image = TILES[2][0]
        elif j > 0 and j < h-1 and i == w-1:
            self.image = TILES[2][2]
        elif j == h-1 and i == 0:
            self.image = TILES[3][0]
        elif j == h-1 and i == w-1:
            self.image = TILES[3][2]
        else:
            self.image = TILES[3][1]
        self.rect = self.image.get_rect(topleft=self.pos)
        self.layer = 1
        self.need_fix = False


class Door(pg.sprite.DirtySprite):

    """docstring for Wall"""

    def __init__(self, pos, i, j, w, h, * groups):
        super(Door, self).__init__(*groups)
        self.pos = pos
        if j == 0 or j == h-1:
            self.normal_image = TILES[0][0]
            self.open_image = TILES[0][1]
            self.locked_image = TILES[1][4]
        elif i == 0:
            self.normal_image = TILES[0][5]
            self.open_image = TILES[0][4]
            self.locked_image = TILES[1][5]
        else:
            self.normal_image = TILES[0][3]
            self.open_image = TILES[0][2]
            self.locked_image = TILES[2][5]
        self.image = self.normal_image
        self.rect = self.image.get_rect(topleft=self.pos)
        self.layer = 1
        self.locked = False
        self.opened = False
        self.room = None

    def open(self):
        self.opened = True
        self.image = self.open_image

    def lock(self):
        self.locked = True
        self.image = self.locked_image
        self.dirty = 1

    def unlock(self):
        self.locked = False
        if self.opened:
            self.image = self.open_image
        else:
            self.image = self.normal_image
        self.dirty = 1


class Hallway(pg.sprite.DirtySprite):

    """docstring for Wall"""

    def __init__(self, rect, *groups):
        super(Hallway, self).__init__(*groups)
        self.pos = list(rect.topleft)
        self.image = pg.Surface((abs(rect.w), abs(rect.h)))
        for x in range(rect.w//TS2):
            for y in range(rect.h//TS2):
                self.image.blit(TILES[1][3], (x*TS2, y*TS2))

        self.rect = rect
        self.layer = 1


class Cell(pg.sprite.DirtySprite):

    """docstring for RandRoom"""

    def __init__(self, *groups):
        super(Cell, self).__init__(*groups)
        self.pos = [0, 0]
        self.pos[0] = GRID[0]*TILE_SIZE/4
        self.pos[1] = GRID[0]*TILE_SIZE/4
        x, y = get_random_point_in_circle(40*TILE_SIZE, 10)
        self.pos[0] += x
        self.pos[1] += y
        w = random.choice(range(TS2, TS2*MAX_ROOM_W, TS2))
        h = random.choice(range(TS2, TS2*MAX_ROOM_H, TS2))
        self.color = [100, 100, 100]
        self.image = pg.Surface((w, h))
        self.image.fill(self.color)

        self.rect = self.image.get_rect(topleft=self.pos)
        self.seleted = False
        self.spawed = False
        self.layer = 1
        self.figthing = False

        self.doors = []

    def generate_image(self):
        for x in range(self.rect.w//TS2):
            for y in range(self.rect.h//TS2):
                self.image.blit(TILES[1][3], (x*TS2, y*TS2))

    def spaw_enemies(self):
        if not self.spawed:
            enemies = random.randint(3, MAX_ROOM_H)
            for i in range(enemies):
                x = random.randint(self.rect.left+TS2, self.rect.right-TS2)
                y = random.randint(self.rect.top+TS2, self.rect.bottom-TS2)
                e = Enemie((x, y))
                e.add(ENEMIES_GROUP, ALL_SPRITES)
            self.spawed = True
            for d in self.doors:
                d.lock()
            self.figthing = True
            print("Enemies in this room %s" % enemies)

    def update(self):
        if self.figthing:
            if len(ENEMIES_GROUP) == 0:
                for d in self.doors:
                    d.unlock()
                    self.figthing = False


class Dugeon(object):

    """docstring for Dugeon"""

    def __init__(self):
        super(Dugeon, self).__init__()
        self.cells_count = 100
        self.rooms_group = pg.sprite.LayeredDirty()
        self.doors_group = pg.sprite.LayeredDirty()
        self.backgound = pg.sprite.LayeredDirty()
        self.visible_sprites = pg.sprite.LayeredDirty()

        self.doors = []
        self.cells = []
        while(len(self.cells) < self.cells_count):
            c = Cell()
            self.cells.append(c)
        self.rooms = self.select_main_rooms(self.cells)
        area, min_x, min_y = self.separate_cells(self.rooms)

        print("Dugeon dimentions With: %s  Heigth: %s" % area)

        w = area[0] + MAX_ROOM_W*TS2 + TS2
        h = area[1] + MAX_ROOM_H*TS2 + TS2
        self.image = pg.Surface((w, h))
        self.image.fill((0, 0, 0))
        self.bg_image = pg.Surface((SCREEN_RECT.w, SCREEN_RECT.h))
        self.bg_image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.clip_rooms(min_x, min_y)
        self.halls = self.connet_rooms(self.rooms)

        self.initial_room = random.choice(self.rooms)
        self.initial_room.spawed = True

        self.walls = []
        self.make_walls()
        # self.remove_useless_doors()
        self.fix_walls()

        self.player = Player(self.initial_room.rect.center, ALL_SPRITES)
        self.viewport = Viewport()
        self.viewport.update(self.player, self.rect)

        # Custom Cursor
        pg.mouse.set_visible(False)
        self.cursor = Cursor((0, 0), ALL_SPRITES)
        self.cursor.update(self.viewport)
        ALL_SPRITES.change_layer(self.cursor, 9)

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
                    if a.rect.colliderect(b.rect.inflate(TS4, TS4)):
                        touching = True
                        dx = min(
                            a.rect.right-b.rect.left+TS4,
                            a.rect.left-b.rect.right-TS4)
                        dy = min(
                            a.rect.bottom-b.rect.top+TS4,
                            a.rect.top-b.rect.bottom-TS4)
                        if (abs(dx) < abs(dy)):
                            dy = 0
                        else:
                            dx = 0

                        dxa = -dx / 2
                        dxb = dx + dxa
                        dya = -dy / 2
                        dyb = dy + dya

                        dxa = math.floor(
                            ((dxa + TS4 - 1)/TS4))*TS4
                        dxb = math.floor(
                            ((dxb + TS4 - 1)/TS4))*TS4
                        dya = math.floor(
                            ((dya + TS4 - 1)/TS4))*TS4
                        dyb = math.floor(
                            ((dyb + TS4 - 1)/TS4))*TS4

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
        return area, min_x, min_y

    def select_main_rooms(self, cells):
        seleted = []
        for room in cells:
            if(room.rect.w > MIN_ROOM_W*TS2
                    and room.rect.h > MIN_ROOM_H*TS2):
                room.seleted = True
                room.generate_image()
                seleted.append(room)
                room.add(ALL_SPRITES, self.rooms_group, self.backgound)

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
        # A always left o B
        if(p1[0] < p2[0]):
            a = p1
            b = p2
        else:
            a = p2
            b = p1
        a = list(a)
        b = list(b)
        w = h = TS2
        # magic o make the perfect centered hallways
        a[0] -= TILE_SIZE
        a[1] -= TILE_SIZE
        b[0] -= TILE_SIZE
        b[1] -= TILE_SIZE
        a[0] = math.floor(((a[0] + TS2 - 1)/TS2))*TS2
        a[1] = math.floor(((a[1] + TS2 - 1)/TS2))*TS2
        b[0] = math.floor(((b[0] + TS2 - 1)/TS2))*TS2
        b[1] = math.floor(((b[1] + TS2 - 1)/TS2))*TS2

        clockwise = random.randint(0, 1) == 1
        dx = b[0] - a[0]
        # A avobe B
        if (a[1] < b[1]):
            dy = b[1] - a[1]
            if clockwise:
                r1 = pg.Rect(a[0], a[1], dx+w, h)
                r2 = pg.Rect(b[0], a[1], w, dy)
            else:
                r1 = pg.Rect(a[0], a[1], w, dy+h)
                r2 = pg.Rect(a[0], b[1], dx+w, h)
        else:
            dy = a[1] - b[1]
            if clockwise:
                r1 = pg.Rect(b[0], b[1], w, dy+h)
                r2 = pg.Rect(a[0], a[1], dx+w, h)
            else:
                r1 = pg.Rect(a[0], b[1], dx+w, h)
                r2 = pg.Rect(a[0], b[1], w, dy+h)

        h1 = Hallway(r1, ALL_SPRITES, self.backgound)
        h2 = Hallway(r2, ALL_SPRITES, self.backgound)
        return [h1, h2]

    def clip_rooms(self, min_x, min_y):
        for r in self.rooms:
            r.pos[0] += abs(min_x) + TS2
            r.pos[1] += abs(min_y) + TS2
            r.rect.topleft = r.pos

    def make_walls(self):
        for room in self.rooms:
            x, y = room.rect.topleft
            w = int(room.rect.w/TS2)
            h = int(room.rect.h/TS2)
            old_hall = None
            for i in range(w):
                for j in range(h):
                    if (j > 0 and j < h-1)and (i > 0 and i < w - 1):
                        y += TS2
                        continue
                    wall = Wall((x, y), i, j, w, h)
                    hit_walls = pg.sprite.spritecollideany(wall, self.walls)
                    hit_rooms = pg.sprite.spritecollideany(
                        wall, self.rooms_group)
                    if not hit_walls or not hit_rooms:
                        hall = pg.sprite.spritecollideany(wall, self.halls)
                        if hall:
                            if old_hall != hall:
                                door = Door((x, y), i, j, w, h)
                                door.add(self.doors_group, ALL_SPRITES)
                                ALL_SPRITES.change_layer(door, 6)
                                self.doors.append(door)
                                door.room = room
                                room.doors.append(door)
                                old_hall = hall
                        else:
                            self.walls.append(wall)
                            ALL_SPRITES.add(wall)
                    y += TS2
                x += TS2
                y = room.rect.top
        for hall in self.halls:
            x, y = hall.rect.topleft
            x -= TS2
            y -= TS2
            w = int(hall.rect.w/TS2) + 2
            h = int(hall.rect.h/TS2) + 2
            for i in range(w):
                for j in range(h):
                    if (j > 0 and j < h-1)and (i > 0 and i < w - 1):
                        y += TS2
                        continue
                    wall = Wall((x, y), i, j, w, h)
                    if not pg.sprite.spritecollideany(wall, ALL_SPRITES):
                        self.walls.append(wall)
                        ALL_SPRITES.add(wall)
                        ALL_SPRITES.change_layer(wall, 3)
                    else:
                        old_wall = pg.sprite.spritecollideany(wall, self.walls)
                        if old_wall:
                            old_wall.need_fix = True

                    y += TS2
                x += TS2
                y = hall.rect.top-TS2

    def remove_useless_doors(self):
        for i in range(len(self.doors)):
            a = self.doors[i]
            a.rect.inflate_ip(TS2, 0)
            walls_around = pg.sprite.spritecollide(a, self.walls, False)
            a.rect.inflate_ip(-TS2, TS2)
            if len(walls_around) < 2:
                walls_around = pg.sprite.spritecollide(a, self.walls, False)
                if len(walls_around) < 2:
                    a.kill()
                    continue
            a.rect.inflate_ip(TS2, 0)
            for j in range(i+1, len(self.doors)):
                b = self.doors[j]
                if pg.sprite.collide_rect(a, b) and not b.locked:
                    b.kill()
            a.rect.inflate_ip(-TS2, -TS2)

    def fix_walls(self):
        pass
        # a = self.walls[0]
        # a.rect.inflate_ip(TS2, TS2)
        # walls_around = pg.sprite.spritecollide(a, self.walls, False)
        # for w in walls_around:
        # a.rect.inflate_ip(-TS2, -TS2)

    def handle_input(self, event):
        self.player.handle_input(event)
        # if event.type == pg.MOUSEMOTION:
        #     print(x1+x2, y1+y2)

    def update(self, dt):
        visible_walls = pg.sprite.spritecollide(
            self.viewport, self.walls, False)
        self.player.update(dt, self.walls, self.doors_group, self.cursor)
        self.viewport.update(self.player, self.rect)
        self.cursor.update(self.viewport)
        # BULLETS_GROUP.update(dt)
        ENEMIES_GROUP.update(dt, self.player)
        self.rooms_group.update()

        visible_sprites = pg.sprite.spritecollide(
            self.viewport, ALL_SPRITES, False)
        self.visible_sprites.add(visible_sprites)
        for sprite in self.visible_sprites.sprites():
            if not sprite in self.backgound:
                self.visible_sprites.change_layer(sprite, sprite.rect.centery)
            else:
                self.visible_sprites.change_layer(sprite, sprite.layer)

            self.visible_sprites.change_layer(self.cursor, 9999)

            if sprite not in visible_sprites:
                self.visible_sprites.remove(sprite)

    def render(self, surface):
        # ALL_SPRITES.repaint_rect(self.viewport)
        self.image.blit(self.bg_image, (self.viewport.rect))
        self.visible_sprites.draw(self.image)
        BULLETS_GROUP.draw(self.image)
        ENEMIES_GROUP.draw(self.image)
        DECORATOR_GROUP.draw(self.image)
        surface.blit(self.image, (0, 0), self.viewport)
        self.viewport.render(surface)


class Viewport(object):

    """docstring for viewport"""

    def __init__(self):
        self.rect = SCREEN_RECT.copy()
        self.image = pg.Surface((self.rect.w, self.rect.h))
        self.image.fill((0, 0, 0))
        # self.image.set_alpha(100)

    def update(self, player, screen_rect):
        self.rect.center = player.rect.center
        self.rect.clamp_ip(screen_rect)

    def render(self, surface):
        # surface.blit(self.image, (0, 0))
        pass
