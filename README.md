# Blending simulation and abstraction for intuitive physics
**Authors**: Felix A. Sosa, Sam J. Gershman, Tomer D. Ullman

### Abstract
How are people able to understand everyday physical events with such ease? One hypothesis is that people use an approximate probabilistic simulation of the world. A contrasting hypothesis is that people use a collection of abstractions or features. The two hypotheses explain complementary aspects of physical reasoning. We develop a ``blended model'' that synthesizes the two hypotheses: under certain conditions, simulation is replaced by a visuo-spatial abstraction (linear path projection). This abstraction purchases efficiency at the cost of fidelity. As a consequence, the blended model predicts that people will make systematic errors whenever the conditions for applying the abstraction are met. We tested this prediction in two experiments where participants made judgments about whether a falling ball will contact a target. First,  we show that response times are longer when straight-line paths are unavailable, even when simulation time is held fixed, arguing against a pure-simulation model (Experiment 1). Second, we show that people incorrectly judge the trajectory of the ball in a manner consistent with linear path projection (Experiment 2). We conclude that people have access to a flexible mental physics engine, but adaptively invoke more efficient abstractions when they are useful.

# Repo Structure

<PUT TREE HERE>

## python
All python modules used for this project.

- ```abstraction.py``` contains the major utilities for the path projection abstraction.
- ```combine_csv.py``` contains the utility used to zip all CSV files containing participant data into one usable for analyses.
- ```graphics.py``` contains the graphics engine utilities.
- ```handlers.py``` contains collision handler utilities.
- ```json_utilities.py``` contains all JSON config file utilities.
- ```model_utilities.py``` contains all model utilities.
- ```mp.py``` contains the model fitting utilities.
- ```objects.py``` contains the scene object classes used for modeling objects in scenes.
- ```physics.py``` contains the physics engine.
- ```scene.py``` contains the scene utilities.
- ```stimuli_generation.py``` contains examples of stimuli generation methods used to generate stimuli for Experiment 1 and Experiment 2.
- ```submit_grid_job.py``` contains a method for submitting grid search jobs on SLURM.
- ```utiltiy.py``` containts misc utilities.
- ```video.py``` contains examples of methods for converting scenes into usable video stimuli.

## paper
All figures used in the paper (.pdfs).

## data
All data collected and generated for the project.
- ```stimuli``` contains the stimuli shown in the main trials for Experiment 1 and Experiment 2.
- ```empirical``` contains the raw anonymized data from Experiment 1 and Experiment 2, the cleaned data used to generate the figures, and the anonymized demographics data for each experiment.
- ```json``` contains the JSON files the define the scenes used to create the stimuli.
- ```model_fits``` contains a subset of the model fits performed during model fitting.

## experiments
All jspsych code used to create and run Experiments 1 and 2.

## notebooks
Jupyter notebooks for data analyses used in the paper.

- ```data_cleaning``` details the methods by which data was cleaned for analysis.
- ```experiment1_analysis``` details the analyses reported in Experiment 1.
- ```experiment2_analysis``` details the analyses reported in Experiment 2.
