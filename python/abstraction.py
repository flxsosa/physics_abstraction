
from pymunk.pygame_util import *
from shapely.geometry import LineString
from pymunk.vec2d import  Vec2d

def check_collision(path_poly, objects):
    '''
    Check whether the path projeciton polygon intersects with
    other polygons in the scene

    :param path_poly: Path projection Polygon object
    :param objects: List of objects in Scene
    '''
    # Check if polygon collides with objects
    for obj in objects:
        if path_poly.intersects(obj.area) and obj.name != "Ball":
            line_of_intersection = path_poly.intersection(obj.area).coords
            highest_point = min(line_of_intersection, key=lambda x: x[1])
            return True, Vec2d(*highest_point)
    return False, Vec2d(1,1)

# Path Projection

def create_path_poly(pos1, pos2, r):
    return LineString([pos1,pos2])

def path_projection(objects, D):
    '''
    Path projection subroutine

    :param objects: Set of objects in the scene
    :param D: Length of path projection
    '''
    # Get the ball
    for obj in objects:
        if obj.name == "Ball":
            ball = obj
    # Detemine position
    curr_pos = ball.body.position
    # Get velocity vector
    velocity_vector = ball.body.velocity.normalized()
    if velocity_vector[1] < 0 or velocity_vector == Vec2d(0,0):
        return curr_pos
    else:
        new_pos = curr_pos+(velocity_vector)*D
    # Check whether path collides with any other objects
    pp_shape = create_path_poly(curr_pos,new_pos,20)
    pp_collision, pp_point_of_collision = check_collision(pp_shape,objects)
    # Whether projected path is valid
    if pp_collision:
        new_pos = pp_point_of_collision - velocity_vector*20
    return new_pos
