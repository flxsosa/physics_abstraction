import pygame
import pymunk
import pymunk.pygame_util
from pygame.locals import *
from pygame.color import *
import math

width, height = 800,1000
'''
Collision types
bottom segment = 2
ball = 0
goal = 1
'''

class SceneBorder:
    def __init__(self, span, d=2):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = 0,0
        self.components = [self.body]
        x0, y0 = (10, 10)
        x1, y1 = span[0]-10,span[1]-10
        pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for i in range(4):
            segment = pymunk.Segment(self.body, pts[i], pts[(i+1)%4], d)
            segment.elasticity = 1
            segment.friction = 1
            segment.color = pygame.Color("black")
            self.components.append(segment)

class PlinkoBorder:
    def __init__(self, span, d=2):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.components = [self.body]
        x0, y0 = 10, span[1]*0.2+10
        x1, y1 = span[0]-10,span[1]-10
        segments = [(x0,y0),(x0,y1),(x1,y1),(x1,y0)] # Right
        # Left and Rigth
        for i in range(3):
            segment = pymunk.Segment(self.body, segments[i], segments[(i+1)%4], d)
            segment.elasticity = 1
            segment.friction = 1
            segment.color = pygame.Color("black")
            self.components.append(segment)

class Container:
    def __init__(self, pos=(width/2,height/2), w=40, l=80, angle=0,d=2):
        self.init_position = pos
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pos
        self.body.angle = math.radians(angle)
        self.area = []
        b_y = l
        b_x1 = w + d + 1
        b_x2 = -w -d -1
        b_segment = pymunk.Segment(self.body,(b_x1,b_y),(b_x2,b_y),d)
        b_segment.color = pygame.Color("black")
        l_y1 = l
        l_y2 = 0
        l_x1 = -w - d - 1
        l_x2 = -w - d - 1
        l_segment = pymunk.Segment(self.body,(l_x1,l_y1),(l_x2,l_y2),d)
        l_segment.color = pygame.Color("black")
        r_y1 = l
        r_y2 = 0
        r_x1 = w + d + 1
        r_x2 = w + d + 1
        r_segment = pymunk.Segment(self.body,(r_x1, r_y1),(r_x2, r_y2),d)
        r_segment.color = pygame.Color("black")
        self.components = self.body,b_segment,l_segment,r_segment

class Platform:
    def __init__(self, pos=(10,10), l=80, rot=0,d=2):
        pos = pos[0]/4, pos[1]/2
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.angle = rot
        self.pos = pos
        x,y=pos
        segment = pymunk.Segment(self.body, (150,10), (150,640), d)
        self.components = self.body, segment

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
        self.l = l
        self.w = l/2
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = pos[0], pos[1]-34
        self.shape = pymunk.Poly.create_box(self.body, (l, l/2))
        self.shape.color = pygame.Color("green")
        self.shape.collision_type = 1
        self.components = [self.body,self.shape]

class Ball:
    def __init__(self, pos=(width/2,height/2), r=20):
        self.init_position = pos
        self.radius = r
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

class Tube:
    def __init__(self, pos=(width/2,height/2), w=40, l=190,d=2):
        self.init_position = pos
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        x,y = pos
        l_y1 = y+l
        l_y2 = y
        l_x1 = x - w - d - 1
        l_x2 = x - w - d - 1
        l_segment = pymunk.Segment(self.body,(l_x1,l_y1),(l_x2,l_y2),d)
        l_segment.color = pygame.Color("black")
        r_y1 = y+l
        r_y2 = y
        r_x1 = x + w + d + 1
        r_x2 = x + w + d + 1
        r_segment = pymunk.Segment(self.body,(r_x1, r_y1),(r_x2, r_y2),d)
        r_segment.color = pygame.Color("black")
        self.components = self.body,l_segment,r_segment