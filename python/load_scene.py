def load_scene(dir,region_test=False):
    '''
    Load a Scene from saved JSON arguments.

    :param dir: Path to scene.
    '''
    with open(dir, 'r') as f:
        scene_args = json.loads(f.read())
        screen_args = scene_args['screen_size']
    physics = Physics()
    graphics = Graphics(*screen_args)
    objects = load_objects(dir,region_test=region_test)

    scene = Scene(physics, objects, graphics, dir)
    scene.graphics.framework.display.set_caption(dir.split('/')[-1])
    return scene