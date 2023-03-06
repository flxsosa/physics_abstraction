import pygame
import pymunk
import pymunk.pygame_util
from pygame.locals import *
from pygame.color import *
import math
from scipy.ndimage.interpolation import rotate
import numpy as np
from shapely.geometry import Polygon

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

def get_border_bb(border):
    if border == "bottom":
        y1, y2 = 1492, 1700
        x1, x2 = 10, 790

    elif border == "right":
        y1, y2 = 210, 1492
        x1, x2 = 790, 1000
    
    elif border == "left":
        y1, y2 = 210, 1492
        x1, x2 = 10, -200

    # Points
    p1 = x1, y1
    p2 = x2, y1
    p3 = x2, y2
    p4 = x1, y2
    points = [p1,p2,p3,p4]
    return points

def get_area_from_bb(bb):
    return Polygon(bb)

def get_container_bb(x1,x2,y,d,angle, offset):
    '''
    Create a bounding box from Container arguments.
    Returns a list of vertices.

    :param d: Thickness of the Container
    :param angle: Angle of the Container in degrees
    '''
    def rotate(origin, point, angle):
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return [qx, qy]

    # Convert radians to degrees
    theta = math.radians(angle)
    x_offset, y_offset = offset

    # Points
    p1 = x1, y+d
    p2 = x2, y+d
    p3 = x2, y-d
    p4 = x1, y-d
    points = [p1,p2,p3,p4]

    for i in range(len(points)):
        p = rotate((0,0),points[i],theta)
        points[i] = p[0]+x_offset, p[1]+y_offset

    return points

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

class PlinkoBorder2(PObject):

    def __init__(self,left, l=1000,w=200,d=2):
        # Left rectangle
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        components = [body]
        x0, y0 = 10, 210 # Right side of left box
        if left:
            x1, y1 = 10-w, l # Left side of left box
            self.bounding_box = get_border_bb("left")
            self.area = get_area_from_bb(self.bounding_box)
        else:
            x1, y1 = 10+w, l
            self.bounding_box = get_border_bb("right")
            self.area = get_area_from_bb(self.bounding_box)

        # Make vertices list for shape
        vs = [(x0,y0),(x1,y0),(x0,y1),(x1,y1)]
        shape = pymunk.Poly(body, vs)
        shape.color = pygame.Color("white")
        shape.collision_type = 1
        components = [body,shape]
        super().__init__("PlinkoBorder",body,components)

class PlinkoBorder(PObject):
    def __init__(self, l=1000, w=800, d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        components = [body]
        x0, y0 = 10, 210
        x1, y1 = w-10,l-10
        segments = [(x0,y0),(x0,y1),(x1,y1),(x1,y0)] # Right
        self.bounding_box = get_border_bb("right")
        self.area = get_area_from_bb(self.bounding_box)
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
        self.bounding_box = get_border_bb("left")
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("PlinkoBorder",body,components)

class RightBorder(PObject):
    def __init__(self, l=1000, w=800, d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        components = [body]
        x0, y0 =  790, 210
        segment = pymunk.Segment(body, (x0,y0),(x0,l-10), d)
        segment.friction = 1
        segment.elasticity = 1
        components.append(segment)
        self.bounding_box = get_border_bb("right")
        self.area = get_area_from_bb(self.bounding_box)
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
        self.bounding_box = get_border_bb("bottom")
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("BottomBorder",body,components)

class Container(PObject):
    def __init__(self, pos=(width/2,height/2), w=40, l=80, angle=0,id=99,d=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        body.angle = math.radians(angle)
        # Bottom segment
        y = 0
        x1 = w
        x2 = -w 
        segment = pymunk.Segment(body,(x1,y),(x2,y),d)
        segment.color = pygame.Color("white")
        segment.collision_type = 3
        segment.friction = 1
        segment.elasticity = obj_elasticity
        components = [body,segment]
        self.bounding_box = get_container_bb(x1,x2,y,d,angle,pos)
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("Container",body,components,id)

class Line(PObject):
    def __init__(self, pos1,pos2,angle=0,d=2,collision_type=3):
        x1,x2 = pos1[0], pos2[0]
        y1,y2 = pos1[1], pos2[1]
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (x1+x2) / 2, (y1 + y2) / 2
        body.angle =  math.radians(angle)
        pos1 = x1 - body.position[0], y1 - body.position[1]
        pos2 = x2 - body.position[0], y2 - body.position[1]
        segment = pymunk.Segment(body,(pos1),(pos2),d)
        segment.color = pygame.Color("white")
        segment.collision_type = collision_type
        segment.friction = 1
        segment.elasticity = obj_elasticity
        components = [body,segment]
        self.bounding_box = [
            (x1,y1+d),
            (x1,y1-d),
            (x2,y2-d),
            (x2,y2+d)
        ]
        self.area = get_area_from_bb(self.bounding_box)
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
        x1 = -l/2
        x2 = l/2
        y = 0
        d = 20
        angle = 0
        self.bounding_box = get_container_bb(x1,x2,y,d,angle,pos)
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("Goal",body,components,100)

class Ball(PObject):
    def __init__(self, pos=(100,100), r=20, id=0):
        self.radius = r
        body = pymunk.Body(10.0, 10)
        body.position = pos
        x,y = pos
        shape = pymunk.Circle(body, r)   
        shape.elasticity = 0.8
        shape.friction = 1
        shape.color = pygame.Color("red")
        shape.collision_type = 0
        components = [body,shape]
        self.bounding_box = [(-r+x,r+y),(r+x,r+y),(r+x,-r+y),(-r+x,-r+y)]
        self.area = get_area_from_bb(self.bounding_box)
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