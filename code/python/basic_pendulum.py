from main import *

# Scene
Box()
Goal((700,800))
# These need to be added in this order
Ball((100,100))

# Pendulum
ball_body = space.bodies[-1]
rotation_center_body = pymunk.Body(body_type=pymunk.Body.STATIC)  # 1
rotation_center_body.position = (400, 10)
rotation_center_joint = pymunk.PinJoint(
    ball_body, rotation_center_body, (0, 0), (0, 0)
)
space.add(rotation_center_joint)

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