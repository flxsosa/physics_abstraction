
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
<<<<<<< HEAD
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
                # print(f"Container body: {o.body.position} Line: {line.a,line.b}")
                # print(f"Normal: {line.normal}")
                if sensorshape.point_query(o.body.position).distance < 0:
                    # print(f"Colliding with {o.id}: {sensorshape.point_query(o.body.position)}")
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
        # print(f"New position should be: {collision_points[0]['new_pos']}")
        # print(" ")
    # Print value of collision flags if requested
    if verbose:
        print(f"We {'are' if coll_containers else 'are not'} colliding w/ containers.")
        print(f"We {'are' if coll_goal else 'are not'} colliding w/ goal.")
        print(f"We {'are' if coll_border else 'are not'} colliding w/ floor.")

    # Return collision flags
    return (coll_goal, coll_containers, coll_border), new_pos
=======
    # Check if polygon collides with objects
    for obj in objects:
        if path_poly.intersects(obj.area) and obj.name != "Ball":
            line_of_intersection = path_poly.intersection(obj.area).coords
            highest_point = min(line_of_intersection, key=lambda x: x[1])
            return True, Vec2d(*highest_point)
    return False, Vec2d(1,1)
>>>>>>> d7149f12597bf9866de9a0caace939b60071e0bd

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
<<<<<<< HEAD
    # print("Creating body...")
    pp_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    # pp_body.position = (new_pos[0]+curr_pos[0]) / 2, (new_pos[1] + curr_pos[1]) / 2
    # print("Creating shape...")
    pp_shape = pymunk.Segment(pp_body,(new_pos),(curr_pos),1)
    # print(f"Body: {pp_body.position}, Line: {pp_shape.a,pp_shape.b}")
    pp_shape.collision_type = 9 
    # print("Adding to space...")
    physics.space.add(pp_body,pp_shape)
    # print("Checking overlap...")
    pp_overlaps, pp_point = check_collision_all(pp_shape,objects)
    # print(f"Point returned from abstraction: {pp_point}")
    # print("Removing from space...")
    physics.space.remove(pp_body,pp_shape)
=======
    pp_shape = create_path_poly(curr_pos,new_pos,20)
    pp_collision, pp_point_of_collision = check_collision(pp_shape,objects)
>>>>>>> d7149f12597bf9866de9a0caace939b60071e0bd
    # Whether projected path is valid
    if pp_collision:
        new_pos = pp_point_of_collision - velocity_vector*20
    return new_pos
