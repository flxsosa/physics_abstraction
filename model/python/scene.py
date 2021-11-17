import os
import pygame
import pymunk
import pymunk.pygame_util
import handlers
from main import *
import math
from pygame.locals import *
from pygame.color import *
from numpy.random import normal, randint
from handlers import *
from random import randrange
from helper import rotate

class Scene:
    def __init__(self, handlers=None, objects=None, obj_params=None, wh=(0,0)):
        # Object parameters
        self._objects = objects
        self._object_args = obj_params
        self.goal = 0
        # Scene parameters
        self.width, self.height = wh
        # Global parameters
        self.running = False
        self.step = False
        self.fps = 60
        self.gravity = (0,150)
        self.objects = None
        self.space = pymunk.Space()
        self.space.gravity = self.gravity
        self.screen = None
        self.clock = None
        self.draw_options = None
        self.coll_handlers = [h for h in handlers] if handlers else None
        self.draw_params = {}
        self.instantiated = False
        # Simulation parameters
        self.stopping_epsilon = 1e-2
        self.tick = 0
        self.ball_pos = None
        self.stopping_timer = 0
        self.goal_ball_collision = False
        self.trajectories = {
            "collision":False,
            "ball":[],
            "ticks":0}

    def instantiate_hamrick(self,func=None,*args):
        '''
        Wrapping functions and their args in *args operator
        '''
        self.width, self.height = 900, 650
        GameBorder2(self.space,p0=(10, 10), p1=(self.width-10, self.height-10))
        objs = []
        self.draw_params['color_ball']=pygame.Color(randrange(256),
                                                    randrange(256),
                                                    randrange(256))
        self.draw_params['color_goal']=pygame.Color(randrange(256),
                                                    randrange(256),
                                                    randrange(256))
        
        # Funcs and args; allowing for additions
        if args:
            funcs,fargs=self._objects+args[0],self._object_args+args[1]
        else:
            funcs,fargs=self._objects,self._object_args
        # Call funcs with their respective args
        for i in range(len(funcs)):
            print(funcs[i])
            print(*fargs[i])
            obj = funcs[i](*fargs[i])
            objs.append(obj)
            if func: 
                func[0](obj)
            if type(obj).__name__ == "Ball":
                self.force_obj = obj      
            self.space.add(*obj.components)
        self.objects = objs
        # if func: func[0](self.objects)
        self.instantiated = True

    def instantiate_scene(self,func=None,*args):
        '''
        Wrapping functions and their args in *args operator
        '''
        border = PlinkoBorder((self.width, self.height))
        self.space.add(*border.components)
        objs = [border]
        self.draw_params['color_ball']=pygame.Color(randrange(156),
                                                    randrange(156),
                                                    randrange(156))
        self.draw_params['color_goal']=pygame.Color(randrange(156),
                                                    randrange(156),
                                                    randrange(156))
        
        # Funcs and args; allowing for additions
        if args:
            funcs,fargs=self._objects+args[0],self._object_args+args[1]
        else:
            funcs,fargs=self._objects,self._object_args
        # Call funcs with their respective args
        for i in range(len(funcs)):
            obj = funcs[i](*fargs[i])
            objs.append(obj)
            if func: 
                func[0](obj)
            self.space.add(*obj.components)
        self.objects = objs
        self.instantiated = True

    def instantiate_handlers(self):
        if self.coll_handlers:
            for obj1, obj2, rem in self.coll_handlers:
                ch = self.space.add_collision_handler(obj1, obj2)
                ch.data["surface"] = self.screen
                ch.post_solve = rem
        else:
            return

    def draw(self,random_color=True):
        self.screen.fill(pygame.Color("gray"))
        # self.space.debug_draw(self.draw_options)
        for o in self.objects:
            # Drawing the ball
            if type(o).__name__ == "Ball":
                color = self.draw_params['color_ball'] if random_color else o.shape.color
                pygame.draw.circle(self.screen, color, o.body.position, o.radius)
            # Drawing the goal
            elif type(o).__name__ == "Goal":
                color = self.draw_params['color_goal'] if random_color else o.shape.color
                r = pygame.Rect(0,0,o.l+1,o.w+1)
                r.center = o.body.position
                pygame.draw.rect(self.screen, color, r)
            # Drawing border and containers
            else:
                color = pygame.Color("black")
                # We skip the first element in the components because that's the body
                for line in o.components[1:]:
                    # Grab the body
                    body = o.components[0]
                    # Offset for sprites
                    offset = body.position
                    # Rotate the sprites
                    a = rotate(body, line.a)
                    b = rotate(body, line.b)
                    # Draw
                    pygame.draw.line(self.screen, color, a+offset, b+offset,5)
        # Update display
        pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN and (event.key in [K_q, K_ESCAPE]):
                self.running = False
            elif event.type == KEYDOWN and (event.key in [K_SPACE]):
                self.step = not self.step
        if handlers.GOAL_BALL:
            self.running=False
            self.goal_ball_collision = True

    def apply_forces(self,obj,direction=(0,650)):
        velocity = 100
        if obj.body.velocity.length < velocity:
            direction = direction - obj.body.position
            direction = direction.normalized()
            direction = direction.normalized()
            impulse = (velocity - obj.body.velocity.length)*direction
            obj.body.apply_impulse_at_local_point(impulse)

    def record(self,end):
        if end:
            self.trajectories['collision'] = True
            self.trajectories['ticks'] = self.tick
            self.trajectories['objects'] = [o.__name__ for o in self._objects]
            self.trajectories['object_params'] = self._object_args
        else:
            for i in range(len(self.objects)):
                if type(self.objects[i]).__name__ == "Ball":
                    ball = self.objects[i]
            self.trajectories['ball'].append((ball.body.position[0],ball.body.position[1]))

    def listen(self):
        for o in self.objects:
            if type(o).__name__ == "Ball":
                if not self.ball_pos:
                    self.ball_pos = o.body.position
                    continue
                diff = math.sqrt((o.body.position[0] - self.ball_pos[0])**2+
                                (o.body.position[1] - self.ball_pos[1])**2)
                self.ball_pos = o.body.position
                if diff < self.stopping_epsilon and self.tick > 10:
                    self.stopping_timer += 1
                    if self.stopping_timer > 50:
                        self.running = False

    def forward(self, view=True, img_capture=False, fname="scene"):
        # Create callable instances of pymunk and pygame components
        if view:
            pygame.init()
            self.screen = pygame.display.set_mode((self.width,self.height))
            self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
            self.clock = pygame.time.Clock()
            self.screen.fill(pygame.Color("gray"))
        
        self.running = True
        # Create callable scene components
        if not self.instantiated:
            self.instantiate_scene()
        # Collision handlers
        self.instantiate_handlers()
        # Simulate
        while self.running:
            self.events()
            self.draw()
            if self.step:
                self.listen()
                self.tick += 1
                self.record(False)
            self.clock.tick(self.fps)
            dt = 1./self.fps
            if self.step: self.space.step(dt)
            if img_capture:
                pygame.image.save(self.screen,fname+".jpg")
                self.running=False
        self.record(True)
        # Reset after simulation
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
        self.instantiated = False