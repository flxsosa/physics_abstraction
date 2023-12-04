"""Custom collision handler callbacks for the physics abstraction project."""

import pymunk

from typing import Any, Union

def is_colliding(
        arbiter:pymunk.Arbiter,
        space:pymunk.Space,
        data:dict[Any,Any]):
    """Callback for determing which two objects are colliding.
    
    Args:
        arbiter: A Pymunk.arbiter.
        space: A pymunk.space.
        data: A dicitonary of collision data."""
    s1,s2 = arbiter.shapes
    data['colliding'] = True
    data['collision_trace'].append([id(s1),id(s2)])
    data['normal'] = arbiter.normal
    data['cps'] = arbiter.contact_point_set
    return True
