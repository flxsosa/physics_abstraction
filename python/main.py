'''
File for scratch jobs and testing. Frequently overwritten.
'''
from cgi import test
import utility
import models
import pandas as pd
import os
from pymunk.vec2d import Vec2d
from video import make_video

def get_scene_name(file_name):
    '''
    Returns scene name from file name
    '''
    return file_name.split(".")[0]

def get_scene_type(scene_name):
    '''
    Returns the scene type for a given scene name.
    '''
    split_name = scene_name.split('_')[:2]
    return '_'.join(split_name)

def main():
    scene_dir = '/Users/lollipop/projects/physics_abstraction/data/json/test/'
    make_video("test.json", loaddir=scene_dir, savedir=scene_dir,alpha=False,region_test=False)
    # scene = utility.load_scene(scene_dir)
    # scene.instantiate_scene()
    # for o in scene.objects:
    #     print(o,id(o),o.id)
    # scene.run(view=True)
    # scene.run_path(view=True,N=5.1409462387944895,D=104.10421721109057,E=0.9010950888058105)

def test_abstraction():
    loaddir = "../data/json/pilot7/"
    # Gather all of the json files in the directory of trial stimuli
    json_files = [pos_json for pos_json in os.listdir(loaddir) if pos_json.endswith('.json')]
    # Dictionary that will contain distance travelled per scenario 
    distances = []

    # Iterate through stimuli files
    for scene_json in json_files:
        scene_dir = loaddir+scene_json
        scene_name = get_scene_name(scene_json)
        scene = utility.load_scene(scene_dir)
        # Extract the origin (the ball's starting position)
        origin = scene.args['ball_args'][0]
        # Extract the goal position
        goal = scene.args['goal_args'][0]
        # Convert these points into Vec2d for compatibility with pymunk
        origin = Vec2d(*origin)
        goal = Vec2d(*goal)
        dist = {}
        # Compute the distance
        dist['distance'] = origin.get_distance(goal)
        # Add the scene, distance pair into the dataframe
        dist['scene'] = scene_name
        distances.append(dist)

    distances = pd.DataFrame.from_dict(distances)

    abstraction_rt = []
    for scene_json in json_files:
        scene_dir = loaddir+scene_json
        scene_name = get_scene_name(scene_json)
        if 'negative' in scene_name:
            collision = False
        else:
            collision = True
        scene_type = get_scene_type(scene_name)
        # Samples to draw from models
        samples = 1
        # Noise (SD on ball starting pos) for simulation model
        noise = 0.02
        # Generate a scene
        scene = utility.load_scene(scene_dir)
        # Get RT profile from model
        ## Abstraction
        abstraction_sample = models.abstraction(scene_args=scene.args,num_samples=samples)
        abstraction_sample['scene'] = scene_name
        abstraction_sample['scene_type'] = scene_type
        abstraction_sample['collision'] = collision
        abstraction_rt.append(abstraction_sample)

    abstraction_predictions = pd.DataFrame.from_dict(abstraction_rt,orient='columns')
    abstraction_predictions['model'] = 'abstraction'

    print(abstraction_predictions)

if __name__ == "__main__":
    main()