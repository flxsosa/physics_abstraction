# For Physics and Object
import pymunk
from handlers import is_colliding, not_colliding
# For Graphics
import pygame
from pygame.locals import *
from pygame.color import *
from math import cos,sin,sqrt
# For general
from random import randrange
# For abstraction
from math import cos, sin
from abstraction import *

class Listener:
    '''
    Class for monitoring state in Physics, Graphics, PObject,
    etc. To be used by Scene (or whatevs floats the boat) for making
    binary decisions (e.g. if object state < epsilon).
    '''
    def __init__(self, object, epsilon=1):
        '''
        :param object: The object whose state is to be tracked
        '''
        self.object = object
        self.epsilon = 1

    def listen(self):
        '''
        Read the state of the object.
        '''
        return self.object.velocity.length < self.epsilon

    def tick_listen(self):
        '''
        Read how many ticks
        '''
        return self.object.tick

class Graphics:
    '''
    A Graphics renders PObjects onto a screen.
    '''
    def __init__(self,width=800,height=1000,fps=60):
        self.screen_size = width,height
        self.framework = pygame # Making this decoupled because plan to move to 3D
        self.screen = None
        self.size = width,height
        self.clock = None
        self.fps = fps
        self.screen_recorder = None
        self.running = True
        self.initialized = False
        self.debug_options = None
        self.draw_params = {
            'Ball':pygame.Color(randrange(156),randrange(156),randrange(156)),
            'Goal':pygame.Color(randrange(156),randrange(156),randrange(156)),
            'Container':pygame.Color("Black"),
            'Border':pygame.Color("Black"),
            'ball_alpha':False # Flag for whether we're making fading videos or not
            }
    
    def instantiate_screen_recorder(self, dir, fname):
        '''
        Method for instantiating the screen recorder.
        '''
        self.screen_recorder = self._record_screen(dir,fname)

    def instantiate_camera(self, dir, fname):
        '''
        Method for instantiating the camera.
        '''
        self.screen_recorder = self._take_snapshot(dir,fname)

    def _record_screen(self,dir,fname):
        '''
        Private method for recording frames from a Graphic's screen.
        '''
        img_num = 0
        while True:
            img_num += 1
            str_num = "00"+str(img_num)
            file_name = dir+fname+str_num[-3:]+".jpg"
            self.framework.image.save(self.screen,file_name)
            yield
    
    def _take_snapshot(self,dir,fname,collision):
        file_name = dir+fname+"_"+collision+".jpg"
        self.framework.image.save(self.screen,file_name)
        print("g")

    def draw_x_ball(self,objects,color=pygame.Color("Black")):
        for o in objects:
            if o.name == "Ball":
                posx,posy = o.body.position
                r = o.components[1].radius
                pygame.draw.line(self.screen, color, (posx-r,posy-r),(posx+r,posy+r),4)
                pygame.draw.line(self.screen, color, (posx+r,posy-r),(posx-r,posy+r),4)

    def draw_bb(self, shape):
            pos = shape.bb.left, shape.bb.bottom
            w = shape.bb.right - shape.bb.left
            h = shape.bb.top - shape.bb.bottom
            p = to_pygame(pos, self.screen)
            pygame.draw.rect(self.screen, pygame.Color("Blue"), (*p, w, h), 1)

    def draw_circle_at_point(self,pos):
        color = pygame.Color("Black")
        pygame.draw.circle(self.screen, color, pos, 20)

    def update_display(self):
        # Update display
        pygame.display.update()
        # If recording screen, record screen
        if self.screen_recorder:
            next(self.screen_recorder)

    def draw(self,objects,tick=None):
        # Fill screen with background, and refresh each frame
        self.screen.fill(pygame.Color("gray"))
        # Iterate and draw objects
        for o in objects:
            # Drawing the ball
            if o.name == "Ball":
                if self.draw_params['ball_alpha']:
                    # Get color object of Ball
                    color = self.draw_params['Ball']
                    # Set alpha value of color object according to curent tick
                    color.a = int(255-tick*4) if int(255-tick*4) > 0 else 0
                    # Draw circle
                    draw_circle_alpha(self.screen, color, o.body.position, 20)
                    # Once shape disappears, end simulation
                    if color.a == 0:
                        self.running = False
                else:
                    color = self.draw_params['Ball']
                    pygame.draw.circle(self.screen, color, to_pygame(o.body.position,self.screen), 20)
                    for line in o.components[2:]:
                        body = o.components[0]
                        offset = body.position
                        pygame.draw.line(self.screen, color, line.a+offset, line.b+offset,5)
            # Drawing the goal
            elif o.name == "Goal":
                color = self.draw_params['Goal']
                r = pygame.Rect(0,0,o.l+1,o.w+1)
                r.center = o.body.position
                pygame.draw.rect(self.screen, color, r)
            # Drawing border and containers
            elif o.name == "Container" or o.name == "Line":
                color = self.draw_params['Container']
                # We skip the first element in the components because that's the body
                for line in o.components[1:]:
                    body = o.components[0]
                    offset = body.position
                    a = self.rotate(body, line.a)
                    b = self.rotate(body, line.b)
                    pygame.draw.line(self.screen, color, a+offset, b+offset,5)
            # Drawing border and containers
            elif "Border" in o.name:# == "Container":
                color = self.draw_params['Border']
                # We skip the first element in the components because that's the body
                for line in o.components[1:]:
                    body = o.components[0]
                    offset = body.position
                    a = self.rotate(body, line.a)
                    b = self.rotate(body, line.b)
                    pygame.draw.line(self.screen, color, a+offset, b+offset,5)
            elif o.name == "Sensor":
                color = self.draw_params['Ball']
                points = o.components[1].get_vertices()
                pygame.draw.polygon(self.screen,color,points)
    
    def debug_draw(self,space):
        self.screen.fill((0,0,0))
        space.debug_draw(self.debug_options)

    def rotate(self,body,point):
        rotatedx = point[0] * cos(body.angle) - point[1] * sin(body.angle)
        rotatedy = point[0] * sin(body.angle) + point[1] * cos(body.angle)
        return (rotatedx, rotatedy)
    
    def initialize_graphics(self):
        self.initialized = True
        self.debug_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.screen = self.framework.display.set_mode(self.size)
        self.clock = self.framework.time.Clock()
        self.framework.init()

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
        self.handlers["ball_goal"].post_solve = is_colliding

        # Ball and floor
        self.handlers["ball_floor"] = self.space.add_collision_handler(0,2)
        self.handlers["ball_floor"].data['colliding'] = False
        self.handlers["ball_floor"].post_solve = is_colliding

        # Ball and containers
        self.handlers["ball_container"] = self.space.add_collision_handler(0,3)
        self.handlers["ball_container"].data['colliding'] = False
        self.handlers["ball_container"].post_solve = is_colliding

        # Sensor and goal
        self.handlers["sensor_goal"] = self.space.add_collision_handler(9,1)
        self.handlers["sensor_goal"].data['colliding'] = False
        self.handlers['sensor_goal'].separate = not_colliding
        self.handlers["sensor_goal"].post_solve = is_colliding

        # Sensor and floor
        self.handlers["sensor_floor"] = self.space.add_collision_handler(9,2)
        self.handlers["sensor_floor"].data['colliding'] = False
        self.handlers['sensor_floor'].separate = not_colliding
        self.handlers["sensor_floor"].post_solve = is_colliding

        # Sensor and containers
        self.handlers["sensor_container"] = self.space.add_collision_handler(9,3)
        self.handlers["sensor_container"].data['colliding'] = False
        self.handlers['sensor_container'].separate = not_colliding
        self.handlers["sensor_container"].post_solve = is_colliding

    def collision(self):
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

class Scene:
    '''
    A Scene is a tuple of PObjects, Physics, and Graphics
    '''
    def __init__(self, physics, objects, graphics):
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
            ball_pos_pp, valid_pp = path_projection(self.objects,self.physics,D)
            # Step simulator forward N times
            for _ in range(int(N)):
                # Physics
                self.physics.forward()
                self.running *= not self.listener.listen()
                self.running *= not self.physics.collision()
                self.running *= self.graphics.running
                if view:
                    self.graphics.draw(self.objects)
                    self.graphics.draw_circle_at_point(ball_pos_pp)
                    self.graphics.clock.tick(self.graphics.fps)
                    self.graphics.update_display()
            if self.physics.tick > 5000:
                self.running = False
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

    def run(self,view=True,subroutine=None,name=None):
        '''
        Forward method for the scene. Evolves PObjects over time according
        to a Physics and renders the simulation to the screen with a Graphics
        '''
        straight_path = False
        if view and not self.graphics.initialized:
            self.graphics.initialize_graphics()
        while self.running:
            # Physics
            if not self.pause:
                self.physics.forward()
                self.running *= not self.listener.listen()
                self.running *= not self.physics.collision()
                self.running *= self.graphics.running
                if subroutine:
                    straight_path, collision = subroutine(self.objects,self.graphics,self.physics)
            if self.physics.tick > 1000:
                self.running = False
            # Graphics
            if view:
                self.graphics.draw(self.objects,self.physics.tick)
                if subroutine:
                    straight_path, collision = subroutine(self.objects,self.graphics,self.physics)
                self.graphics.clock.tick(self.graphics.fps)
                self.graphics.update_display()
                # User Events
                self.event()
            if straight_path:
                self.running = False

    def instantiate_scene(self):
        for obj in self.objects:
            self.physics.space.add(*obj.components)
            if obj.name == "Ball":
                self.listener = Listener(obj.body)

class SceneBuilder(Scene):
    '''
    Convenience class for using the mouse to build Scenes
    '''

    def __init__(self, physics, objects, graphics, pallete):
        super().__init__(physics,objects,graphics)
        self.pos1 = None
        self.pos2 = None
        self.brush = None
        self.pallete = pallete
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
                obj = self.pallete['c'](self.pos1,self.pos2)
                self.objects.append(obj)
                self.object_record = (self.pallete['c'])
                self.object_arg_record['line_args'].append([self.pos1,self.pos2])
                self.physics.space.add(*obj.components)
                self.pos1, self.pos2 = None, None
        elif self.brush == 'b':
            if self.object_arg_record['ball_args'] == None:
                obj = self.pallete['b'](pos)
                self.objects.append(obj)
                self.object_record = (self.pallete['b'])
                self.object_arg_record['ball_args']= [pos]
                self.physics.space.add(*obj.components)
            else:
                for obj in self.objects:
                    if obj.name == "Ball":
                        obj.body.position = pos
                        self.object_arg_record['ball_args'] = [pos]
        elif self.brush == 'g':
            if self.object_arg_record['goal_args'] == None:
                obj = self.pallete['g']((pos[0],1000))
                self.objects.append(obj)
                self.object_record = (self.pallete['g'])
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
            ball_pos_pp, valid_pp = path_projection(self.objects,self.physics, D)
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
                if self.physics.collision():
                    print(f'tick: {self.physics.tick}')
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
