import json_utilities
import model_utilities
import os
import pandas as pd 

def main():
    scenedir = os.path.expanduser(
        '~/projects/physics_abstraction/data/json/experiment2')
    scene_json_files = [
        pos_json
        for pos_json
        in os.listdir(scenedir)
        if pos_json.endswith('.json')]
    blended_model_parameters = {
        'view': True,
        'noise': 0.00,
        'N': 1,
        'D': 340,
        'E': 0.0,
    }
    positions = []
    for scene_file in scene_json_files:
        df = pd.DataFrame.from_dict({})
        for _ in range(10):
            path_to_scene_file = os.path.join(scenedir, scene_file)
            scene_model = json_utilities.json_file_to_model(path_to_scene_file)
            blended_model = model_utilities.BlendedModel(
                blended_model_parameters
            )
            blended_model_sample = blended_model.sample_with_pos(
                scene_config=scene_model)
            position = blended_model_sample.model_dump()['ball_position']
            positions.append(position)
            sample_df = pd.DataFrame.from_dict(
                {'position': [
                    pd.DataFrame.from_dict(
                        blended_model_sample.model_dump()['ball_position'])]})
            df = pd.concat([df,sample_df])
        print(df.describe())
        print(positions)
        print(set(x for x in positions))

if __name__ == '__main__':
    main()
