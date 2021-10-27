import logging 
from moviepy.editor import *
import random 




comment_limit = 3

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def print_post(post):
    logging.info('Creating Video')
    logging.info("SubReddit : " + post.subreddit_name_prefixed)
    logging.info("Title     : " + post.title)
    logging.info("Score     : " + str(post.score))
    logging.info("ID        : " + str(post.id))
    logging.info("URL       : " + post.url)

class Scene():
    text = []

class Video():
    scenes = []
    meta = None
    background = ""

    def get_background(self):
        self.background = random.choice(os.listdir("backgrounds"))
        logging.info('Randomly Selecting Background : ' + self.background)

def create(post):

    v = Video()
    v.meta = post
    logging.info('Creating Video Object :')
    logging.info(v.meta.title)
    v.get_background()
    print(v.background)
    scene_title = Scene()
    scene_title.text = v.meta.title

    v.scenes.append(scene_title)
    i = 0
    for c in v.meta.comments:
        
        scene_comment = Scene()
        scene_comment.text = c.body
        v.scenes.append(scene_comment)
        i += 1
        if i == comment_limit:
            break



    return v

def compile(video):
    height = 720
    width = 1280
    clip_margin = 50 
    fontsize = 32
    txt_clip_size = (width - (clip_margin * 2), None)

    logging.info('========== Compiling Videos ==========')
    clip_list = []
    for scene in video.scenes:
        logging.info('Generating Clip :')
        logging.info(scene.text)
        txt_clip = TextClip(scene.text, 
                            font="Verdana",
                            fontsize = fontsize, 
                            color = 'white',
                            size = txt_clip_size,
                            kerning=-1,
                            method='caption',
                            #bg_color='blue',
                            align='West').set_pos((clip_margin,40)).set_duration(2)                            
                            #.resize(0.33)
                            
                            
                 
        clip_list.append(txt_clip)
    logging.info('Merging Text Clips')
    text_clip = concatenate(clip_list, method = "compose")
    text_clip.write_videofile(video.meta.id + ".mp4", fps = 24, codec = 'mpeg4')
    background_clip = VideoFileClip("backgrounds\\" + video.background)\
                                                      .set_duration(text_clip.duration)\
                                                      .set_opacity(0.1)

    logging.info('Merging Background and Text Clip')

    post_video = CompositeVideoClip([background_clip, text_clip])
    video_filename = "output\\" + video.meta.id + ".mp4"
    post_video.write_videofile(video_filename)




    