import pygame
import pymunk
import pymunk.pygame_util
from pygame.locals import *
from pygame.color import *
import math

# Global settings
fps = 60
width, height = 800,800
space = pymunk.Space()
space.gravity = 0,150
# pygame.init()
# screen = pygame.display.set_mode((width,height))
# clock = pygame.time.Clock()
running = True
step = False
# draw_options = pymunk.pygame_util.DrawOptions(screen)

class GameBorder:
    def __init__(self, space, p0=(10, 10), p1=(width-10, height-10), d=2):
        x0, y0 = p0
        x1, y1 = p1
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for i in range(4):
            segment = pymunk.Segment(space.static_body, pts[i], pts[(i+1)%4], d)
            segment.elasticity = 1
            segment.friction = 1
            space.add(segment)

class Container:
    def __init__(self, pos=(width/2,height/2), l=80,d=2):
        self.init_position = pos
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        x,y = pos
        b_y = y+l
        b_x1 = x+l/2
        b_x2 = x-l/2
        b_segment = pymunk.Segment(self.body,(b_x1,b_y),(b_x2,b_y),d)
        l_y1 = y+l
        l_y2 = y
        l_x1 = x - l/2
        l_x2 = x - l/2
        l_segment = pymunk.Segment(self.body,(l_x1,l_y1),(l_x2,l_y2),d)
        r_y1 = y+l
        r_y2 = y
        r_x1 = x + l/2
        r_x2 = x + l/2
        r_segment = pymunk.Segment(self.body,(r_x1, r_y1),(r_x2, r_y2),d)
        self.components = self.body,b_segment,l_segment,r_segment

class Platform:
    def __init__(self, space, pos=(width/2,height/2), l=80,d=2):
        self.pos = pos
        x,y=pos
        segment = pymunk.Segment(space.static_body, (x-l/2,y),(x+l/2,y),d)
        space.add(segment)

class Platform:
    def __init__(self, space, pos=(width/2,height/2), l=80,d=2):
        self.pos = pos
        x,y=pos
        segment = pymunk.Segment(space.static_body, (x-l/2,y),(x+l/2,y),d)
        space.add(segment)

class Slide:
    def __init__(self, space, pos=(width/2, height/2), degree=45, l=80, d=2):
        self.pos = pos
        x,y=pos
        rads = math.radians(degree)
        a_x = x + l/2*math.cos(rads)
        a_y = y + l/2*math.sin(rads)
        rads = math.radians(degree+180)
        b_x = x + l/2*math.cos(rads)
        b_y = y + l/2*math.sin(rads)
        segment = pymunk.Segment(space.static_body, (a_x,a_y), (b_x,b_y), d)
        space.add(segment)

class Goal:
    def __init__(self, pos=(width,height), l=80,):
        self.init_position = pos
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pos[0], pos[1]-34
        self.shape = pymunk.Poly.create_box(self.body, (l, l/2))
        self.shape.color = pygame.Color("green")
        self.shape.collision_type = 1
        self.components = [self.body,self.shape]

class Ball:
    def __init__(self, pos=(width/2,height/2), r=20):
        self.init_position = pos
        self.init_radius = r
        self.body = pymunk.Body(10.0, 1)
        self.body.position = pos
        self.body.elasticity = 1
        self.shape = pymunk.Circle(self.body, r)   
        self.shape.color = pygame.Color("red")
        self.shape.collision_type = 0
        self.components = self.body,self.shape

class Teleporter:
    def __init__(self, space, pos=(width/2,height/2), mask=2, l=80):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pos
        self.shape = pymunk.Poly.create_box(self.body, (l, l/2))
        self.shape.color = pygame.Color("yellow")
        self.shape.collision_type = mask
        space.add(self.body, self.shape)

class Pendulum:
    def __init__(self):
        # rotation_center_body = pymunk.Body(body_type=pymunk.Body.STATIC)  # 1
        # rotation_center_body.position = (400, 10)
        body = pymunk.Body(1,1)
        body.position = (300, 300)
        l1 = pymunk.Segment(body, (400, 10), (200, 30), 2)
        rotation_center_joint = pymunk.PinJoint(
            body, rotation_center_body, (0, 0), (0, 0)
            )
        space.add(l1, body, rotation_center_joint)