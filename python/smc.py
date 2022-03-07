import arviz as az
import matplotlib.pyplot as plt
import numpy as np
import pymc3 as pm
from models import abstraction_simulation_pp as sim
import pandas as pd
import os
import json

def main():
    # Extract args
    data = pd.read_json("../experiments/experiment3/data/cleaned_data.json")
    data['rt_norm'] = (data.rt-data.rt.mean())/data.rt.std()
    RT_y_mean = data.groupby('scene').rt.apply(np.mean)
    data = RT_y_mean

    # Collect scene parameter files for simulator
    scenedir = "../data/json/pilot3/"
    scene_files = [s_json for s_json in os.listdir(scenedir) if s_json.endswith('.json')]
    scene_args = {}
    for file in scene_files:
        with open(scenedir+file, 'r') as f:
            sargs = (json.loads(f.read()))
            scene_args[sargs['name'].split(".")[0]] = sargs
    RT_x = RT_y_mean.index.to_list()

    def my_model(N,D,E):
        '''
        '''
        # Model predictions
        y_pred = []
        # Get model predictins for each scene
        print(f"Candidate Parameters: N,D,E={int(N),float(D),float(E)}")
        assert int(N) > 0, "N is < 0. Something is wrong."
        for x_ in RT_x:
            # print(f"Candidate Params: {int(N),float(D),float(E)}")
            # print(f"Types: {type(int(N)),type(float(D)),type(float(E))}")
            y_pred.append(
                sim(scene_args[x_], int(N),float(D),float(E))[-1][0])
        # Convert to array
        y_pred = np.array(y_pred)
        print(f"Done running model, returning predicions: {y_pred}")
        y_pred = (y_pred-y_pred.mean())/y_pred.std()
        return y_pred

    with pm.Model() as example:
        # Priors on model parameters
        # Number of samples to take from simulator
        N = pm.TruncatedNormal("N",sigma=1,lower=5,upper=100)
        # Length of path projection
        D = pm.TruncatedNormal("D",sigma=1, lower=100)
        # Cosine similarity threshold
        E = pm.TruncatedNormal("E",sigma=0.01,lower=0.0,upper=1)
        # Simulator likelihood
        s = pm.Simulator("s", my_model, 
                            params=(N,D,E), 
                            distance="gaussian",
                            sum_stat="sort",
                            epsilon=1.4, 
                            observed=data)

        pm.sample_smc(2000,kernel="ABC",cores=1,chains=1)

if __name__ == "__main__":
    main()