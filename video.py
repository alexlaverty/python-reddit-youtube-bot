from moviepy.editor import *
from pathlib import Path
import logging 
import random 
import re
import speech
import json 


max_video_length = 600 # Seconds
comment_limit = 600

pause = 1 # Pause after speech

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])

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
    logging.info("Body     : " + str(comment.body))
    
def safe_filename(text):
    text = text.replace(" ","_")
    return "".join([c for c in text if re.match(r'\w', c)])[:50]

class Scene():
    def __init__(self, text, audio, starttime, duration, textclip):
        self.text = text
        self.audio = audio
        self.starttime = starttime
        self.duration = duration
        self.textclip = textclip

class Video():
    def __init__(self, clips=[], meta=None, background=None, script="", duration=0):
        self.clips = clips
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
    v.clips = []
    v.get_background()

    height = 720
    width = 1280
    clip_margin = 50 
    clip_margin_top = 30
    fontsize = 32
    txt_clip_size = (width - (clip_margin * 2), None)

    background_filepath = str(Path("backgrounds", v.background))

    current_clip_text =""
    t = 0

    audio_title = str(Path("audio", v.meta.id + "_title.mp3"))

    speech.create_audio(audio_title, v.meta.title)

    audioclip_title = AudioFileClip(audio_title)

    subreddit_clip = TextClip(v.meta.subreddit_name_prefixed, 
                            font="Verdana",
                            fontsize = 42, 
                            color = 'white',
                            size = txt_clip_size,
                            kerning=-1,
                            method='caption',
                            #bg_color='blue',
                            align='West')\
                            .set_pos((40,40))\
                            .set_duration(audioclip_title.duration + pause)\
                            .set_start(t)   

    v.clips.append(subreddit_clip)

    title_clip = TextClip(v.meta.title, 
                            font="Verdana",
                            fontsize = 40, 
                            color = 'white',
                            size = txt_clip_size,
                            kerning=-1,
                            method='caption',
                            #bg_color='blue',
                            align='Center')\
                            .set_pos(("center","center"))\
                            .set_duration(audioclip_title.duration + pause)\
                            .set_audio(audioclip_title)\
                            .set_start(t)\
                            .volumex(1.5)
    v.clips.append(title_clip)

    t += audioclip_title.duration + pause
    v.duration += audioclip_title.duration + pause

    for count, c in enumerate(v.meta.comments):
        logging.info(f'========== Processing Reddit Comment {count}/{comment_limit} ==========')
        print_comment_details(c)
        logging.info("Comment #  : " + str(count))

        comment = c.body 
        comment = os.linesep.join([s for s in comment.splitlines() if s])

        logging.info("Comment Length  : " + str(len(comment)))

        if c.stickied:
            logging.info("Skipping Stickied Comment...")
            continue

        comment_lines = comment.splitlines()

        for comment_line_count, comment_line in enumerate(comment_lines):
            logging.info("comment_line     : " + comment_line)
            audio_filepath = str(Path("audio", v.meta.id + "_" + c.id + "_" + str(comment_line_count) + ".mp3"))
            speech.create_audio(audio_filepath, comment_line)
            audioclip = AudioFileClip(audio_filepath)

            current_clip_text += comment_line + "\n\n"
            logging.info("Current Clip Text :")
            logging.info(current_clip_text)

            txt_clip = TextClip(current_clip_text, 
                                font="Verdana",
                                fontsize = fontsize, 
                                color = 'white',
                                size = txt_clip_size,
                                kerning=-1,
                                method='caption',
                                #bg_color='blue',
                                align='West')\
                                .set_pos((clip_margin,clip_margin_top))\
                                .set_duration(audioclip.duration + pause)\
                                .set_audio(audioclip)\
                                .set_start(t)\
                                .volumex(1.5)
                                

            if txt_clip.h > height:
                logging.info("Text exceeded Video Height, reset text")
                current_clip_text = comment_line + "\n\n"
                txt_clip = TextClip(current_clip_text, 
                        font="Verdana",
                        fontsize = fontsize, 
                        color = 'white',
                        size = txt_clip_size,
                        kerning=-1,
                        method='caption',
                        #bg_color='blue',
                        align='West')\
                        .set_pos((clip_margin,clip_margin_top))\
                        .set_duration(audioclip.duration + pause)\
                        .set_audio(audioclip)\
                        .set_start(t)

                if txt_clip.h > height:
                    logging.info("Comment Text Too Long, Skipping Comment")
                    continue   

            t += audioclip.duration + pause
            v.duration += audioclip.duration + pause
            

            v.clips.append(txt_clip)
            logging.info("Video Clips : ")
            logging.info(str(len(v.clips)))

        logging.info("Current Video Duration : " + str(v.duration))

        if v.duration > max_video_length:
            logging.info("Reached Maximum Video Length : " + str(max_video_length))
            logging.info("Exiting...")     
            break 

        if count == comment_limit:
            logging.info("Reached Maximum Number of Comments Limit : " + str(comment_limit))
            logging.info("Exiting...")
            break
        
        
    
    background_clip = VideoFileClip(background_filepath)\
                        .set_opacity(0.2)\
                        .volumex(0)

    logging.info("Video Clip Duration      : " + str(v.duration))
    logging.info("Background Clip Duration : " + str(background_clip.duration))

    if background_clip.duration < v.duration:
        logging.info("Looping Background")
        background_clip = vfx.make_loopable(background_clip, cross=0)
        background_clip = vfx.loop(background_clip, duration=v.duration)
    else:
        logging.info("Not Looping Background")
        background_clip = background_clip.set_duration(v.duration)

    v.clips.insert(0,background_clip)

    post_video = CompositeVideoClip(v.clips)
    #video_filename = str(Path("tmp", v.meta.id + "_" + str(count) + "_" + c.id + ".mp4"))
    video_filename = str(Path("final", v.meta.id + "_" + safe_filename(v.meta.title) + ".mp4"))
    json_filename  = str(Path("final", v.meta.id + "_" + safe_filename(v.meta.title) + ".json"))

    data = {
        'title': v.meta.title ,
        'subreddit': 'askreddit',
        'duration': v.duration,
        'height': height,
        'width': width
    }

    with open(json_filename, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    post_video.write_videofile(video_filename)
    


