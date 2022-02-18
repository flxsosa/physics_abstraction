import argparse
import pandas as pd
import numpy as np
import os
import sys
import json
import theano.tensor as tt
import arviz as az
from statsmodels.formula.api import ols
from models import abstraction_simulation_pp
import time
import ast

def main():
    parser = argparse.ArgumentParser(
        description="Automatically submit jobs using a json file")
    parser.add_argument('datadir', 
        help="read-directory where participant data is")
    parser.add_argument('scenedir',
        help='read-directory where scene simulation parameter files are')
    parser.add_argument('savedir',
        help='write-directory where model parameter files saved to')
    parser.add_argument('nrange',
        help='the range of values for N')
    parser.add_argument('drange',
        help="the range of values for D")
    args = parser.parse_args()

    # Parameter spaces
    N = ast.literal_eval(args.nrange)
    D = ast.literal_eval(args.drange)
    E = np.arange(0.1,1.0,0.01)

    # Import empirical data
    data = pd.read_json(args.datadir)

    # Import scene configuration files
    scene_files = [scene_json for scene_json in os.listdir(args.scenedir) if scene_json.endswith('.json')]
    scene_args = {}
    for file in scene_files:
        with open(args.scenedir+file, 'r') as f:
            sargs = (json.loads(f.read()))
            scene_args[sargs['name'].split(".")[0]] = sargs

    # Observed RT
    rt_mean = data.groupby('scene').rt.apply(np.mean).to_frame()
    scenes = rt_mean.index.to_list()

    # Regression parameters
    formula = 'rt ~ y_pred'

    def my_model(N,D,E):
        '''
        :param theta: Expected theta == [N, D, E]
        :param x: Expected list of scene arguments
        '''
        # Model predictions
        y_pred = {
            'scene':[],
            'y_pred':[]
        }
        # Get model predictins for each scene
        for scene in scenes:
            y_pred['scene'].append(scene)
            y_pred['y_pred'].append(abstraction_simulation_pp(scene_args[scene],int(N),D,E)[-1][0])
        return pd.DataFrame(y_pred)

    def add_to_list(l, m):    
        '''
        Adds a linear model to a list of linear models according to rsquared value

        :param l: The list of linear models
        :param m: The candidate linear model
        '''
        if len(l) < max_pe:
            l.append(m)
        else:
            l.sort(key=lambda x: x.rsquared)
            for i in range(1,len(l)-1):
                if m.rsquared > l[i].rsquared:
                    l[0] = m
        return l

    # List for best parameters
    point_estimates = []
    max_pe = 1

    # Grid search
    for n_i in N:
        for d_i in D:
            for e_i in E:
                y_ = my_model(n_i,d_i,e_i)
                df = rt_mean.merge(y_, on="scene")
                model_fit = ols(formula, df).fit()
                point_estimates = add_to_list(point_estimates, model_fit)

    # Save the models
    for i in range(len(point_estimates)):
        point_estimates[i].save(f"{args.savedir}_{i}.pickle")

if __name__ == "__main__":
    main()