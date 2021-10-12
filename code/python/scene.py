import pygame
import pymunk
import pymunk.pygame_util
from main import *
from pygame.locals import *
from pygame.color import *

class Scene:
    def __init__(self,*args,r=False,s=False,fps=60,w=800,h=800,g=(0,150)):
        # Global parameters
        self.running = r
        self.step = s
        self.fps = fps
        self.width, self.height = w,h
        self.gravity = g
        self._objects = args[0]
        self._object_args = args[1]
        self.objects = None
        self.space = pymunk.Space()
        self.space.gravity = self.gravity
        self.screen = None
        self.clock = pygame.time.Clock()
        self.draw_options = None

    def instantiate_scene(self,*args):
        '''
        Wrapping functions and their args in *args operator
        '''
        GameBorder(self.space)
        objs = []
        # Funcs and args; allowing for additions
        if args:
            funcs,fargs=self._objects+args[0],self._object_args+args[1]
        else:
            funcs,fargs=self._objects,self._object_args
        # Call funcs with their respective args
        print(self.objects)
        for i in range(len(funcs)):
            obj = funcs[i](*fargs[i])
            objs.append(obj)
            self.space.add(*obj.components)
        self.objects = objs

    def forward(self):
        # Create callable instances of pymunk and pygame components
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((self.width,self.height))
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        # Create callable scene components
        self.instantiate_scene()
        # Simulate
        while self.running:
            for event in pygame.event.get():
                if event.type == KEYDOWN and (event.key in [K_q, K_ESCAPE]):
                    self.running = False
                elif event.type == KEYDOWN and (event.key in [K_SPACE]):
                    self.step = True

            self.screen.fill(THECOLORS["gray"])
            self.space.debug_draw(self.draw_options)
            dt = 1./self.fps
            if self.step:
                self.space.step(dt)
            pygame.display.flip()
            self.clock.tick(fps)
        self.reset()
    
    def reset(self):
        pygame.quit()
        self.step = False
        self.space = pymunk.Space()
        self.space.gravity = self.gravity
        self.screen = None
        self.clock = pygame.time.Clock()
        self.draw_options = None