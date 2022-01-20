from utility import *
import os
import numpy as np
from test import *

# Original directory
dir = '../data/json/pilot3/'
# Destination directory
ddir = '../data/videos/pilot3_recovery/'
conditions = {
    'rt':'high',
    'sp':False,
    'bgc':False,
    'bins':{
        'high_no':0
    }
}

scene_json_to_video(dir,ddir)