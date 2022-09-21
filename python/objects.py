import pygame
import pymunk
import pymunk.pygame_util
from pygame.locals import *
from pygame.color import *
import math

width, height = 800,1000
obj_elasticity = 1
ball_elasticity = 1
'''
Collision types
bottom segment = 2
ball = 0
goal = 1
object = 3
sensor = 9
'''

class PObject:
    '''
    An PObject is a simulated physical object that evolves over time according
    to a Physics.
    '''
    def __init__(self,name,body,components,id=99):
        self.name = name # Name of the object
        self.body = body # Pymunk body of the object
        self.components = components # Body and shapes for object
        self.id=id

class PlinkoBorder(PObject):
    def __init__(self, l=1000, w=800, d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        components = [body]
        x0, y0 = 10, 210
        x1, y1 = w-10,l-10
        segments = [(x0,y0),(x0,y1),(x1,y1),(x1,y0)] # Right
        # Left and Right
        for i in range(3):
            if i == 1:
                continue
            segment = pymunk.Segment(body, segments[i], segments[(i+1)%4], d)
            segment.elasticity = 1
            segment.friction = 1
            segment.color = pygame.Color("white")
            components.append(segment)
        super().__init__("PlinkoBorder",body,components)

class LeftBorder(PObject):
    def __init__(self, l=1000, w=800, d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        components = [body]
        x0, y0 = 10, 210
        segment = pymunk.Segment(body, (x0,y0),(x0,l-10), d)
        segment.friction = 1
        segment.elasticity = 1
        components.append(segment)
        super().__init__("PlinkoBorder",body,components)

class RightBorder(PObject):
    def __init__(self, l=1000, w=800, d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        components = [body]
        x0, y0 = w-10, 210
        segment = pymunk.Segment(body, (x0,y0),(x0,l-10), d)
        segment.friction = 1
        segment.elasticity = 1
        components.append(segment)
        super().__init__("PlinkoBorder",body,components)

class BottomBorder(PObject):
    def __init__(self, pos1=(10,990),pos2=(790,990), d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        segment = pymunk.Segment(body,pos1,pos2, d)
        segment.color = pygame.Color("white")
        segment.collision_type = 2
        segment.friction = 1
        segment.elasticity = obj_elasticity
        components = [body,segment]
        super().__init__("BottomBorder",body,components)

class Container(PObject):
    def __init__(self, pos=(width/2,height/2), w=40, l=80, angle=0,id=99,d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        body.angle = math.radians(angle)
        # Bottom segment
        y = l
        x1 = w + d + 1 
        x2 = -w - d - 1 
        segment = pymunk.Segment(body,(x1,y),(x2,y),d)
        segment.color = pygame.Color("white")
        segment.collision_type = 3
        segment.friction = 1
        segment.elasticity = obj_elasticity
        components = [body,segment]
        super().__init__("Container",body,components,id)

class Line(PObject):
    def __init__(self, pos1,pos2,angle=0,d=2,collision_type=3):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (pos1[0]+pos2[0]) / 2, (pos1[1] + pos2[1]) / 2
        body.angle =  math.radians(angle)
        pos1 = pos1[0] - body.position[0], pos1[1] - body.position[1]
        pos2 = pos2[0] - body.position[0], pos2[1] - body.position[1]
        segment = pymunk.Segment(body,(pos1),(pos2),d)
        segment.color = pygame.Color("white")
        segment.collision_type = collision_type
        segment.friction = 1
        segment.elasticity = obj_elasticity
        components = [body,segment]
        super().__init__("Line",body,components)

class Goal(PObject):
    def __init__(self, pos=(200,200), l=80):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos[0], pos[1]
        shape = pymunk.Poly.create_box(body, (l, l/2))
        shape.color = pygame.Color("green")
        shape.collision_type = 1
        components = [body,shape]
        # Convenience properties for accessing length and width
        self.l = l
        self.w = l/2
        super().__init__("Goal",body,components,100)

class Ball(PObject):
    def __init__(self, pos=(100,100), r=20, id=0):
        self.radius = r
        body = pymunk.Body(10.0, 10)
        body.position = pos
        shape = pymunk.Circle(body, r)   
        shape.elasticity = 0.8
        shape.friction = 1
        shape.color = pygame.Color("red")
        shape.collision_type = 0
        components = [body,shape]
        super().__init__("Ball",body,components,id)

class Region(PObject):
    def __init__(self, pos=(100,100), r=60):
        self.radius = r
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Circle(body, r)   
        shape.color = pygame.Color("red")
        shape.collision_type = 1
        components = [body,shape]
        super().__init__("Region",body,components)