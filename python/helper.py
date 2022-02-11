from math import cos, sin
import numpy as np
import pygame
# import cv2
import numpy as np


def rotate(body,point):
    rotatedx = point[0] * cos(body.angle) - point[1] * sin(body.angle)
    rotatedy = point[0] * sin(body.angle) + point[1] * cos(body.angle)
    return (rotatedx, rotatedy)

def draw_scanner(screen,body,scale):
    mx,my = body.position + np.multiply(body.velocity.normalized(), scale)
    pygame.draw.line(screen, pygame.Color("green"), (mx,my),body.position)

def make_video(screen,scene_name,dir):
    '''
    Generates screenshots from a simulation

    screen::screen -- a pygame screen on which the simulation is rendered
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
    pass
#     print(f"Passed movie directory: {dir}")
#     print(f"Passed movie Scene Name: {scene_name}")
#     '''
#     Takes images generated from make_video and stitches them into a video

#     name::str -- name of the simulation for file naming
#     dir::str  -- parameter for globbing the files together
#     '''
#     img_dic = {}
#     img_str = []
#     size = 0,0
#     for filename in glob.glob(dir+filetype):
#         img = cv2.imread(filename)
#         h,w,l =img.shape
#         size = (img.shape[1],img.shape[0])
#         img_str.append(filename)
#         img_dic[filename] = img

#     out = cv2.VideoWriter(dir+scene_name+'.mp4', cv2.VideoWriter_fourcc(*'avc1'),60,size)
#     img_str.sort()

#     for i in img_str:
#         out.write(img_dic[i])

#     out.release()
#     os.system("rm "+ dir +"*.jpg")

def draw_circle_alpha(surface, color, center, radius):
    '''
    Draws a circle on the screen with variable alpha values
    '''
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)

def draw_application(surface, color, center, radius):
    pygame.draw.line(surface, color, 
                     (center[0]-radius,center[1]-radius),(center[0]+radius,center[1]+radius),
                     4)
    pygame.draw.line(surface, color, 
                     (center[0]+radius,center[1]-radius),(center[0]-radius,center[1]+radius),
                     4)

def adjust_body_angle(object):
    '''
    Adjusts the object body's angle to point in the velocity vector's direction
    '''
    x,y = object.body.velocity.normalized()
    angle = np.arctan2(y,x)
    object.body.angle = math.radians(180*angle/math.pi - 90)     