from simulation import *
from objects import *

physics = Physics()
graphics = Graphics(800,1000)
objects = [PlinkoBorder(), BottomBorder()]
ball_args = [(400,650)]
objects = [PlinkoBorder(), BottomBorder()]

scene = SceneBuilder(physics,objects,graphics,{'c':Line,'b':Ball,'g':Goal})
scene.instantiate_scene()
scene.run()
