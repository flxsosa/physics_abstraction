"""Graphics module for rendering simulations to screen."""

import math
import pygame
import pymunk
import objects as pobjects
import random

from pymunk import pygame_util
from pygame.locals import *
from typing import Union


class Graphics:
    """A Graphics renders PObjects onto a screen."""
    def __init__(self, width:int=800, height:int=1500, fps:int=60):
        self.screen_size = width,height
        self.framework = pygame
        self.screen = None
        self.size = width,height
        self.clock = None
        self.fps = fps
        self.screen_recorder = None
        self.running = True
        self.initialized = False
        self.debug_options = None
        self.simulation_trace = []
        self.abstraction_trace = []
        self.decision_points = []
        self.simulation_line_trace = []
        self.draw_params = {
            'Ball':pygame.Color(
                random.randrange(156),
                random.randrange(156),
                random.randrange(156)),
            'Goal':pygame.Color(
                random.randrange(156),
                random.randrange(156),
                random.randrange(156)),
            'Container':pygame.Color('Black'),
            'Block':pygame.Color(102,102,102),
            'Border':pygame.Color('Black'),
            'ball_alpha':False,
            'trace':[],
            'record_trace':True,
            'bounding_boxes':True
            }


    def instantiate_screen_recorder(self, dir:str, fname:str):
        """Method for instantiating the screen recorder."""
        self.screen_recorder = self._record_screen(dir,fname)


    def instantiate_camera(self, dir:str, fname:str):
        """Method for instantiating the camera."""
        self.screen_recorder = self._take_snapshot(dir,fname)


    def _record_screen(self, dir:str, fname:str):
        """Private method for recording frames from a Graphic's screen."""
        img_num = 0
        while True:
            img_num += 1
            str_num = '00'+str(img_num)
            file_name = dir+fname+str_num[-3:]+'.jpg'
            self.framework.image.save(self.screen,file_name)
            yield


    def _take_snapshot(self, dir:str, fname:str):
        file_name = dir+fname+'.jpg'
        self.framework.image.save(self.screen, file_name)


    def draw_bounding_box(self, bb:list[Union[int,float]]):
        pos = bb.left, bb.bottom
        width = bb.right - bb.left
        height = bb.top - bb.bottom
        point_on_screen = pygame_util.to_pygame(pos, self.screen)
        pygame.draw.rect(
            self.screen,
            pygame.Color('Blue'),
            (*point_on_screen, width, height),
            1)


    def draw_circle_at_point(
            self,
            pos:list[Union[int,float]],
            color:str='Black',
            size:int=20):
        color = pygame.Color(color)
        pygame.draw.circle(self.screen, color, pos, size)


    def draw_simulation_trace_of_ball(
            self,
            trace:list[list[Union[int, float]]],
            color:str='Black'):
        self.simulation_trace += trace
        color = pygame.Color(color)
        for point in self.simulation_trace:
            pygame.draw.circle(self.screen, color, point, 5)


    def draw_abstraction_trace_of_ball(
            self,
            trace:list[list[Union[int, float]]],
            color:str='Red'):
        self.abstraction_trace.append(trace)
        color = pygame.Color(color)
        for line in self.abstraction_trace:
            pygame.draw.line(self.screen, color, line[0], line[1],5)


    def draw_simulation_line_trace_of_ball(
            self,
            trace:list[list[Union[int, float]]],
            color:str='Yellow'):
        self.simulation_line_trace += trace
        color = pygame.Color(color)
        for line in self.simulation_line_trace:
            pygame.draw.line(self.screen, color, line[0], line[1],5)


    def draw_decision_points_of_ball(
            self,
            point:list[Union[int, float]],
            color:str='Green'):
        if point not in self.decision_points:
            self.decision_points.append(point)
        color = pygame.Color(color)
        for decision_point in self.decision_points:
            pygame.draw.circle(self.screen, color, decision_point, 10)


    def draw_circle_alpha(
            self,
            surface:pygame.Surface,
            color:str,
            center:list[Union[int,float]],
            radius:Union[int,float]):
        """Draws a circle on the screen with variable alpha values

        Args:
            surface: Surface to draw to
            color: Color of the shape
            center: Center point of shape on screen
            radius: Radius of shape
        """
        target_rect = pygame.Rect(
            center, (0, 0)).inflate((radius * 2, radius * 2))
        shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
        pygame.draw.circle(shape_surf, color, (radius, radius), radius)
        surface.blit(shape_surf, target_rect)


    def update_display(self):
        """Method for updating display."""
        # Update display
        pygame.display.update()
        # If recording screen, record screen
        if self.screen_recorder:
            next(self.screen_recorder)


    def draw(self,
             simulation_objects:list[pobjects.PObject],
             tick:Union[int, None]=None):
        """Drawing method for graphics engine."""
        # Fill screen with background, and refresh each frame
        self.screen.fill(pygame.Color("gray"))
        # Iterate and draw objects
        for obj in simulation_objects:
            # Drawing the ball
            if obj.name == "Ball":        
                if self.draw_params.get('ball_alpha'):
                    # Get color object of Ball
                    color = self.draw_params['Ball']
                    # Set alpha value of color object according to curent tick
                    color.a = int(255-tick*4) if int(255-tick*4) > 0 else 0
                    # Draw circle
                    self.draw_circle_alpha(
                        self.screen,
                        color,
                        obj.body.position,
                        20)
                    # Once shape disappears, end simulation
                    if color.a == 0:
                        self.running = False
                elif self.draw_params['record_trace']:
                    color = pygame.Color('Black')
                    self.draw_params['trace'].append(obj.body.position)
                    for point in self.draw_params['trace']:
                        pygame.draw.circle(
                            self.screen,
                            color,
                            pygame_util.to_pygame(point, self.screen),
                            20)
                    color = self.draw_params['Ball']
                    pygame.draw.circle(
                        self.screen,
                        color,
                        pygame_util.to_pygame(obj.body.position, self.screen),
                        20)
                    for line in obj.components[2:]:
                        body = obj.components[0]
                        offset = body.position
                        pygame.draw.line(
                            self.screen,
                            color,
                            line.a+offset,
                            line.b+offset,5)
                elif self.draw_params.get('bounding_boxes'):
                    self.draw_bounding_box(obj.components[1].bb)
                else:
                    color = self.draw_params['Ball']
                    pygame.draw.circle(
                        self.screen,
                        color,
                        pygame_util.to_pygame(obj.body.position, self.screen),
                        20)
                    for line in obj.components[2:]:
                        body = obj.components[0]
                        offset = body.position
                        pygame.draw.line(
                            self.screen,
                            color,
                            line.a+offset,
                            line.b+offset,
                            5)
            # Drawing the goal
            elif obj.name == 'Goal':
                color = self.draw_params['Goal']
                rectangle = pygame.Rect(0,0,obj.length+1,obj.width+1)
                rectangle.center = obj.body.position
                pygame.draw.rect(self.screen, color, rectangle)
                # FIXME
                font = pygame.font.Font('freesansbold.ttf', 24)
                # FIXME
                text = font.render(
                    f'Goal',
                    True,
                    pygame.Color('White'),
                    pygame.Color('Black'))
                # FIXME
                textRect = text.get_rect()
                # FIXME
                textRect.center = obj.body.position
                # FIXME
                self.screen.blit(text, textRect)
                if self.draw_params.get('bounding_boxes'):
                    self.draw_bounding_box(obj.components[1].bb)
            # Drawing border and containers
            elif obj.name in ['Container', 'Line']:
                color = self.draw_params['Container']
                # We skip the first element in the components because that's
                #   the body.
                for line in obj.components[1:]:
                    body = obj.components[0]
                    offset = body.position
                    # FIXME
                    font = pygame.font.Font('freesansbold.ttf', 24)
                    # FIXME
                    text = font.render(
                        f'{obj.id}',
                        True,
                        pygame.Color('White'),
                        pygame.Color('Black'))
                    # FIXME
                    textRect = text.get_rect()
                    # FIXME
                    textRect.center = offset
                    # FIXME
                    self.screen.blit(text, textRect)
                    line_point_a = self.rotate(body, line.a)
                    line_point_b = self.rotate(body, line.b)
                    pygame.draw.line(
                        self.screen,
                        color,
                        line_point_a+offset,
                        line_point_b+offset,
                        5)
                    if self.draw_params.get('bounding_boxes'):
                        self.draw_bounding_box(line.bb)
            # Drawing border and containers
            elif 'Border' in obj.name:
                color = self.draw_params['Border']
                # We skip the first element in the components because that's
                #   the body.
                for line in obj.components[1:]:
                    body = obj.components[0]
                    offset = body.position
                    line_point_a = self.rotate(body, line.a)
                    line_point_b = self.rotate(body, line.b)
                    pygame.draw.line(
                        self.screen,
                        color,
                        line_point_a+offset,
                        line_point_b+offset,
                        5)
        for obj in simulation_objects:
            if obj.name == 'BottomBorder':
                line = obj.components[1]
                y_point = line.a[1]+3
                color = pygame.Color('gray')
                radius = pygame.Rect(0, y_point, 800, 1000-y_point)
                pygame.draw.rect(self.screen, color, radius)


    def rotate(self, body:pobjects.PObject, point:list[Union[int, float]]):
        rotatedx = (
            point[0] * math.cos(body.angle) - point[1] * math.sin(body.angle))
        rotatedy = (
            point[0] * math.sin(body.angle) + point[1] * math.cos(body.angle))
        return (rotatedx, rotatedy)


    def initialize_graphics(self):
        self.initialized = True
        self.debug_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.screen = self.framework.display.set_mode(
            self.size, pygame.RESIZABLE)
        self.clock = self.framework.time.Clock()
        self.framework.init()
