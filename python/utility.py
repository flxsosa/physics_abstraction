"""Utilities for the physics abstraction project."""
import json_utilities
from typing import Any
import pandas as pd
import objects as pobjects


def make_video(screen,scene_name,dir):
    """
    Generates screenshots from a simulation

    Args:
        scene_name: Name of the scene
        screen: Pygame screen on which the simulation is rendered
        dir: Directory to which to save video
    """
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


def anonymize_data(datadir:str):
    """Anonymize subject_id's in a dataframe.
    
    Args:
        datadir: A string path to the empirical data.
    """
    raise NotImplementedError


def get_objects_from_scene_config(
        scene_args_config:json_utilities.SceneConfig
        ) -> dict[str, list[Any]]:
    """
    Instantiates objects from a scene config.

    Args:
        scene_args_config: Config for a scene.
    """
    # TODO(fasosa): Make this better.
    obj_map = {
        "Ball":pobjects.Ball,
        "Container":pobjects.Container,
        "Goal":pobjects.Goal,
        "BottomBorder":pobjects.BottomBorder,
        "Line":pobjects.Line
    }
    objects = []
    object_args = []
    scene_arg_dict = scene_args_config.model_dump()
    num_objs = {
        'Container':0,
        'Line':0
    }
    for obj in set(scene_arg_dict['objects']):
        if obj == "Ball":
            objects.append(obj_map[obj])
            object_args.append(
                json_utilities.BallConfig.parse_obj(
                    scene_arg_dict["ball_args"][0]
                    )
                )
        elif obj == "Goal":
            objects.append(obj_map[obj])
            object_args.append(
                json_utilities.BallConfig.parse_obj(
                    scene_arg_dict["goal_args"][0]
                    )
                )
        elif obj == "Container":
            for i in range(len(scene_arg_dict["container_args"])):
                # FIXME
                objects.append(obj_map[obj])
                args = scene_arg_dict["container_args"][i]
                parse = json_utilities.ContainerConfig.parse_obj(args)
                parse.id = num_objs["Container"]
                num_objs["Container"] += 1
                object_args.append(
                    parse
                )
        elif obj == "Line":
            objects.append(obj_map[obj])
            object_args.append(
                json_utilities.LineConfig.parse_obj(
                    scene_arg_dict["line_args"][0]
                )
            )
        elif obj == "PlinkoBorder":
            objects.append(pobjects.LeftBorder)
            object_args.append(scene_arg_dict["plinko_border_args"])
            objects.append(pobjects.RightBorder)
            object_args.append(scene_arg_dict["plinko_border_args"])
        elif obj == "BottomBorder":
            objects.append(obj_map[obj])
            if "bottom_border_args" in scene_arg_dict:
                object_args.append(scene_arg_dict["bottom_border_args"])
            else:
                object_args.append(obj_map[obj]())
        else:
            raise ValueError(
                f"Received an invalid value in load_objects: obj=={obj}")
    return {'object_constructors': objects, 'arguments': object_args}
