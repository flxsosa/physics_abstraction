from math import pi, radians
import numpy as np
import pymunk
import pygame
from pymunk.pygame_util import *
from helper import rotate

# Straight Path

def update_angle(object):
    '''
    Updates the angle of the body of a PObject to point
    in the direction of its velocity.

    :param object: A PObject or Pymunk.Shape
    '''
    # Get the body
    body = object.body
    # Get the velocity angle
    x,y = body.velocity.normalized()
    angle = np.arctan2(y,x)
    angle = radians(180*angle/pi - 90)
    # Set the body angle to the velocity angle
    body.angle = angle

def get_shape(object):
    '''
    Creates a sensorshape centered on a given PObject.

    :param object: Object to which the sensorshape is attached.
    '''
    # Parameter for sensor
    length = 400

    # Body to which sensorshape is attached
    body = object.body
    r = object.components[1].radius-0.5*object.components[1].radius

    # Sensorshape
    sensorshape = pymunk.Poly(body, [(-r,r+length), (r,r+length), (r,-r), (-r,-r)])
    sensorshape.color = pygame.Color("purple")
    sensorshape.collision_type = 9
    sensorshape.sensor = True
    return sensorshape

def check_collision_all(sensorshape,objects,verbose=False):
    '''
    Checks for overlap between sensor and all objects in a Scene.
    To be used with the path projection subroutine

    :param sensorshape: Sensor, expected to be a Pymunk.Shape.
    :param objects: List of PObjects in Scene.
    :param verbose: Flag for printing value of collision flags.
    '''
    # Set all collision flags to false
    coll_containers = False
    coll_goal = False
    coll_border = False
    points = None

    # Iterate through objects in scene, and check for overlap with sensor
    for o in objects:  
        # Containers and Lines
        if o.name == "Container" or o.name == "Line":
            # We skip the first element in the components because that's the body
            for line in o.components[1:]:
                coll_containers = bool(sensorshape.shapes_collide(line).points) or coll_containers
                points = [(p.point_a, p.point_b) for p in sensorshape.shapes_collide(line).points]
        # Floor of game
        elif "Border" in o.name:
            # We skip the first element in the components because that's the body
            for line in o.components[1:]:
                coll_border = bool(sensorshape.shapes_collide(line).points) or coll_border
        # Goal
        elif o.name == "Goal":
            goalshape = o.components[1]
            coll_goal = bool(sensorshape.shapes_collide(goalshape).points)
    
    # Print value of collision flags if requested
    if verbose:
        print(f"We {'are' if coll_containers else 'are not'} colliding w/ containers.")
        print(f"We {'are' if coll_goal else 'are not'} colliding w/ goal.")
        print(f"We {'are' if coll_border else 'are not'} colliding w/ floor.")

    # Return collision flags
    return (coll_goal, coll_containers, coll_border), points

# Path Projection

def path_projection(objects, physics, D):
    '''
    Could check out position_func in pymunk

    :param objects: Set of objects in the scene
    :param physics: Physics backend for scene
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
    if velocity_vector[1] < 0:
        return curr_pos, False
    else:
        new_pos = curr_pos+(velocity_vector)*D

    # Check whether path collides with any other objects
    pp_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    pp_shape = pymunk.Segment(pp_body,(new_pos),(curr_pos),1)
    pp_shape.collision_type = 9 
    physics.space.add(pp_body,pp_shape)
    pp_overlaps, pp_points = check_collision_all(pp_shape,objects)
    physics.space.remove(pp_body,pp_shape)
    # Whether projected path is valid
    valid_pp = not any(pp_overlaps)

    return new_pos, valid_pp
