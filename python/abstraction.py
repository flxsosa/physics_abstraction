"""Utilities for the abstraction method in the physics abstraction project."""
import objects as pobjects
import numpy as np

from typing import Union
from pymunk import vec2d
from shapely import geometry

GLOB = 1

def check_collision_old(
        line_polygon:geometry.LineString,
        simulation_objects:list[pobjects.PObject],
        scene) -> (bool, vec2d.Vec2d): #FIXME
    """Check projection polygon intersects with other polygons in the scene.

    Args:
        line_polygon: Path projection Polygon object
        simulation_objects: List of objects in Scene

    Outputs:
        collision_result: Tuple of whether collision occured location of coll.
    """
    path_projection_origin = [
        round(x, 2) for x  in np.asarray(line_polygon.coords)[0]
        ]
    for obj in simulation_objects:
        if (line_polygon.intersects(obj.area) or
            line_polygon.intersection(obj.area)) and obj.name != "Ball":
            line_of_collision_coords = np.asarray(
                line_polygon.intersection(obj.area).coords)
            intersect_point_a = [
                round(x, 2) for x in line_of_collision_coords[0]
                ]
            intersect_point_b = [
                round(x, 2) for x in line_of_collision_coords[1]
                ]
            distance_to_point_a = geometry.LineString(
                [path_projection_origin, intersect_point_a]).length
            distance_to_point_b = geometry.LineString(
                [path_projection_origin, intersect_point_b]).length
            if distance_to_point_a <= distance_to_point_b:
                return True, vec2d.Vec2d(*intersect_point_a)
            return True, vec2d.Vec2d(*intersect_point_b)
    return False, vec2d.Vec2d(1,1)



def check_collision(
        line_polygon:geometry.LineString,
        simulation_objects:list[pobjects.PObject]) -> (bool, vec2d.Vec2d):
    """Check projection polygon intersects with other polygons in the scene.

    Args:
        line_polygon: Path projection Polygon object
        simulation_objects: List of objects in Scene

    Outputs:
        collision_result: Tuple of whether collision occured location of coll.
    """
    path_projection_coords = np.asarray(line_polygon.coords)
    path_projection_origin = [round(x, 2) for x  in path_projection_coords[0]]
    collision_point = vec2d.Vec2d(1,1)
    distance_to_point = np.inf
    collision_flag = False
    for obj in simulation_objects:
        if line_polygon.intersects(obj.area) and obj.name != "Ball":
            line_of_collision_coords = np.asarray(
                line_polygon.intersection(obj.area).coords)
            intersect_point_a = line_of_collision_coords[0]
            distance_to_point_a = geometry.LineString(
                [path_projection_origin, intersect_point_a]).length
            if distance_to_point_a <= distance_to_point:
                collision_flag = True
                collision_point = vec2d.Vec2d(*intersect_point_a)
                distance_to_point = distance_to_point_a
            if len(line_of_collision_coords) == 2:
                intersect_point_b = line_of_collision_coords[1]
                distance_to_point_b = geometry.LineString(
                    [path_projection_origin, intersect_point_b]).length
                if distance_to_point_b <= distance_to_point:
                    collision_flag = True
                    collision_point = vec2d.Vec2d(*intersect_point_a)
                    distance_to_point = distance_to_point_b
    return collision_flag, collision_point


def create_path_poly(
        point_a:list[Union[int, float]],
        point_b:list[Union[int, float]]) -> geometry.LineString:
    """Creates a geometry.LineString between two points."""
    return geometry.LineString([point_a, point_b])


def new_position(
        original_point:list[Union[int, float]],
        velocity_vector:vec2d.Vec2d,
        objects:list[pobjects.PObject],
        D:Union[int, float]) -> vec2d.Vec2d:
    '''
    Path projection subroutine

    :param objects: Set of objects in the scene
    :param D: Length of path projection
    '''
    # Detemine position
    current_point = [round(x, 2) for x in original_point]
    # Get velocity vector direction
    velocity_vector = velocity_vector.normalized()
    # We do not project if the ball is moving up or is stationary
    if velocity_vector[1] < 0 or velocity_vector == vec2d.Vec2d(0,0):
        return current_point
    updated_point = current_point + (velocity_vector) * D
    updated_point = [round(x, 2) for x in updated_point]
    # Check whether path collides with any other objects
    line_polygon = create_path_poly(current_point, updated_point)
    collision_flag, point_of_collision = check_collision(
        line_polygon, objects)
    # Whether projected path is valid
    if collision_flag:
        updated_point = point_of_collision - velocity_vector*20
    return updated_point
