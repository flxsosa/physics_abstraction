"""Utilities for invoking models in the physics abstraction project."""
from typing import Any, Callable
import scene
import json_utilities
import pydantic
import utility
import os
import numpy as np


def model_call_wrapper(model:Callable, model_parameters:dict[str,Any]):
    """A model call wrapper that uses currying."""
    def model_call(input_):
        return model(input_, *model_parameters)
    return model_call


def get_scene_objects(
        object_constructors:Callable,
        object_arguments:pydantic.BaseModel,
        noise=None):
    """Returns a list of object instances for a scene."""
    objects = []
    for obj, obj_args in zip(object_constructors, object_arguments):
        if obj.__name__ == "Ball" and noise:
            noisy_position = obj_args.model_dump()['position']
            noisy_position = noisy_position*np.random.normal(1,noise,2)
            noisy_ball_args = json_utilities.BallConfig(
                position = noisy_position
            )
            objects.append(obj(noisy_ball_args))
        else:
            try:
                objects.append(obj(obj_args))
            except TypeError:
                objects.append(obj())
    return objects


def _get_scene_from_config(
        scene_config:json_utilities.SceneConfig,
        noise:float):
    objects = []
    obj_arg_pairs = utility.get_objects_from_scene_config(
        scene_args_config=scene_config)
    objects = get_scene_objects(
        object_constructors=obj_arg_pairs['object_constructors'],
        object_arguments=obj_arg_pairs['arguments'],
        noise=noise)
    scene_instance = scene.Scene(objects)
    return scene_instance


def _parse_model_output_with_pos(scene_instance:scene.Scene):
    for scene_obj in scene_instance.objects:
        if scene_obj.name == 'Ball':
            pos = list(scene_obj.body.position)
    return ModelOutputWithPos(
        ball_position=pos
    )


def _parse_model_output(scene_instance:scene.Scene):
    return ModelOutput(
        collision=scene_instance.physics.handlers['ball_goal'].data['colliding'],
        simulation_ticks=scene_instance.physics.tick,
        trajectory_length=scene_instance.ball_distance_traveled
    )


class ModelOutput(pydantic.BaseModel):
    """A class for model outputs."""
    collision: bool
    simulation_ticks: int
    trajectory_length: float


class ModelOutputWithPos(pydantic.BaseModel):
    """A class for model outputs."""
    ball_position: list[float]


class PhysModel:
    """Class for models used in Physics Abstraction project."""

    def __init__(self):
        pass


class SimulationModel(PhysModel):
    """Class for pure simulation model."""

    def __init__(self, model_parameters: dict[str, Any]):
        super().__init__()
        self.model_parameters = model_parameters
        self.output = None

    def sample(self, scene_config:json_utilities.SceneConfig):
        """A model call on a given SceneConfig"""
        # Get scene instance
        scene_instance = _get_scene_from_config(
            scene_config=scene_config,
            noise=self.model_parameters['noise'])
        scene_instance.instantiate_scene()
        # Run simulation
        scene_instance.run(view=self.model_parameters['view'])
        # Get model outputs
        self.output = _parse_model_output(scene_instance)
        return self.output


class BlendedModel(PhysModel):
    """Class for blended model."""

    def __init__(self, model_parameters: dict[str, Any]):
        super().__init__()
        self.model_parameters = model_parameters
        self.output = None

    def sample(self, scene_config:json_utilities.SceneConfig):
        """A model call on a given SceneConfig"""
        # Get scene instance
        scene_instance = _get_scene_from_config(
            scene_config=scene_config,
            noise=self.model_parameters['noise'])
        scene_instance.instantiate_scene()
        # Run simulation
        scene_instance.run_path(
            view=self.model_parameters['view'],
            N=self.model_parameters['N'],
            D=self.model_parameters['D'],
            E=self.model_parameters['E']
            )
        # Get model outputs
        self.output = _parse_model_output(scene_instance)
        return self.output

    def sample_with_pos(self, scene_config:json_utilities.SceneConfig):
        """A model call on a given SceneConfig"""
        # Get scene instance
        scene_instance = _get_scene_from_config(
            scene_config=scene_config,
            noise=self.model_parameters['noise'])
        scene_instance.instantiate_scene()
        # Run simulation
        scene_instance.run_path(
            view=self.model_parameters['view'],
            N=self.model_parameters['N'],
            D=self.model_parameters['D'],
            E=self.model_parameters['E']
            )
        # Get model outputs
        self.output = _parse_model_output_with_pos(scene_instance)
        return self.output


def main():
    """Main entrypoint."""
    path_to_scene_dir_exp1 = "../../../Desktop/pydantic/experiment1/"

    scene_json_files_exp1 = [
        pos_json
        for pos_json
        in os.listdir(path_to_scene_dir_exp1)
        if pos_json.endswith('.json')
    ]
    for scene in scene_json_files_exp1:
        path_to_scene_file = path_to_scene_dir_exp1+scene
        scene_config = json_utilities.json_file_to_model(path_to_scene_file)
        simulation_parameters = {
                'noise': 0.02,
                'view': False
            }
        simulation_model = SimulationModel(simulation_parameters)
        simulation_model.sample(scene_config)
        abstraction_parameters = {
            'noise': 0.02,
            'view': False,
            'N': 5,
            'D': 100,
            'E': 0.8
        }
        abstraction_model = BlendedModel(abstraction_parameters)
        abstraction_model.sample(scene_config)


if __name__ == '__main__':
    main()
