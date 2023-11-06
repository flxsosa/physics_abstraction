"""Utilities for JSON functionality in the physics abstractio project."""

import json
from typing import Union, Optional
import pydantic


class LineConfig(pydantic.BaseModel):
    """A datatype representing a line's properties."""
    point_a: list[Union[int, float]]
    point_b: list[Union[int, float]]


class GoalConfig(pydantic.BaseModel):
    """A datatype representing a goal's properties."""
    position: list[Union[int, float]]


class BallConfig(pydantic.BaseModel):
    """A datatype representing a ball's properties."""
    position: list[Union[int, float]]


class ContainerConfig(pydantic.BaseModel):
    """A datatype representing a container's properties."""
    position: list[Union[int, float]]
    width: Union[int, float]
    length: Union[int, float]
    angle: Union[int, float]
    id: Optional[int]=99


class SceneConfig(pydantic.BaseModel):
    """A datatype representing scene configurations."""
    name: str
    screen_size: list[Union[int, float]]
    objects: list[str]
    ball_args: list[BallConfig]
    goal_args: list[GoalConfig]
    container_args: Optional[list[ContainerConfig]] = None
    line_args: Optional[list[LineConfig]] = None
    bottom_border_args: list[list[Union[int, float]]]
    plinko_border_args: list[Union[int, float]]


def dict_to_model(scene_json:dict) -> SceneConfig:
    """Converts JSON object into a SceneConfig."""
    scene_model = SceneConfig(**scene_json)
    return scene_model


def json_file_to_model(path_to_json:str) -> SceneConfig:
    """Converts JSON object into a SceneConfig."""
    with open(path_to_json, 'r') as f:
        scene_json = json.load(f)
        scene_model = SceneConfig(**scene_json)
    return scene_model


def model_to_json_file(scene_model:SceneConfig, path_to_json:str):
    """Converts a SceneConfig to a dict and stores on disk."""
    scene_args = scene_model.model_dump()
    with open(path_to_json, 'w') as f:
        json.dump(scene_args, f)
