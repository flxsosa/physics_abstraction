from pygame.locals import *

END_STATE = []
GOAL_BALL = []
GOAL_SENSOR = []

def teleporter(arbiter, space, data):
    a = space.bodies[-1]
    b = space.bodies[-2]
    a.position = b.position[0], b.position[1]+41
    return True

def end_state(arbiter, space, data):
    if END_STATE:
        return True
    END_STATE.append(1)
    return True

def goal_ball(arbiter, space, data):
    if GOAL_BALL:
        return True
    END_STATE.append(1)
    GOAL_BALL.append(1)
    return True

def goal_sensor(arbiter, space, data):
    if GOAL_SENSOR:
        return True
    GOAL_SENSOR.append(1)
    return True

def is_colliding(arbiter, space, data):
    data['colliding'] = True
    return True

def not_colliding(arbiter, space, data):
    data['colliding'] = False
    return True

def straight_path(arbiter,space,data):
    return True