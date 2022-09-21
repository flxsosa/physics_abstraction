# For Physics and Object
import pymunk
# For Graphics
import pygame
from pygame.locals import *
from pygame.color import *
from pymunk.pygame_util import to_pygame
from math import cos,sin
# For general
from random import randrange
# For abstraction
from math import cos, sin
import abstraction
import objects
from helper import draw_circle_alpha

class SceneBuilder(Scene):
    '''
    Convenience class for using the mouse to build Scenes
    '''

    def __init__(self, physics, objects, graphics):
        super().__init__(physics,objects,graphics)
        self.pos1 = None
        self.pos2 = None
        self.brush = None
        self.step = False
        self.starting_pos = None
        self.object_record = []
        self.object_arg_record = {
            'ball_args':None,
            'goal_args':None,
            'line_args':[]
        }
        self.shape = None

    def print_args(self):
        print([obj.name for obj in self.objects])
        print(self.object_arg_record)

    def save_args(self, dir='../data/json/test/'):
        '''
        Record arguments for a Scene and end state of the Scene into
        a JSON.
        '''
        import json
        name = input("Name the scene: ")
        record = {}
        record['name'] = name
        record['screen_size'] = self.graphics.screen_size
        record['tick'] = None
        record['objects'] = [obj.name for obj in self.objects]
        for key in self.object_arg_record.keys():
            record[key] = self.object_arg_record[key]
        with open(dir+name+'.json', 'w') as f:
            json.dump(record, f)

    def set_brush(self,pos):
        if self.brush == 'c':
            if not self.pos1:
                self.pos1 = pos
            else:
                self.pos2 = pos
                obj = objects.Line(self.pos1,self.pos2)
                self.objects.append(obj)
                self.object_record = (objects.Line)
                self.object_arg_record['line_args'].append([self.pos1,self.pos2])
                self.physics.space.add(*obj.components)
                self.pos1, self.pos2 = None, None
        elif self.brush == 'b':
            if self.object_arg_record['ball_args'] == None:
                obj = objects.Ball(pos)
                self.objects.append(obj)
                self.object_record = (objects.Ball)
                self.object_arg_record['ball_args']= [pos]
                self.physics.space.add(*obj.components)
            else:
                for obj in self.objects:
                    if obj.name == "Ball":
                        obj.body.position = pos
                        self.object_arg_record['ball_args'] = [pos]
        elif self.brush == 'g':
            if self.object_arg_record['goal_args'] == None:
                obj = objects.Goal((pos[0],1000))
                self.objects.append(obj)
                self.object_record = (objects.Goal)
                self.object_arg_record['goal_args']= [(pos[0],1000)]
                self.physics.space.add(*obj.components)
            else:
                for obj in self.objects:
                    if obj.name == "Goal":
                        obj.body.position = (pos[0],1000)
                        self.object_arg_record['goal_args'] = [(pos[0],1000)]

    def event(self):
        '''
        Event handler for pygame events, such as keyboard events.
        '''
        for event in self.graphics.framework.event.get():
            if event.type == KEYDOWN and (event.key in [K_q, K_ESCAPE]):
                self.running = False
            elif event.type == KEYDOWN and (event.key in [K_SPACE]):
                self.step = not self.step
            elif event.type == KEYDOWN and (event.key in [K_c]):
                self.brush = 'c'
            elif event.type == KEYDOWN and (event.key in [K_b]):
                self.brush = 'b'
            elif event.type == KEYDOWN and (event.key in [K_g]):
                self.brush = 'g'
            elif event.type == KEYDOWN and (event.key in [K_e]):
                for obj in self.objects[2:]:
                    self.physics.space.remove(*obj.components)
                self.objects = self.objects[:2]
                self.object_arg_record = {
                    'ball_args':None,
                    'goal_args':None,
                    'line_args':[]
                }
                self.reset_physics_vars()
            elif event.type == KEYDOWN and (event.key in [K_s]):
                self.save_args()
            elif event.type == KEYDOWN and (event.key in [K_p]):
                self.print_args()
            elif event.type == KEYDOWN and (event.key in [K_t]):
                self.physics.tick = 0
                self.reset_physics_vars()
            elif event.type == self.graphics.framework.MOUSEBUTTONUP:
                pos = self.graphics.framework.mouse.get_pos()
                self.set_brush(pos)
    
    def reset_physics_vars(self):
        self.physics.tick = 0
        for obj in self.objects:
            obj.body.velocity = 0,0
        self.physics.handlers["ball_goal"].data['colliding'] = False
        self.physics.handlers["ball_floor"].data['colliding'] = False

    def run_path(self,view=True):
        '''
        Forward method for the scene. Evolves PObjects over time according
        to a Physics and renders the simulation to the screen with a Graphics
        '''
        N = 35
        epsilon = 0.9
        D = 200
        self.graphics.initialize_graphics()
        while self.running:
            # Get projected path and end positio of path
            ball_pos_pp, valid_pp = abstraction.path_projection(self.objects,self.physics, D)
            # Step simulator forward N times
            for _ in range(N):
                # Physics
                self.physics.forward()
                if view:
                    self.graphics.draw(self.objects)
                    self.graphics.draw_circle_at_point(ball_pos_pp)
                    self.graphics.clock.tick(self.graphics.fps)
                    self.graphics.update_display()
            # Get the ball
            for obj in self.objects:
                if obj.name == "Ball":
                    ball = obj
            # Get end position of simulation run
            ball_pos_sim = ball.body.position
            # Detemrine cosine similaroty between simulation and path projection
            normsim = ball_pos_sim.length
            normpp = ball_pos_pp.length
            dot = ball_pos_sim.dot(ball_pos_pp)
            cossim = dot / (normsim * normpp)
            if cossim > epsilon and valid_pp:
                ball.body.position = ball_pos_pp
                self.physics.space.reindex_shapes_for_body(ball.body)
            # Graphics
            if view:
                self.graphics.draw(self.objects)
                self.graphics.draw_circle_at_point(ball_pos_pp)
                self.graphics.clock.tick(self.graphics.fps)
                self.graphics.update_display()
                # User Events
                self.event()

    def run(self):
        '''
        Forward method for the scene. Evolves PObjects over time according
        to a Physics and renders the simulation to the screen with a Graphics
        '''
        self.graphics.initialize_graphics()
        while self.running:
            if self.step:
                # Physics
                # Check if shape is colliding with anything
                self.physics.forward()
                if self.physics.collision_end():
                    self.step = False
                    self.reset_physics_vars()
            # Graphics
            self.graphics.draw(self.objects)
            self.graphics.clock.tick(self.graphics.fps)
            self.graphics.update_display()
            # User Events
            self.event()

    def instantiate_scene(self):
        # Get the ball
        for obj in self.objects:
            self.physics.space.add(*obj.components)