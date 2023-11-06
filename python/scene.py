import abstraction
import json

from copy import deepcopy
from graphics import Graphics
from physics import Physics


def get_ball_position(objects):
    for obj in objects:
        if obj.name == "Ball":
            return deepcopy(obj.body.position)


def get_ball_velocity(objects):
    for obj in objects:
        if obj.name == "Ball":
            return deepcopy(obj.body.velocity)


def set_ball_velocity(objects, velocity, space):
    space.reindex_static()
    for obj in objects:
        space.reindex_shapes_for_body(obj.body)
        if obj.name == "Ball":
            obj.body.velocity = velocity



def set_ball_position(objects, position, space):
    space.reindex_static()
    for obj in objects:
        space.reindex_shapes_for_body(obj.body)
        if obj.name == "Ball":
            obj.body.position = position


class Scene:
    """A class object for scenes."""
    def __init__(self, objects, screen_size=None, args=None):
        self.physics = Physics()
        if screen_size:
            self.graphics = Graphics(*screen_size)
        else:
            self.graphics = Graphics()
        self.objects = objects
        self.running = True
        # Probability of collision between Ball and Goal
        self.collision_prob = None
        # Tick samples from stochastic runs
        self.tick_samples = []
        # Flag for user to pause simulation
        self.pause = False
        self.sensor_obj = None
        self.trace = []
        self.ball_distance_traveled = 0
        self.computation_choice = []
        if args:
            with open(args, 'r') as f:
                self.args = json.loads(f.read())
        else:
            self.args = None
        self.collide_with_goal = False


    def calculate_distance_ball_traveled(self,previous_point):
        """Compute the distance of the ball's trajectory."""
        for o in self.objects:
            if o.name == "Ball":
                current_position = o.body.position
                self.ball_distance_traveled += current_position.get_distance(
                    previous_point)


    def run_path(self, view:bool=True, N:int=5, D:float=100, E:float=0.9):
        """Blended forward method for the scene.
        
        Evolves PObjects over time according to a simulator and the path
        projection abstraction, and renders the scene to the screen with a
        Graphics.

        Args:
            view: Boolean that determines whether the scene is rendered.
            N: An integer of the ticks a simulator can take.
            D: An integer of the length of the path projection.
            E: A float of the cosine similarity threshold.
        """
        # Initialize graphics engine
        if view and not self.graphics.initialized:
            self.graphics.initialize_graphics()
        # Main loop
        while self.running:
            # Get position from simulation
            ball_pos_start = get_ball_position(self.objects)
            ball_velocity_start = get_ball_velocity(self.objects)
            # Simulation for N steps
            for _ in range(N):
                # Physics
                self.physics.forward()
                self.physics.space.reindex_static()
                self.running *= not self.physics.collision_border_end()
                self.running *= not self.physics.collision_goal_end()
                if self.physics.collision_goal_end():
                    self.collide_with_goal = True
                self.running *= self.graphics.running
                self.running *= self.physics.tick < 3000
                # Graphics
                if view:
                    # Draw objects
                    self.graphics.draw(self.objects)
                    self.graphics.clock.tick(self.graphics.fps)
                    self.graphics.update_display()
                # Get position from simulation
                ball_pos_sim = get_ball_position(self.objects)
                # Abstraction for one step
                ball_pos_pp = abstraction.new_position(
                    ball_pos_start,
                    ball_velocity_start,
                    self.objects,
                    D)
                try:
                    bps = ball_pos_sim-ball_pos_start
                    bppp = ball_pos_pp-ball_pos_start
                    normsim = bps.length
                    normpp = bppp.length
                    dot = bps.dot(bppp)
                    cossim = dot / (normsim * normpp)
                except ZeroDivisionError:
                    cossim = 0
                if cossim > E:
                    set_ball_position(
                        self.objects,ball_pos_pp,self.physics.space)
                    set_ball_velocity(
                        self.objects,ball_velocity_start,self.physics.space)
                    self.computation_choice.append(0)
                else:
                    self.computation_choice.append(1)
                self.calculate_distance_ball_traveled(ball_pos_start)
        self.computation_choice = sum(
            self.computation_choice) / len(self.computation_choice)

    def run(self,view=True):
        """Forward method for pure simulation.
        
        Evolves PObjects over time according to a simulator and the path
        projection abstraction, and renders the scene to the screen with a
        Graphics.

        Args:
            view: Boolean that determines whether the scene is rendered.
        """
        # Initialize graphics engine
        if view and not self.graphics.initialized:
            self.graphics.initialize_graphics()

        # Main loop
        while self.running:
            # print(self.physics.tick)
            # Physics
            if not self.pause:
                for o in self.objects:
                    self.physics.space.reindex_static()
                    self.physics.space.reindex_shapes_for_body(o.body)
                    if o.name == "Ball":
                        ball_previous_position = o.body.position
                        self.trace.append(ball_previous_position)
                self.physics.forward()
                self.running *= not self.physics.collision_border_end()
                self.running *= not self.physics.collision_goal_end()
                if self.physics.collision_goal_end():
                    self.collide_with_goal = True
                self.running *= self.graphics.running
                self.calculate_distance_ball_traveled(ball_previous_position)
            if self.physics.tick > 3000:
                self.running = False

            # Graphics
            if view:
                self.graphics.draw(self.objects,self.physics.tick)
                self.graphics.clock.tick(self.graphics.fps)
                self.graphics.update_display()
        self.computation_choice = 1


    def instantiate_scene(self):
        """Instantiates the objects into the scene."""
        for obj in self.objects:
            self.physics.space.add(*obj.components)
