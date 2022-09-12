from math import pi, radians
from turtle import Vec2D
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
    new_pos = None
    collision_points = []

    # Iterate through objects in scene, and check for overlap with sensor
    for o in objects:  
        collision = {
            "object_id":None,
            "distance":None,
            "normal":None,
            "new_pos":None
        }
        # Containers and Lines
        if o.name == "Container" or o.name == "Line":
            # We skip the first element in the components because that's the body
            for line in o.components[1:]:
                print(f"Container body: {o.body.position} Line: {line.a,line.b}")
                # print(f"Normal: {line.normal}")
                if sensorshape.point_query(o.body.position).distance < 0:
                    print(f"Colliding with {o.id}: {sensorshape.point_query(o.body.position)}")
                    normal = sensorshape.shapes_collide(line).normal
                    collision['object_id'] = o.id
                    collision['distance'] = abs(sensorshape.b-o.body.position)
                    collision['normal'] = sensorshape.shapes_collide(line).normal
                    collision['new_pos'] = o.body.position+normal*40
                else:
                    continue
                
                collision_points.append(collision)
                coll_containers = bool(sensorshape.shapes_collide(line).points) or coll_containers
        # Floor of game
        elif "Border" in o.name:
            # We skip the first element in the components because that's the body
            for line in o.components[1:]:
                for line in o.components[1:]:
                    # print(f"Angle: {o.body.angle}")
                    # print(f"Colliding with {o.id}: {sensorshape.point_query(o.body.position)}")
                    # print(f"Ball at {sensorshape.b} with distance {abs(sensorshape.b-o.body.position)}")
                    # print(f"Normal is {sensorshape.shapes_collide(line).normal}")
                    # print(f"New position would be {o.body.position+Vec2D(0,-40)}")
                    # print(f"Normal: {line.normal}")
                    if sensorshape.point_query(o.body.position).distance < 0:
                        collision['object_id'] = o.id
                        collision['distance'] = abs(sensorshape.b-o.body.position)
                        collision['normal'] = sensorshape.shapes_collide(line).normal
                        collision['new_pos'] = o.body.position+Vec2D(0,-40)
                    else:
                        continue
                    
                    collision_points.append(collision)
                coll_border = bool(sensorshape.shapes_collide(line).points) or coll_border
        # Goal
        elif o.name == "Goal":
            goalshape = o.components[1]
            # print(f"Normal: {goalshape.normal}")
            if sensorshape.point_query(o.body.position).distance < 0:
                # print(f"Colliding with {o.id}: {sensorshape.point_query(o.body.position)}")
                # print(f"Ball at {sensorshape.b} with distance {abs(sensorshape.b-o.body.position)}")
                # print(f"Normal is {sensorshape.shapes_collide(goalshape).normal}")
                # print(f"New position would be {o.body.position+Vec2D(0,40)}")
                collision['object_id'] = o.id
                collision['distance'] = abs(sensorshape.b-o.body.position)
                collision['normal'] = sensorshape.shapes_collide(goalshape).normal
                collision['new_pos'] = o.body.position+Vec2D(0,-40)
            else:
                continue
            
            collision_points.append(collision)
            coll_goal = bool(sensorshape.shapes_collide(goalshape).points)

    if collision_points:
        # print(f"There are collision points")
        collision_points.sort(key=lambda x: x['distance'])
        new_pos = collision_points[0]['new_pos']
        # print(collision_points)
        # print(f"Closest shape: {collision_points[0]}")
        print(f"New position should be: {collision_points[0]['new_pos']}")
        # print(" ")
    # Print value of collision flags if requested
    if verbose:
        print(f"We {'are' if coll_containers else 'are not'} colliding w/ containers.")
        print(f"We {'are' if coll_goal else 'are not'} colliding w/ goal.")
        print(f"We {'are' if coll_border else 'are not'} colliding w/ floor.")

    # Return collision flags
    return (coll_goal, coll_containers, coll_border), new_pos

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
        # print(f"Current position: {curr_pos}")
        # print(f"Velocity vector: {velocity_vector}")
        # print(f"Default new position: {new_pos}")
    # Check whether path collides with any other objects
    # print("Creating body...")
    pp_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    # pp_body.position = (new_pos[0]+curr_pos[0]) / 2, (new_pos[1] + curr_pos[1]) / 2
    # print("Creating shape...")
    pp_shape = pymunk.Segment(pp_body,(new_pos),(curr_pos),1)
    print(f"Body: {pp_body.position}, Line: {pp_shape.a,pp_shape.b}")
    pp_shape.collision_type = 9 
    # print("Adding to space...")
    physics.space.add(pp_body,pp_shape)
    # print("Checking overlap...")
    pp_overlaps, pp_point = check_collision_all(pp_shape,objects)
    # print(f"Point returned from abstraction: {pp_point}")
    # print("Removing from space...")
    physics.space.remove(pp_body,pp_shape)
    # Whether projected path is valid
    # print("Determining validity...")
    valid_pp = not any(pp_overlaps)
    valid_pp = True
    # print(f"Valid: {valid_pp}")
    if pp_point:
        new_pos = pp_point

    # print(f"The new position: {new_pos}")
    return new_pos, valid_pp
