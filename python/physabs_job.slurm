#!/bin/bash
#SBATCH -t=0-06:00
#SBATCH --mem=1000

DATADIR=$HOME/projects/physabs/git/physics_abstraction/experiments/experiment3/data/cleaned_data.json
SCENEDIR=$HOME/projects/physics_abstraction/data/json/pilot3/
SAVEDIR=$HOME/projects/physabs/.out/

echo $DATADIR $SCENEDIR $SAVEDIR${FNAME}

# Load conda module and activate env
# module load Anaconda3/2020.11
# conda activate physabs

# Run the analysis 
# python abc_fit.py $DATADIR $SCENEDIR $SAVEDIR${FNAME}