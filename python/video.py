import os
import json
import random
import glob
import cv2

def flip_movies(loaddir:str, savedir:str) -> None:
    """
    Flips movies from a directory randomly.

    Args:
        loaddir: Directory with videos to flip
        savedir: Directory to save flipped videos to.
    """
    from moviepy.editor import VideoFileClip, vfx
    mp4_files = [
        pos_mp4
        for pos_mp4
        in os.listdir(loaddir)
        if pos_mp4.endswith('.mp4')]
    idx = list(range(len(mp4_files)))
    mp4_samples = random.sample(idx, int(len(idx)/2))
    for idx in mp4_samples:
        file = mp4_files[idx]
        clip = VideoFileClip(loaddir+file)
        reversed_clip = clip.fx(vfx.mirror_x)
        reversed_clip.write_videofile(savedir+file)  
        reversed_clip.close()

def make_video(fname:str, loaddir:str, savedir:str, alpha:bool=False) -> None:
    """
    Make a video from a JSON config for a scene.

        fname: File name 
        loaddir: Directory containing scene JSONs
        savedir: Directory to save videos to
    """
    # Generate positive stimuli
    with open(loaddir+fname, 'r') as f:
        scene_args = json.loads(f.read())
    for i in range(3):
        # Load the new scene
        # scene = load_scene_from_args(scene_args)
        # Run the scene
        scene.instantiate_scene()
        if alpha:
            scene.graphics.draw_params['ball_alpha'] = True
        scene.run(
            view=True,
            fname=fname.split(".")[0]+f"_{i}",
            ecord=True,
            dir=savedir)
        vid_from_img(fname.split(".")[0]+f"_{i}",savedir)


def make_video_from_args(
        fname:str,
        args,
        savedir:str,
        alpha:bool=False) -> None:
    # Load the new scene
    # scene = load_scene_from_args(args)
    # Run the scene
    scene.instantiate_scene()
    if alpha:
        scene.graphics.draw_params['ball_alpha'] = True
    scene.run(view=True,fname=fname.split(".")[0],record=True,dir=savedir)
    vid_from_img(fname,savedir)


def vid_from_img(
        scene_name:str,
        savedir:str,
        filetype:str="*.jpg") -> None:
    """
    Takes images generated from make_video and stitches them into a video
    [DEPRECATED]

        scene_name: Name of the simulation for file naming
        filetype: Glob parameter
        dir: Location to save video to
    """
    print(f"Passed movie directory: {savedir}")
    print(f"Passed movie Scene Name: {scene_name}")
    img_dic = {}
    img_str = []
    size = 0,0
    for filename in glob.glob(savedir+filetype):
        img = cv2.imread(filename)
        size = (img.shape[1],img.shape[0])
        img_str.append(filename)
        img_dic[filename] = img
    out = cv2.VideoWriter(
        savedir + scene_name + '.mp4',
        cv2.VideoWriter_fourcc(*'avc1'),
        60,
        size)
    img_str.sort()
    for i in img_str:
        out.write(img_dic[i])
    out.release()
    os.system("rm "+ savedir +"*.jpg")
