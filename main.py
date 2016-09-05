import sys

import pygame as pg

from conts import *
from dugeon import Dugeon


class Game:

    def __init__(self):

        self.fps = 30

        self.screen = pg.display.get_surface()
        self.clock = pg.time.Clock()

        self.dugeon = Dugeon()

    def handle_input(self):
        for event in pg.event.get():
            self.dugeon.handle_input(event)
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.KEYUP:
                if event.key == pg.K_p:
                    self.dugeon.show_paths = not self.dugeon.show_paths

    def update(self, dt):
        capition = "Hola mundo - FPS: {:.2f}".format(self.clock.get_fps())
        pg.display.set_caption(capition)
        self.dugeon.update(dt)

    def render(self):
        self.dugeon.render(self.screen)

    def main_loop(self):
        while True:
            dt = self.clock.tick(self.fps)/1000.0
            self.handle_input()
            self.update(dt)
            self.render()

            pg.display.flip()


if __name__ == '__main__':
    g = Game()
    g.main_loop()
