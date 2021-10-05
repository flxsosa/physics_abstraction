from main import *

# Scene
Box()
Goal((100,800))
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