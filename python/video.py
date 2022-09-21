import os
from utility import load_scene_from_args
import json
import random
import glob
import cv2

def flip_movies():
    from moviepy.editor import VideoFileClip, vfx
    dir = "/Users/lollipop/Desktop/tmp/"
    savedir = dir+'flipped/'
    mp4_files = [pos_mp4 for pos_mp4 in os.listdir(dir) if pos_mp4.endswith('.mp4')]
    # print(mp4_files)
    idx = list(range(len(mp4_files)))
    mp4_samples = random.sample(idx, int(len(idx)/2))
    for idx in mp4_samples:
        file = mp4_files[idx]
        clip = VideoFileClip(dir+file)
        reversed_clip = clip.fx(vfx.mirror_x)
        reversed_clip.write_videofile(dir+file)  

def make_video(fname,loaddir,savedir,alpha=False,region_test=False):
    # Generate positive stimuli
    with open(loaddir+fname, 'r') as f:
        scene_args = json.loads(f.read())
    # Load the new scene
    scene = load_scene_from_args(scene_args,region_test)
    # Run the scene
    scene.instantiate_scene()
    if alpha:
        scene.graphics.draw_params['ball_alpha'] = True
    scene.run(view=True,fname=fname.split(".")[0],record=True,dir=savedir)
    vid_from_img(fname,savedir)

def vid_from_img(scene_name,dir,filetype="*.jpg"):
    '''
    Takes images generated from make_video and stitches them into a video
    [DEPRECATED]
    :param scene_name: Name of the simulation for file naming
    :param filetype: Glob parameter
    :param dir: Location to save video to
    '''
    print(f"Passed movie directory: {dir}")
    print(f"Passed movie Scene Name: {scene_name}")
    img_dic = {}
    img_str = []
    size = 0,0
    for filename in glob.glob(dir+filetype):
        img = cv2.imread(filename)
        h,w,l =img.shape
        size = (img.shape[1],img.shape[0])
        img_str.append(filename)
        img_dic[filename] = img
    out = cv2.VideoWriter(dir+scene_name+'.mp4', cv2.VideoWriter_fourcc(*'avc1'),60,size)
    img_str.sort()
    for i in img_str:
        out.write(img_dic[i])
    out.release()
    os.system("rm "+ dir +"*.jpg")