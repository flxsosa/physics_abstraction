import pygame
import pymunk
import pymunk.pygame_util
import handlers
from main import *
from pygame.locals import *
from pygame.color import *
from numpy.random import normal
from handlers import *
from random import randrange

class Scene:
    def __init__(self, handlers=None, *args):
        # Global parameters
        self.running = False
        self.step = False
        self.fps = 60
        self.width, self.height = 812,1012
        self.gravity = (0,150)
        self._objects = args[0]
        self._object_args = args[1]
        self.objects = None
        self.space = pymunk.Space()
        self.space.gravity = self.gravity
        self.screen = None
        self.clock = None
        self.draw_options = None
        self.coll_handlers = [h for h in handlers] if handlers else None
        self.goal = 0
        self.draw_params = {}

    def instantiate_scene(self,*args):
        '''
        Wrapping functions and their args in *args operator
        '''
        GameBorder(self.space)
        objs = []
        self.draw_params['color_ball']=pygame.Color(randrange(256),randrange(256),randrange(256))
        self.draw_params['color_goal']=pygame.Color(randrange(256),randrange(256),randrange(256))
        # Funcs and args; allowing for additions
        if args:
            funcs,fargs=self._objects+args[0],self._object_args+args[1]
        else:
            funcs,fargs=self._objects,self._object_args
        # Call funcs with their respective args
        for i in range(len(funcs)):
            obj = funcs[i](*fargs[i])
            objs.append(obj)
            self.space.add(*obj.components)
        self.objects = objs
    
    def instantiate_handlers(self):
        if self.coll_handlers:
            for obj1, obj2, rem in self.coll_handlers:
                ch = self.space.add_collision_handler(obj1, obj2)
                ch.data["surface"] = self.screen
                ch.post_solve = rem
        else:
            return

    def draw(self,random_color=True):
        for o in self.objects:
            if type(o).__name__ == "Ball":
                color = self.draw_params['color_ball'] if random_color else o.shape.color
                pygame.draw.circle(self.screen, color, o.body.position, o.radius+1)
            elif type(o).__name__ == "Goal":
                color = self.draw_params['color_goal'] if random_color else o.shape.color
                r = pygame.Rect(0,0,o.l+1,o.w+1)
                r.center = o.body.position
                pygame.draw.rect(self.screen, color, r)

    def forward(self, view=True, img_capture=False, fname="scene"):
        # Create callable instances of pymunk and pygame components
        if view:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width,self.height))
            self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
            self.clock = pygame.time.Clock()
        
        self.running = True
        # Create callable scene components
        self.instantiate_scene()
        # Collision handlers
        self.instantiate_handlers()
        # Simulate
        while self.running:
            for event in pygame.event.get():
                if event.type == KEYDOWN and (event.key in [K_q, K_ESCAPE]):
                    self.running = False
                elif event.type == KEYDOWN and (event.key in [K_SPACE]):
                    self.step = True
            self.screen.fill(pygame.Color("gray"))
            self.space.debug_draw(self.draw_options)
            self.draw()
            # pygame.draw.circle(self.screen, pygame.Color("blue"), (200,200), 30)
            dt = 1./self.fps
            if self.step:
                self.space.step(dt)
            pygame.display.flip()
            if img_capture:
                pygame.image.save(self.screen,fname+".jpg")
                self.running=False
            self.clock.tick(self.fps)
        self.reset()

    def forward_stochastic(self,view=True):
        # Create callable instances of pymunk and pygame components
        if view:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width,self.height))
            self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
            self.draw_options.shape_outline_color = self.draw_options.shape_dynamic_color
            self.clock = pygame.time.Clock()
        
        self.running = True
        # Create callable scene components
        self.instantiate_scene()
        self.instantiate_handlers()
        # Perturb starting posiiton of Ball
        x,y = self.space.bodies[0].position
        x = x*normal(1,0.3)
        if x < 20+10+2: # ball radius and border and border radius
            x = 32
        self.space.bodies[0].position = x,y
        # Simulate
        while self.running and not(handlers.END_STATE):
            
            dt = 1./self.fps
            if self.step or not(view):
                self.space.step(dt)

            if view:
                self.screen.fill(THECOLORS["gray"])
                self.space.debug_draw(self.draw_options)
                pygame.display.flip()
                self.clock.tick(self.fps)
                for event in pygame.event.get():
                    if event.type == KEYDOWN and (event.key in [K_q, K_ESCAPE]):
                        self.running = False
                    elif event.type == KEYDOWN and (event.key in [K_SPACE]):
                        self.step = True

        self.reset()
        if handlers.GOAL_BALL:
            self.goal+=1
        handlers.GOAL_BALL = []
        handlers.END_STATE = []
    
    def reset(self):
        pygame.quit()
        self.step = False
        self.space = pymunk.Space()
        self.space.gravity = self.gravity
        self.screen = None
        self.clock = pygame.time.Clock()
        self.draw_options = None