import pygame
from pygame.locals import *
import abstraction
import json
from listener import Listener

class Scene:
    '''
    A Scene is a tuple of PObjects, Physics, and Graphics
    '''
    def __init__(self, physics, objects, graphics, args=None):
        self.physics = physics
        self.objects = objects
        self.graphics = graphics
        self.running = True
        # Probability of collision between Ball and Goal
        self.collision_prob = None
        # Tick samples from stochastic runs
        self.tick_samples = []
        # Flag for user to pause simulation
        self.pause = False
        self.sensor_obj = None
        self.trace = []
        if args:
            with open(args, 'r') as f:
                self.args = json.loads(f.read())
        else:
            self.args = None
    
    def event(self):
        '''
        Event handler for pygame events, such as keyboard events.
        '''
        for event in self.graphics.framework.event.get():
            if event.type == KEYDOWN and (event.key in [K_q, K_ESCAPE]):
                self.running = False
            elif event.type == KEYDOWN and (event.key in [K_SPACE]):
                self.pause = not self.pause
            elif event.type == self.graphics.framework.MOUSEBUTTONUP:
                pos = self.graphics.framework.mouse.get_pos()
                for o in self.objects:
                    if o.name == "Ball":
                        o.body.position = pos
                        o.body.velocity = (0,0)

    def run_path(self,view=True,N=None,D=None,E=None):
        '''
        Forward method for the scene. Evolves PObjects over time according
        to a Physics and renders the simulation to the screen with a Graphics
        '''
        epsilon = E
        if view and not self.graphics.initialized:
            self.graphics.initialize_graphics()
        while self.running:
            # Get projected path and end positio of path
            ball_pos_pp, valid_pp = abstraction.path_projection(self.objects,self.physics,D)
            # Step simulator forward N times
            for _ in range(int(N)):
                # Physics
                self.physics.forward()
                # self.running *= not self.listener.listen()
                self.running *= not self.physics.collision_end()
                self.running *= self.graphics.running
                self.running *= self.physics.tick < 1000
                if view:
                    self.graphics.draw(self.objects)
                    self.graphics.draw_circle_at_point(ball_pos_pp)
                    for o in self.objects:
                        if o.name == "Ball":
                            pos = o.body.position
                    pygame.draw.line(self.graphics.screen, pygame.Color("Black"), ball_pos_pp, pos,5)
                    self.graphics.clock.tick(self.graphics.fps)
                    self.graphics.update_display()
            if self.physics.tick > 5000:
                self.running = False
                # print(self.running)
                self.physics.tick = 1e5
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

    def run(self,view=True,fname=None,record=False,dir=None):
        '''
        Forward method for the scene. Evolves PObjects over time according
        to a Physics and renders the simulation to the screen with a Graphics
        '''
        if record:
            if dir:
                camera = self.graphics._record_screen(dir,fname)
            else:
                ValueError("No directory given")
        if view and not self.graphics.initialized:
            self.graphics.initialize_graphics()
        while self.running:
            # Physics
            if not self.pause:
                for o in self.objects:
                    if o.name == "Ball":
                        self.trace.append(o.body.position)
                self.physics.forward()
                self.running *= not self.physics.collision_end()
                self.running *= self.graphics.running
            if self.physics.tick > 1000:
                self.running = False
            # Graphics
            if view:
                self.graphics.draw(self.objects,self.physics.tick)
                self.graphics.clock.tick(self.graphics.fps)
                if self.graphics.draw_params.get('collision_normal'):
                    collision_normals = self.physics.handlers['ball_container'].data
                    self.graphics.draw_collision_normals(collision_normals)
                self.graphics.update_display()
                if record:
                    next(camera)
                # User Events
                self.event()

    def instantiate_scene(self):
        for obj in self.objects:
            self.physics.space.add(*obj.components)
            if obj.name == "Ball":
                self.listener = Listener(obj.body)
