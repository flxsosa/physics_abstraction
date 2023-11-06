"""Entrypoint and utilities for grid search parameter fitting."""

import argparse
import csv
import multiprocessing
import numpy as np
import os
import pandas as pd
import secrets
import model_utilities
import json_utilities

from typing import Any
from statsmodels.formula.api import ols


def _run_model_on_all_inputs(
        model:model_utilities.PhysModel,
        scene_paths:list[str],
        num_samples:int=50) -> pd.DataFrame:
    """Runs the model on all the input SceneConfigs."""
    model_df = pd.DataFrame({})
    for path_to_scene in scene_paths:
        for _ in range(num_samples):
            scene_config = json_utilities.json_file_to_model(path_to_scene)
            model_output = model.sample(scene_config)
            model_output = model_output.model_dump()
            model_output['scene'] = scene_config.name
            model_output['model'] = 'blended'
            model_output_df = pd.DataFrame(model_output, index=[0])
            model_df = pd.concat([model_df, model_output_df])
    return model_df.reset_index(drop=True)


def _format_model_outputs(model_outputs:pd.DataFrame) -> pd.DataFrame:
    model_outputs['sim_time_z'] = model_outputs.simulation_ticks.transform(
        lambda x: (x-x.mean())/x.std()
    )
    model_rt_predictions = model_outputs.groupby(
        'scene'
    ).sim_time_z.apply(np.mean).to_frame()
    return model_rt_predictions


def grade_model_parameters(
        savedir:str,
        scene_files:list[Any],
        empirical_rt_data:Any,
        param_range_n:list[int],
        param_range_d:list[int],
) -> None:
    param_range_n = range(param_range_n[0], param_range_n[1]+1)
    param_range_d = range(param_range_d[0], param_range_d[1]+1)
    param_range_e = np.arange(0.9,1.0, 0.1)
    param_range_noise = np.arange(0.9,1.0, 0.1)
    # Regression formula
    formula = 'participant_z_rt ~ sim_time_z'
    job_id = secrets.token_urlsafe(4)
    # Enuemrate parameter space
    with open( # pylint: disable=unspecified-encoding
        f'{savedir}/model_fitting_{job_id}.csv',
        'a'
    ) as output_file:
        csv_writer = csv.writer(output_file)
        csv_writer.writerow(['N', 'D', 'E', 'Noise', 'mse'])
        num_params = len(param_range_n) * len(param_range_d)
        num_params *= len(param_range_e)
        num_params *= len(param_range_noise)
        count = 1
        for param_n_i in param_range_n:
            for param_d_i in param_range_d:
                for param_e_i in param_range_e:
                    # Round floating point
                    param_e_i = round(param_e_i, 2)
                    for param_noise_i in param_range_noise:
                        # Round floating point
                        param_noise_i = round(param_noise_i, 2)
                        print(
                            f'Job {job_id} '
                            f'running param setting: {count} '
                            f'of {num_params}'
                            )
                        count += 1
                        # Instantiate model with current parameter
                        #   selection.
                        blended_model_parameters = {
                            'view': False,
                            'noise': param_noise_i,
                            'N': param_n_i,
                            'D': param_d_i,
                            'E': param_e_i,
                        }
                        blended_model = model_utilities.BlendedModel(
                            blended_model_parameters)
                        model_outputs = _run_model_on_all_inputs(
                            blended_model,
                            scene_files)
                        model_rt_predictions = _format_model_outputs(
                            model_outputs)
                        full_rt_data = pd.merge(
                            model_rt_predictions,
                            empirical_rt_data,
                            left_index=True,
                            right_index=True)
                        model_fit = ols(formula, full_rt_data).fit()
                        mse_residual = model_fit.mse_model
                        csv_writer.writerow(
                            (
                                param_n_i,
                                param_d_i,
                                param_e_i,
                                param_noise_i,
                                mse_residual
                            )
                        )
    print(f'Job {job_id} done...')

def main():
    """Entrypoint for grid search parameter fitting."""
    parser = argparse.ArgumentParser(
        description="Automatically submit jobs using a json file")
    parser.add_argument(
        'datadir',
        help="read-directory where participant data is")
    parser.add_argument(
        'scenedir',
        help='read-directory where scene simulation parameter files are')
    parser.add_argument(
        'savedir',
        help='write-directory where model parameter files saved to')
    parser.add_argument(
        'n_range_start',
        type=int,
        help='the range of values for N')
    parser.add_argument(
        'n_range_stop',
        type=int,
        help='the range of values for N')
    parser.add_argument(
        'd_range_start',
        type=int,
        help="the range of values for D")
    parser.add_argument(
        'd_range_stop',
        type=int,
        help='the range of values for D')
    args = parser.parse_args()
    # Number of CPUs TODO: Make this arbitrary
    num_cores = 5
    # Parameter spaces
    partitions_n = np.array_split(
        range(args.n_range_start, args.n_range_stop+1),
        num_cores)
    partitions_d = np.array_split(
        range(args.d_range_start, args.d_range_stop+1),
        num_cores)
    parameter_partitions = {'N': partitions_n, 'D': partitions_d}
    # Read empirical data
    empirical_rt_data = pd.read_json(args.datadir)
    empirical_rt_data = empirical_rt_data.groupby(
        'scene').participant_z_rt.apply(np.mean).to_frame()
    # Import scene configuration files
    scene_files = [
        args.scenedir+x
        for x
        in os.listdir(args.scenedir)
        if x.endswith('.json')
        ]
    procs = []
    print("Starting processes...")
    for i in range(num_cores):
        proc = multiprocessing.Process(
            target=grade_model_parameters,
            args=[
                args.savedir,
                scene_files,
                empirical_rt_data,
                [
                    parameter_partitions['N'][i][0],
                    parameter_partitions['N'][i][-1]
                ],
                [
                    parameter_partitions['D'][i][0],
                    parameter_partitions['D'][i][-1]
                ]
            ]
        )
        procs.append(proc)
        proc.start()
    print("Stopping...")
    for proc in procs:
        proc.join()


if __name__ == '__main__':
    main()
