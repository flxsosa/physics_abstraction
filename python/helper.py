from math import cos, sin, radians, pi
import numpy as np
import pygame
import cv2
import numpy as np
import os
import glob


def rotate(body,point):
    '''
    Rotates a pymunk body around a point

    :param body: Body to rotate
    :param point: Point to rotate body around
    '''
    rotatedx = point[0] * cos(body.angle) - point[1] * sin(body.angle)
    rotatedy = point[0] * sin(body.angle) + point[1] * cos(body.angle)
    return (rotatedx, rotatedy)

def draw_scanner(screen,body,scale):
    '''
    Draws a scanner object on screen using Pygame

    :param screen: Screen to render scanner to
    :param body: Body of scanner
    :param scale: Scale of drawing
    '''
    mx,my = body.position + np.multiply(body.velocity.normalized(), scale)
    pygame.draw.line(screen, pygame.Color("green"), (mx,my),body.position)

def make_video(screen,scene_name,dir):
    '''
    Generates screenshots from a simulation

    :param screen: Pygame screen on which the simulation is rendered
    :param scene_name: Name of the scene
    :param dir: Directory to which to save video
    '''
    print(f"Passed Image Save Dir: {dir}")
    print(f"Passed Image Save Name: {scene_name}")
    pygame.init()
    img_num = 0
    while True:
        img_num += 1
        str_num = "00"+str(img_num)
        file_name = dir+scene_name+str_num[-3:]+".jpg"
        pygame.image.save(screen,file_name)
        yield

def vid_from_img(scene_name,dir,filetype="*.jpg"):
    '''
    Takes images generated from make_video and stitches them into a video
    [DEPRECATED]
    :param scene_name: Name of the simulation for file naming
    :param filetype: Glob parameter
    :param dir: Location to save video to
    '''
    print(f"Passed movie directory: {dir}")
    print(f"Passed movie Scene Name: {scene_name}")
    img_dic = {}
    img_str = []
    size = 0,0
    for filename in glob.glob(dir+filetype):
        img = cv2.imread(filename)
        h,w,l =img.shape
        size = (img.shape[1],img.shape[0])
        img_str.append(filename)
        img_dic[filename] = img
    out = cv2.VideoWriter(dir+scene_name+'.mp4', cv2.VideoWriter_fourcc(*'avc1'),60,size)
    img_str.sort()
    for i in img_str:
        out.write(img_dic[i])
    out.release()
    os.system("rm "+ dir +"*.jpg")

def draw_circle_alpha(surface, color, center, radius):
    '''
    Draws a circle on the screen with variable alpha values

    :param surface: Surface to draw to
    :param color: Color of the shape
    :param center: Center point of shape on screen
    :param radius: Radius of shape
    '''
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)

def draw_application(surface, color, center, radius):
    '''
    Draw the point at which an abstraction was applied and accepted

    :param surface: Surface to draw to
    :param color: Color of the shape
    :param center: Center point of shape on screen
    :param radius: Radius of shape
    '''
    pygame.draw.line(surface, color, 
                     (center[0]-radius,center[1]-radius),(center[0]+radius,center[1]+radius),
                     4)
    pygame.draw.line(surface, color, 
                     (center[0]+radius,center[1]-radius),(center[0]-radius,center[1]+radius),
                     4)

def adjust_body_angle(object):
    '''
    Adjusts the object body's angle to point in the velocity vector's direction

    :param object: Object to be adjusted
    '''
    x,y = object.body.velocity.normalized()
    angle = np.arctan2(y,x)
    object.body.angle = radians(180*angle/pi - 90)     