import argparse
import pandas as pd
import numpy as np
import os
import json
import csv
from statsmodels.formula.api import ols
from models import abstraction

def main():
    parser = argparse.ArgumentParser(
        description="Automatically submit jobs using a json file")
    parser.add_argument('datadir', 
        help="read-directory where participant data is")
    parser.add_argument('scenedir',
        help='read-directory where scene simulation parameter files are')
    parser.add_argument('savedir',
        help='write-directory where model parameter files saved to')
    parser.add_argument('nrange1',type=int,
        help='the range of values for N')
    parser.add_argument('nrange2',type=int,
        help='the range of values for N')
    parser.add_argument('drange1',type=int,
        help="the range of values for D")
    parser.add_argument('drange2',type=int,
        help='the range of values for D')
    args = parser.parse_args()

    # Parameter spaces
    N = range(args.nrange1,args.nrange2)
    D = range(args.drange1,args.drange2)
    E = np.arange(0.5,1.0,0.01)

    # Import empirical data
    data = pd.read_json(args.datadir)

    # Import scene configuration files
    scene_files = [scene_json for scene_json in os.listdir(args.scenedir) if scene_json.endswith('.json')]
    scene_args = {}
    for file in scene_files:
        with open(args.scenedir+file, 'r') as f:
            sargs = (json.loads(f.read()))
            scene_args[file.split(".")[0]] = sargs

    # Observed RT
    data_emp = data.groupby('scene').part_zrt.apply(np.mean).to_frame()
    scenes = data_emp.index.to_list()

    # Regression parameters
    formula = 'part_zrt ~ sim_time_z'

    def my_model(N,D,E,scene_args=scene_args):
        '''
        Returns model predictions for a given Scene with parameters
        N, D, and E.

        :param N: Number of simulation ticks
        :param D: Path projection distance
        :param E: Similarity threshold
        '''
        # Model dataframe
        model_df = pd.DataFrame({})

        # Get model predictins for each scene
        for scene in scenes:
            # Sample model 100 times on scene
            model_result = abstraction(scene_args[scene],N=int(N),D=D,E=E,num_samples=1)
            model_row = pd.DataFrame({
                "scene": scene,
                "collision_prob": np.mean(model_result['collision_probability']),
                "sim_time": model_result['simulation_time'],
                "type": "abstraction_model"
            })
            model_df = pd.concat([model_df,model_row])
            
        return model_df

    with open(f"{args.savedir}grid_fit_n_{n_i}_d_{d_i}.csv","w") as out:
        csv_out=csv.writer(out)
        # Dictionary of parameters and respective model fit resutls
        csv_out.writerow(['N','D','E','MSE Residual', 'MSE Model', 'MSE Total'])

        # Grid search
        for n_i in N:
            for d_i in D:
                for e_i in E:
                    # Grab model predictions
                    model_predictions = pd.DataFrame({})
                    model_predictions = my_model(n_i,d_i,e_i)
                    # Normalize predicted model runtime
                    model_predictions['sim_time_z'] = model_predictions.sim_time.transform(lambda x: (x-x.mean())/x.std())
                    # Subset model prediction dataframe to only include RT predictions per scene
                    data_model = model_predictions.groupby('scene').sim_time_z.apply(np.mean).to_frame()
                    # Merge model and empirical data
                    df = pd.merge(data_model, data_emp, left_index = True, right_index = True)
                    # Fit linear model
                    model_fit = ols(formula, df).fit()
                    # Grab MSE
                    mse_res = model_fit.mse_resid
                    mse_mod = model_fit.mse_model
                    mse_tot = model_fit.mse_total
                    # Append MSE results to list
                    csv_out.writerow((n_i,d_i,e_i,mse_res,mse_mod,mse_tot))
        
if __name__ == "__main__":
    main()
