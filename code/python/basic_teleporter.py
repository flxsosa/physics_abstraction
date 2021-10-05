from main import *
from handlers import teleporter

# Collision handlers
ch = space.add_collision_handler(0,1)
ch.data["surface"] = screen
ch.post_solve = teleporter

# Scene
Box()
Teleporter((100,300))
Goal((700,800))
# These need to be added in this order
Teleporter((700,600))
Ball((100,100))

while running:
    for event in pygame.event.get():
        if event.type == KEYDOWN and (event.key in [K_q, K_ESCAPE]):
            running = False
        elif event.type == KEYDOWN and (event.key in [K_SPACE]):
            step = True

    screen.fill(THECOLORS["gray"])
    space.debug_draw(draw_options)

    dt = 1./fps
    if step:
        space.step(dt)
    pygame.display.flip()
    clock.tick(fps)