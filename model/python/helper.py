from math import cos, sin, radians

def rotate(body,point):
    rotatedx = point[0] * cos(body.angle) - point[1] * sin(body.angle)
    rotatedy = point[0] * sin(body.angle) + point[1] * cos(body.angle)
    return (rotatedx, rotatedy)