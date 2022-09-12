from pygame.locals import *

END_STATE = []
GOAL_BALL = []
GOAL_SENSOR = []

def is_colliding(arbiter, space, data):
    s1,s2 = arbiter.shapes
    data['colliding'] = True
    data['collision_trace'].append([id(s1),id(s2)])
    return True

def count_collision(arbiter, space, data):
    data['num_collision'] += 1
    return True

def not_colliding(arbiter, space, data):
    data['colliding'] = False
    return True

def straight_path(arbiter,space,data):
    return True