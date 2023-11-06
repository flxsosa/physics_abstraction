import json_utilities
import math
import numpy as np
import pygame
import pymunk
import pymunk.pygame_util
import shapely.geometry

from typing import Any, Union
from pygame.locals import *
from pygame.color import *

WIDTH, HEIGHT = 800,1000
OBJECT_ELASTICITY = 1
BALL_ELASTICITY = 1


def get_border_bb(border:str) -> list[int]:
    """Get a border object's bounding box."""
    if border == "bottom":
        x1, x2 = 10, 790
        y1, y2 = 1000,1010
    elif border == "right":
        x1, x2 = 790, 800
        y1, y2 = 210, 1000
    elif border == "left":
        x1, x2 = 10, 0
        y1, y2 = 210, 1000
    # Points
    p1 = x1, y1
    p2 = x2, y1
    p3 = x2, y2
    p4 = x1, y2
    points = [p1,p2,p3,p4]
    return points


def rotate(
        origin:list[Union[int, float]],
        point:list[Union[int, float]],
        angle:Union[int, float]) -> list[Union[int, float]]:
    """Rotate a point some angle about an origin."""
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return [qx, qy]


def get_area_from_bb(bb:list[Union[int, float]]) -> shapely.geometry.Polygon:
    """Get area of object from its bounding box."""
    return shapely.geometry.Polygon(bb)


def get_container_bb(
        x1:Union[int, float],
        x2:Union[int, float],
        y:Union[int, float],
        d:Union[int, float],
        angle:Union[int, float],
        offset:Union[int, float]) -> list[Union[int, float]]:
    """Create a bounding box from Container arguments.

    Args:
        d: Thickness of the Container
        angle: Angle of the Container in degrees

    Outputs:
        points: A list of vertices.
    """
    # Convert radians to degrees
    theta = math.radians(angle)
    x_offset, y_offset = offset
    d+=2
    # Points
    p1 = x1, y+d
    p2 = x2, y+d
    p3 = x2, y-d
    p4 = x1, y-d
    points = [p1,p2,p3,p4]
    for i, point in enumerate(points):
        p = rotate((0,0), point, theta)
        points[i] = round(p[0]+x_offset, 2), round(p[1]+y_offset,2)
    return points


class PObject :
    """A simulated physical object."""
    def __init__(
            self,
            name:str,
            body:pymunk.Body,
            components:list[Any],
            id:int=99):
        # Name of the object
        self.name = name
        # Pymunk body of the object
        self.body = body
        # Body and shapes for object
        self.components = components
        self.id=id


class LeftBorder(PObject):
    """Left border object of a scene."""
    def __init__(self, l:int=1000, w:int=800, d:int=2):
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
    """Right border object of a scene."""
    def __init__(self, l:int=1000, w:int=800, d:int=2):
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
    """Bottom border object of a scene."""
    def __init__(
            self,
            pos1:list[Union[int, float]]=(10,990),
            pos2:list[Union[int, float]]=(790,990),
            d:int=2):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        segment = pymunk.Segment(body,pos1,pos2, d)
        segment.color = pygame.Color("white")
        segment.collision_type = 2
        segment.friction = 1
        segment.elasticity = OBJECT_ELASTICITY
        components = [body,segment]
        self.bounding_box = get_border_bb("bottom")
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("BottomBorder",body,components)


class Container(PObject):
    """Class for container object in a scene."""
    def __init__(self, config:json_utilities.ContainerConfig):
        config = config.model_dump()
        id = config['id']
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = config['position']
        body.angle = math.radians(config['angle'])
        # Bottom segment
        y_point = 0
        x_point_1 = config['width']
        x_point_2 = -1*config['width']
        segment = pymunk.Segment(
            body,
            (x_point_1,y_point),
            (x_point_2,y_point),
            2)
        segment.color = pygame.Color('white')
        segment.collision_type = 3
        segment.friction = 1
        segment.elasticity = OBJECT_ELASTICITY
        components = [body,segment]
        self.bounding_box = get_container_bb(
            x_point_1,
            x_point_2,
            y_point,
            2,
            config['angle'],
            config['position'])
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("Container", body, components, id)


class Line(PObject):
    """Class for line object in scene."""
    def __init__(self,
                 config:json_utilities.LineConfig,
                 angle:Union[int, float]=0):
        config = config.model_dump()
        height = 2
        x_point_1 = config['point_a'][0]
        x_point_2 = config['point_b'][0]
        y_point_1 = config['point_a'][1]
        y_point_2 = config['point_b'][1]
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        position = (x_point_1 + x_point_2) / 2, (y_point_1 + y_point_2) / 2
        body.position = position
        body.angle =  math.radians(angle)
        line_point_a = (
            x_point_1 - body.position[0],
            y_point_1 - body.position[1])
        line_point_b = (
            x_point_2 - body.position[0],
            y_point_2 - body.position[1])
        segment = pymunk.Segment(body, (line_point_a), (line_point_b), height)
        segment.color = pygame.Color("white")
        segment.collision_type = 3
        segment.friction = 1
        segment.elasticity = OBJECT_ELASTICITY
        components = [body,segment]
        self.bounding_box = [
            (x_point_1, y_point_1 + height),
            (x_point_1, y_point_1 - height),
            (x_point_2, y_point_2 - height),
            (x_point_2, y_point_2 + height)
        ]
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("Line",body,components)


class Goal(PObject):
    """Class for goal object in scene."""
    def __init__(self, config:json_utilities.GoalConfig):
        config = config.model_dump()
        length = 80
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = config['position']
        shape = pymunk.Poly.create_box(body, (length, length/2))
        shape.color = pygame.Color('green')
        shape.collision_type = 1
        components = [body,shape]
        # Convenience properties for accessing length and width
        self.length = length
        self.width = length/2
        x_point_1 = -length/2
        x_point_2 = length/2
        y_point = 0
        height = 20
        angle = 0
        self.bounding_box = get_container_bb(
            x_point_1,
            x_point_2,
            y_point,
            height,
            angle,
            config['position'])
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("Goal", body, components, 100)


class Ball(PObject):
    """Class for ball object in scene."""
    def __init__(self, config: json_utilities.BallConfig):
        config = config.model_dump()
        self.radius = 20
        body = pymunk.Body(10.0, 10)
        body.position = config['position']
        pos_x, pos_y = config['position']
        shape = pymunk.Circle(body, self.radius)
        shape.elasticity = 0.8
        shape.friction = 1
        shape.color = pygame.Color("red")
        shape.collision_type = 0
        components = [body,shape]
        self.bounding_box = [
            (-self.radius + pos_x, self.radius + pos_y),
            (self.radius + pos_x, self.radius + pos_y),
            (self.radius + pos_x, -self.radius + pos_y),
            (-self.radius + pos_x, -self.radius + pos_y)
            ]
        self.area = get_area_from_bb(self.bounding_box)
        super().__init__("Ball", body, components, 0)
