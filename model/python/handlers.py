from pygame.locals import *

END_STATE = []
GOAL_BALL = []

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