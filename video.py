import logging 
from moviepy.editor import *
import random 
from pathlib import Path
import speech


comment_limit = 3

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

def print_post_details(post):
    logging.info("SubReddit : " + post.subreddit_name_prefixed)
    logging.info("Title     : " + post.title)
    logging.info("Score     : " + str(post.score))
    logging.info("ID        : " + str(post.id))
    logging.info("URL       : " + post.url)

def print_comment_details(comment):
    logging.info("Author   : " + str(comment.author))
    logging.info("id       : " + str(comment.id))
    logging.info("Stickied : " + str(comment.stickied))
    

class Scene():
    def __init__(self, text, audio, starttime, duration, textclip):
        self.text = text
        self.audio = audio
        self.starttime = starttime
        self.duration = duration
        self.textclip = textclip

class Video():
    def __init__(self, scenes=[], meta=None, background=None, script="", duration=0):
        self.scenes = scenes
        self.meta = meta
        self.background = background
        self.script = script
        self.duration = duration

    def get_background(self):
        self.background = random.choice(os.listdir("backgrounds"))
        logging.info('Randomly Selecting Background : ' + self.background)
    
    def compile(self):
        pass


def create(post):
    logging.info('========== Processing Reddit Post ==========')
    print_post_details(post)
    v = Video()
    v.meta = post

    v.get_background()



    height = 720
    width = 1280
    clip_margin = 50 
    clip_margin_top = 40
    fontsize = 32
    txt_clip_size = (width - (clip_margin * 2), None)

    background_filepath = str(Path("backgrounds", v.background))

    current_clip_text =""
    t = 0
    clip_duration = 3
    #for c in v.meta.comments:
    for count, c in enumerate(v.meta.comments):
        logging.info(f'========== Processing Reddit Comment {count}/{comment_limit} ==========')
        print_comment_details(c)
        logging.info("Comment #  : " + str(count))

        comment = c.body 
        comment = os.linesep.join([s for s in comment.splitlines() if s])

        logging.info("Body       : " + comment)
        logging.info("Comment Length  : " + str(len(comment)))

        if c.stickied:
            logging.info("Skipping Stickied Comment...")
            continue

        audio_filepath = str(Path("audio", v.meta.id + "_" + c.id + ".mp3"))
        speech.create_audio(audio_filepath, comment)
        audioclip = AudioFileClip(audio_filepath)

        txt_clip = TextClip(comment, 
                            font="Verdana",
                            fontsize = fontsize, 
                            color = 'white',
                            size = txt_clip_size,
                            kerning=-1,
                            method='caption',
                            #bg_color='blue',
                            align='West')\
                            .set_pos((clip_margin,clip_margin_top))\
                            .set_duration(audioclip.duration)\
                            .set_audio(audioclip)

        background_clip = VideoFileClip(background_filepath)\
                            .set_duration(audioclip.duration)\
                            .set_opacity(0.1)\
                            .volumex(0.1)

        scene = Scene(comment, audio_filepath, t, audioclip.duration, txt_clip)
        v.scenes.append(scene)
    
        post_video = CompositeVideoClip([background_clip, txt_clip])
        video_filename = str(Path("tmp", v.meta.id + "_" + c.id + ".mp4"))
        post_video.write_videofile(video_filename)


        if count == comment_limit:
            logging.info("Reached Maximum Number of Comments Limit : " + str(comment_limit))
            logging.info("Exiting...")
            break
    