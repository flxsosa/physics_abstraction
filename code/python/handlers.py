from pygame.locals import *

def teleporter(arbiter, space, data):
    a = space.bodies[-1]
    b = space.bodies[-2]
    a.position = b.position[0], b.position[1]+41
    return True