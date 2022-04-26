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
    def __init__(self,name,body,components):
        self.name = name # Name of the object
        self.body = body # Pymunk body of the object
        self.components = components # Body and shapes for object

class PlinkoBorder(PObject):
    def __init__(self, span=(800,1000), d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        components = [body]
        x0, y0 = 10, span[1]*0.2+10
        x1, y1 = span[0]-10,span[1]-10
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

class BottomBorder(PObject):
    def __init__(self, span=(800,1000), d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        segment = pymunk.Segment(body,(10,990),(790,990), d)
        segment.color = pygame.Color("white")
        segment.collision_type = 2
        segment.friction = 1
        segment.elasticity = obj_elasticity
        components = [body,segment]
        super().__init__("BottomBorder",body,components)

class Container(PObject):
    def __init__(self, pos=(width/2,height/2), w=40, l=80, angle=0,d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        body.angle = math.radians(angle)
        # Bottom segment
        b_y = l
        b_x1 = w + d + 1
        b_x2 = -w - d - 1
        b_segment = pymunk.Segment(body,(b_x1,b_y),(b_x2,b_y),d)
        b_segment.color = pygame.Color("white")
        b_segment.collision_type = 3
        b_segment.friction = 1
        b_segment.elasticity = obj_elasticity
        # Left segment
        l_y1 = l
        l_y2 = 0
        l_x1 = -w - d - 1
        l_x2 = -w - d - 1
        l_segment = pymunk.Segment(body,(l_x1,l_y1),(l_x2,l_y2),d)
        l_segment.color = pygame.Color("white")
        l_segment.collision_type = 3
        l_segment.friction = 1
        l_segment.elasticity = obj_elasticity
        # Right segment
        r_y1 = l
        r_y2 = 0
        r_x1 = w + d + 1
        r_x2 = w + d + 1
        r_segment = pymunk.Segment(body,(r_x1, r_y1),(r_x2, r_y2),d)
        r_segment.color = pygame.Color("white")
        r_segment.collision_type = 3
        r_segment.friction = 1
        r_segment.elasticity = obj_elasticity
        components = [body,b_segment,l_segment,r_segment]
        super().__init__("Container",body,components)

class Line(PObject):
    def __init__(self, pos1,pos2,d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        segment = pymunk.Segment(body,(pos1),(pos2),d)
        segment.color = pygame.Color("white")
        segment.collision_type = 3
        segment.friction = 1
        segment.elasticity = obj_elasticity
        components = [body,segment]
        super().__init__("Line",body,components)

class Goal(PObject):
    def __init__(self, pos=(200,200), l=80):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos[0], pos[1]
        shape = pymunk.Poly.create_box(body, (l/2, l))
        shape.color = pygame.Color("green")
        shape.collision_type = 1
        components = [body,shape]
        # Convenience properties for accessing length and width
        self.l = l
        self.w = l/2
        super().__init__("Goal",body,components)

class Ball(PObject):
    def __init__(self, pos=(100,100), r=20):
        self.radius = r
        body = pymunk.Body(10.0, 10)
        body.position = pos
        shape = pymunk.Circle(body, r)   
        shape.elasticity = 0.8
        shape.friction = 1
        shape.color = pygame.Color("red")
        shape.collision_type = 0
        components = [body,shape]
        super().__init__("Ball",body,components)
