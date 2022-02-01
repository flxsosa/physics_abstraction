from math import cos, sin, pi, radians
from turtle import Vec2D
import numpy as np
import pymunk
import pygame
from pymunk.pygame_util import *
from pymunk import Transform, Vec2d
from helper import rotate

# Straight Path

def straight_path_collision(objects,graphics=None,physics=None):
    '''
    Subroutine for checking whether there exists a straight path
    between the Ball in a Scene and the Goal or Floor. Uses
    Pymunk.Shape as the datatype for the sensor.

    :param objects: List of PObjects in the Scene.
    :param graphics: Graphics engine used for convenience drawing methods.
    :param physics: Physics engine used for adding the sensor to the Scene.
    '''
    # Get the ball
    for obj in objects:
        if obj.name == "Ball":
            ball = obj
    
    # Constrcut shape around ball
    sensorshape = get_shape(ball)
    
    # Add sensor to Scene
    physics.space.add(sensorshape)
    
    # Check if sensorshape is colliding with anything
    coll_g,coll_c,coll_f = check_collision(sensorshape,objects)
    
    # Draw the sensorshape onto the screen
    # debug_draw_shape(graphics,physics.space)
    # draw_shape(sensorshape,graphics.screen)
    
    # Remove the sensorshape from the Scene
    physics.space.remove(sensorshape)
    
    # Return collision
    if coll_g and not coll_c:
        return True, "goal"
    elif coll_f and not coll_c:
        return True, "floor"
    else:
        return False, "nothing"

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

def debug_draw_shape(graphics,space):
    '''
    Draws all shapes in a space to the screen using pymunk.debug_draw 
    method.

    :param graphics: Graphics engine for drawing.
    :param space: Physics engine space for debug_draw method.
    '''
    graphics.debug_draw(space)

def draw_shape(shape, screen):
    '''
    Draws a single shape to the screen using pygame's draw methods.

    :param shape: Shape to be drawn to screen.
    :param screen: Screen to which the shape is drawn.
    '''
    # Grab points
    points = shape.get_vertices()
    world_coords = shape.body.position
    print(world_coords)
    for i in range(len(points)):
        points[i] = points[i].rotated(shape.body.angle)
        points[i] += world_coords
    # Select color
    color = pygame.Color("Black")
    # Draw to screen via pygame
    pygame.draw.polygon(screen,color,points)

def check_collision(sensorshape,objects,verbose=False):
    '''
    Checks for overlap between sensor and objects in a Scene.

    :param sensorshape: Sensor, expected to be a Pymunk.Shape.
    :param objects: List of PObjects in Scene.
    :param verbose: Flag for printing value of collision flags.
    '''
    # Update angle of sensor's body to point in the direction of its velocity
    update_angle(sensorshape)
    # Set all collision flags to false
    coll_containers = False
    coll_goal = False
    coll_floor = False

    # Iterate through objects in scene, and check for overlap with sensor
    for o in objects:  
        # Containers and Lines
        if o.name == "Container" or o.name == "Line":
            # We skip the first element in the components because that's the body
            for line in o.components[1:]:
                body = o.components[0]
                offset = body.position
                a = rotate(body, line.a)
                b = rotate(body, line.b)
                coll_containers = bool(sensorshape.segment_query(a+offset, b+offset).shape) or coll_containers
        # Floor of game
        elif o.name == "BottomBorder":
            # We skip the first element in the components because that's the body
            for line in o.components[1:]:
                body = o.components[0]
                offset = body.position
                a = rotate(body, line.a)
                b = rotate(body, line.b)
                coll_floor = bool(sensorshape.segment_query(a+offset, b+offset).shape) or coll_floor
        # Goal
        elif o.name == "Goal":
            goalshape = o.components[1]
            coll_goal = bool(sensorshape.shapes_collide(goalshape).points)
    
    # Print value of collision flags if requested
    if verbose:
        print(f"We {'are' if coll_containers else 'are not'} colliding w/ containers.")
        print(f"We {'are' if coll_goal else 'are not'} colliding w/ goal.")
        print(f"We {'are' if coll_floor else 'are not'} colliding w/ floor.")

    # Return collision flags
    return coll_goal, coll_containers, coll_floor

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

def path_projection(objects, graphics, physics, D=100):
    '''
    Could check out position_func in pymunk
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
