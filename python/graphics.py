import pymunk
import pygame
from pygame.locals import *
from pygame.color import *
from pymunk.pygame_util import to_pygame
from math import cos,sin
from random import randrange
from math import cos, sin
from helper import draw_circle_alpha
from pymunk.vec2d import Vec2d

class Graphics:
    '''
    A Graphics renders PObjects onto a screen.
    '''
    def __init__(self,width=800,height=1500,fps=60):
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
            'ball_alpha':False
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
    
    def _take_snapshot(self,dir,fname):
        file_name = dir+fname+".jpg"
        self.framework.image.save(self.screen,file_name)

    def draw_x_ball(self,objects,color=pygame.Color("Black")):
        for o in objects:
            if o.name == "Ball":
                posx,posy = o.body.position
                r = o.components[1].radius
                pygame.draw.line(self.screen, color, (posx-r,posy-r),(posx+r,posy+r),4)
                pygame.draw.line(self.screen, color, (posx+r,posy-r),(posx-r,posy+r),4)

    def draw_bb(self, bb):
            pos = bb.left, bb.bottom
            w = bb.right - bb.left
            h = bb.top - bb.bottom
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
                
                if self.draw_params.get('ball_alpha'):
                    # Get color object of Ball
                    color = self.draw_params['Ball']
                    # Set alpha value of color object according to curent tick
                    color.a = int(255-tick*4) if int(255-tick*4) > 0 else 0
                    # Draw circle
                    draw_circle_alpha(self.screen, color, o.body.position, 20)
                    # Once shape disappears, end simulation
                    if color.a == 0:
                        self.running = False
                elif type(self.draw_params.get('trace')) == list:
                    color = pygame.Color("Black")
                    self.draw_params['trace'].append(o.body.position)
                    for point in self.draw_params['trace']:
                        pygame.draw.circle(self.screen, color, to_pygame(point,self.screen), 20)
                    color = self.draw_params['Ball']
                    pygame.draw.circle(self.screen, color, to_pygame(o.body.position,self.screen), 20)
                    for line in o.components[2:]:
                        body = o.components[0]
                        offset = body.position
                        pygame.draw.line(self.screen, color, line.a+offset, line.b+offset,5)
                elif self.draw_params.get('bounding_boxes'):
                    self.draw_bb(o.components[1].bb)
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
                if self.draw_params.get('bounding_boxes'):
                    self.draw_bb(o.components[1].bb)
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
                    if self.draw_params.get('bounding_boxes'):
                        self.draw_bb(line.bb)
            # Drawing border and containers
            elif "Border" in o.name:
                color = self.draw_params['Border']
                # We skip the first element in the components because that's the body
                for line in o.components[1:]:
                    body = o.components[0]
                    offset = body.position
                    a = self.rotate(body, line.a)
                    b = self.rotate(body, line.b)
                    pygame.draw.line(self.screen, color, a+offset, b+offset,5)
            # Drawing body sensors
            elif o.name == "Region":
                color = pygame.Color("Red")
                color.a = 80
                draw_circle_alpha(self.screen, color, o.body.position, 60)
                # pygame.draw.circle(self.screen, color, to_pygame(o.body.position,self.screen), 60)
                color = pygame.Color("Black")
                pygame.draw.circle(self.screen, color, to_pygame(o.body.position,self.screen), 60, 2)
        
        for o in objects:
            if o.name == "BottomBorder":
                line = o.components[1]
                y = line.a[1]+3
                color = pygame.Color("gray")
                r = pygame.Rect(0,y,800,1000-y)
                pygame.draw.rect(self.screen, color, r)
   
    def debug_draw(self,space):
        self.screen.fill((0,0,0))
        space.debug_draw(self.debug_options)

    def draw_collision_normals(self,collision_normals):
        if collision_normals['colliding']:
            normal = collision_normals['normal'] * -1
            collision_point_set = collision_normals['cps']
            collision_point = collision_point_set.points
            pos1 = collision_point[0].point_a
            pos2 = pos1+100*normal
            pygame.draw.line(self.screen, pygame.Color('black'), pos1, pos2,5)

    def rotate(self,body,point):
        rotatedx = point[0] * cos(body.angle) - point[1] * sin(body.angle)
        rotatedy = point[0] * sin(body.angle) + point[1] * cos(body.angle)
        return (rotatedx, rotatedy)
    
    def initialize_graphics(self):
        self.initialized = True
        self.debug_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.screen = self.framework.display.set_mode(self.size, pygame.RESIZABLE)
        self.clock = self.framework.time.Clock()
        self.framework.init()
