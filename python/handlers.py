from pygame.locals import *

END_STATE = []
GOAL_BALL = []
GOAL_SENSOR = []

def is_colliding(arbiter, space, data):
    data['colliding'] = True
    return True

def not_colliding(arbiter, space, data):
    data['colliding'] = False
    return True

def straight_path(arbiter,space,data):
    return True