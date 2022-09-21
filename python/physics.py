# For Physics and Object
import pymunk
from handlers import is_colliding
from pymunk.vec2d import Vec2d
# For Graphics
from pygame.locals import *
from pygame.color import *
from math import cos,sin
# For abstraction
from math import cos, sin


class Physics:
    '''
    A Physics is a dynamics applied to a Scene to evolve the 
    Scene over time.
    '''
    def __init__(self,fps=60):
        # Space in which Pymunk objects reside
        self.space = pymunk.Space()
        self.space.gravity = (0,300) # Gravit
        self.space.damping = 0.6 # Simulated "fRiCtiOn"
        self.dt = 1./fps
        self.tick = 0
        self.handlers = {}
        self.instantiate_handlers() # Instantiate collision handlers
        
    def instantiate_handlers(self,args=None):
        '''
        Instantiate collision handlers.
        '''
        # Ball and goal
        self.handlers["ball_goal"] = self.space.add_collision_handler(0,1)
        self.handlers["ball_goal"].data['colliding'] = False
        self.handlers["ball_goal"].data['collision_trace'] = []
        self.handlers['ball_goal'].data['normal'] = Vec2d(0,0)
        self.handlers["ball_goal"].post_solve = is_colliding

        # Ball and floor
        self.handlers["ball_floor"] = self.space.add_collision_handler(0,2)
        self.handlers["ball_floor"].data['colliding'] = False
        self.handlers["ball_floor"].data['collision_trace'] = []
        self.handlers['ball_floor'].data['normal'] = Vec2d(0,0)
        self.handlers["ball_floor"].post_solve = is_colliding

        # Ball and containers
        self.handlers["ball_container"] = self.space.add_collision_handler(0,3)
        self.handlers["ball_container"].data['colliding'] = False
        self.handlers['ball_container'].data['collision_trace'] = []
        self.handlers['ball_container'].data['normal'] = Vec2d(0,0)
        self.handlers["ball_container"].post_solve = is_colliding

    def collision_end(self):
        '''
        Outputs data from handlers for Scene to use
        '''
        rval = self.handlers["ball_goal"].data['colliding']
        rval += self.handlers["ball_floor"].data['colliding']
        return rval
    
    def forward(self):
        '''
        Forward method for the physics. Evolves PObjects over time
        according to a dynamics.
        '''
        self.space.step(self.dt)
        self.tick += 1 

    def abstraction(self):
        '''
        Outputs data from handlers for Scene to use
        '''
        rval = self.handlers["sensor_goal"].data['colliding']
        rval += self.handlers["sensor_floor"].data['colliding']
        rval *= not self.handlers['sensor_container'].data['colliding']
        return rval
