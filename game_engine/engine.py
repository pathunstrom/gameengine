import logging
import time
from typing import Type

import pygame

from game_engine.abc import Engine, Scene


class GameEngine(Engine):

    def __init__(self, first_scene: Type, **kwargs):
        super(GameEngine, self).__init__()

        # Engine Configuration
        self.delta_time = kwargs.get("delta_time", 0.016)
        self.resolution = kwargs.get("resolution", (600, 400))
        self.flags = kwargs.get("flags", 0)
        self.depth = kwargs.get("depth", 0)
        self.log_level = kwargs.get("log_level", logging.WARNING)
        self.first_scene = first_scene
        logging.basicConfig(level=self.log_level)

        # Engine State
        self.scenes = []
        self.unused_time = 0
        self.last_tick = None
        self.running = False
        self.display = None

    def __enter__(self):
        logging.getLogger(self.__class__.__name__).info("Entering context.")
        pygame.init()
        self.display = pygame.display.set_mode(self.resolution,
                                               self.flags,
                                               self.depth)
        self.update_input()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.getLogger(self.__class__.__name__).info("Exiting context")
        pygame.quit()

    def run(self):
        self.running = True
        self.last_tick = time.time()
        self.scenes.append(self.first_scene(self))
        while self.running:
            scene = self.current_scene  # type: Scene
            if scene is None or scene.quit:
                return
            if not scene.running:
                self.scenes.pop()
            if scene.next is not None:
                self.scenes.append(scene.next())
                scene.next = None
            scene.render()
            pygame.display.update()
            tick = time.time()
            new_time = tick - self.last_tick
            self.unused_time += new_time
            self.last_tick = tick
            while self.unused_time >= self.delta_time:
                for event in pygame.event.get():
                    scene.handle_event(event)
                self.update_input()
                scene.simulate(self.delta_time)
                self.unused_time -= self.delta_time

    @property
    def current_scene(self):
        try:
            return self.scenes[-1]
        except IndexError:
            return None

    def update_input(self):
        self.mouse["x"], self.mouse["y"] = pygame.mouse.get_pos()
        self.mouse[1], self.mouse[2], self.mouse[3] = pygame.mouse.get_pressed()
