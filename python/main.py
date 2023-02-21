'''
File for scratch jobs and testing. Frequently overwritten.
'''
from utility import load_scene
import models as m
import os
import pygame
from pygame.locals import QUIT
from objects import *

def get_border(obj, screen_size):
    '''
    Grab the actual X,Y position of the border object and return position
    and size
    '''
    # Offset term for border position
    eps = 10
    if obj.name == "BottomBorder":
        y = screen_size[1] - eps # Border will be at bottom of screen
        x = screen_size[0] / 2
    else:
        y = screen_size[1] / 2
        x = screen_size[0] - eps
    return (x,y)

def main_test():
    # Load in a scene
    loaddir = "../data/json/pilot8/trial/"
    json_files = [pos_json for pos_json in os.listdir(loaddir) if pos_json.endswith('.json')]
    scene_file = json_files[0]
    scene = load_scene(loaddir+scene_file)

    # Set up graphics parameters
    fps = pygame.time.Clock()
    screen_size = (800,1000)
    pygame.init()
    screen = pygame.display.set_mode(screen_size)

    # Starting angle for cursor shape
    angle = 90

    # Font parameters
    font = pygame.font.Font('freesansbold.ttf', 12)

    # Game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONUP:
                angle += 10
                angle %= 360

        # Fill screen
        screen.fill((0,0,0))

        # Go through objects and draw them on the screen with their names
        for o in scene.objects:
            pygame.draw.polygon(screen, pygame.Color("Red"), o.bounding_box)
            # Create pygame text object
            text = font.render(o.name, True, pygame.Color("White"), pygame.Color("Black"))
            textRect = text.get_rect()
            textRect.center = o.body.position # Set the object to the body's position
            screen.blit(text, textRect)

        # # Create "Container"
        container1 = Container(pygame.mouse.get_pos(), 50, 80, angle, 99, 10)
        pygame.draw.polygon(screen, pygame.Color("Red"), container1.bounding_box)
    
        
        for obj in scene.objects:
            if container1.area.intersects(obj.area):
                # Create pygame text object
                text = font.render("Collision Detected", True, pygame.Color("White"), pygame.Color("Black"))
                textRect = text.get_rect()
                textRect.center = [400,100] # Set the object to the body's position
                screen.blit(text, textRect)
                pygame.draw.polygon(screen, pygame.Color("Green"), container1.bounding_box)

        # Forward the graphics one step
        pygame.display.update()
        fps.tick(60)

def main():
    # Load in a scene
    loaddir = "../data/json/pilot8/trial/"
    json_files = [pos_json for pos_json in os.listdir(loaddir) if pos_json.endswith('.json')]
    scene_file = json_files[1]
    scene_file = "stim_2_goalpos_12_negative.json"
    scene = load_scene(loaddir+scene_file)

    # sim = m.simulation(scene.args,1,0,True)
    # print(sim)
    abs = m.abstraction(scene.args,N=5,D=100,E=0.8,num_samples=1,noise=10,view=True)

if __name__ == "__main__":
    main()