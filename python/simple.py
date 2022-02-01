from simulation import *
from abstraction import *
from objects import *
from utility import sample_object_arguments
from numpy.random import normal

pallete = {'b':Ball,'c':Line,'g':Goal}
physics = Physics()
graphics = Graphics()
objects = [
    Ball((700,100)),
    Line((700,100),(100,400)),
    Line((200,700),(800,550)),
    Line((100,800),(500,800)),
    PlinkoBorder(),
    BottomBorder()
    ]
# ball_args,goal_args,container_args = sample_object_arguments(1)
# # # Perturb those arguments N times
# for i in range(1):
#     noisy_ball_args = list(*ball_args*normal(1,0.02,2))
#     objects = [Ball(noisy_ball_args), Goal(*goal_args), PlinkoBorder(), BottomBorder()]
#     for j in range(len(container_args[0])):
#         objects.append(Container(*container_args[0][j]))

scene = SceneBuilder(physics,objects,graphics,pallete)
scene.instantiate_scene()
scene.graphics.initialize_graphics()

scene.run_path(view=True)
