from main import *
from scene import Scene

objs_c = [Ball,Goal,Container]

objs_t = [Ball,Goal,Tube]

obj_params = [
    [
        [(400,100)],
        [(400,1000)],
        [(100,200)]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,200)]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(700,200)]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(100,500)]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,500)]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(700,500)]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(100,800)]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,800)]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(700,800)]
    ]
]

obj_params_w = [
    [
        [(400,100)],
        [(400,1000)],
        [(400,200),20]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,500),20]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,800),20]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,200),160]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,500),160]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,800),160]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,200),320]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,500),320]
    ],
    [
        [(400,100)],
        [(400,1000)],
        [(400,800),320]
    ]
]

i = 0
for op in obj_params:
    s = Scene(None, objs_c, op)
    s.forward(view=True,img_capture=True,fname="../../images/scene_container"+str(i))
    i += 1

i = 0
for op in obj_params:
    s = Scene(None, objs_t, op)
    s.forward(view=True,img_capture=True,fname="../../images/scene_tube"+str(i))
    i += 1

i = 0
for op in obj_params_w:
    s = Scene(None, objs_c, op)
    s.forward(view=True,img_capture=True,fname="../../images/scene_container_w"+str(i))
    i += 1

i = 0
for op in obj_params_w:
    s = Scene(None, objs_t, op)
    s.forward(view=True,img_capture=True,fname="../../images/scene_tube_w"+str(i))
    i += 1

s = Scene(None, [Ball,Goal,Tube],[[(400,100)],[(400,1000)],[(400,754),20]])
s.forward(view=True,img_capture=True,fname="../../images/scene_tube_w2")

s = Scene(None, [Ball,Goal],[[(400,100)],[(400,1000)]])
s.forward(view=True,img_capture=True,fname="../../images/scene_0")