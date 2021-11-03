from moviepy.editor import *
from pathlib import Path
import logging 
import random 
import re
import speech
import json 
import thumbnail
import os 
import youtube 

max_video_length = 30 # Seconds
comment_limit = 600
background_opacity = 0.5
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
    logging.info("SelfText  : " + post.selftext)

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

def get_font_size(length):

    fontsize = 50
    lineheight = 60

    if length < 10 :
        fontsize = 100
        lineheight = 100

    if length >= 10 and length < 30:
        fontsize = 120
        lineheight = 140

    if length >= 30 and length < 40:
        fontsize = 130
        lineheight = 150

    if length >= 40 and length < 50:
        fontsize = 100
        lineheight = 120

    if length >= 50 and length < 70:
        fontsize = 100
        lineheight = 110

    if length >= 70 and length < 80:
        fontsize = 80
        lineheight = 110

    if length >= 80 and length < 90:
        fontsize = 70
        lineheight = 90

    if length >= 90 and length < 100:
        fontsize = 60
        lineheight = 80

    logging.info(f"Title Length       : {length}")
    logging.info(f"Setting Fontsize   : {fontsize} " )
    logging.info(f"Setting Lineheight : {lineheight} " )

    return fontsize, lineheight

class Video():
    def __init__(self, 
                background=None, 
                clips=[],   
                description="",
                duration=0,
                meta=None, 
                script="", 
                thumbnail=None, 
                title="",
                filepath="",
                json=""
                ):
        self.background = background
        self.clips = clips
        self.description = description
        self.duration = duration
        self.meta = meta
        self.script = script
        self.thumbnail = thumbnail
        self.title = title
        self.filepath = filepath
        self.json = json

    def get_background(self):
        self.background = random.choice(os.listdir("backgrounds"))
        logging.info('Randomly Selecting Background : ' + self.background)
    
    def compile(self):
        pass

def contains_url(text):
    matches = ["http://", "https://"]
    if any(x in text for x in matches):
        return True


def create(post):
    logging.info('========== Processing Reddit Post ==========')
    print_post_details(post)

    v = Video()
    v.meta = post
    v.clips = []
    v.get_background()

    thumbnail_name = v.meta.id + "_thumbnail.png"
    v.thumbnail = str(Path("final", thumbnail_name))
    thumbnail.generate(v, v.thumbnail)
    v.description = f"{v.meta.subreddit_name_prefixed} \\n\\n{v.meta.title} - \\n\\n{v.meta.url}\\n\\n{v.meta.selftext}\\n\\nCredits :\\n\\n Motion Graphics provided by https://www.tubebacks.com\\n\\nYouTube Channel: https://goo.gl/aayJRf\\n\\n"
    v.title = f"{v.meta.title} - {v.meta.subreddit_name_prefixed}"
    height = 720
    width = 1280
    clip_margin = 50 
    clip_margin_top = 30
    fontsize = 32
    txt_clip_size = (width - (clip_margin * 2), None)

    background_filepath = str(Path("backgrounds", v.background))

    current_clip_text =""
    t = 0

    #intro_audio = AudioFileClip("intro.mp3").volumex(2)

    intro_clip = VideoFileClip("intro_welcome_crop.mp4")\
                    .set_start(0)
    
    #intro_clip_with_audio = intro_clip.set_audio(CompositeAudioClip([intro_audio.set_start(1)]))

    v.clips.append(intro_clip)

    t += intro_clip.duration

    tb = t

    audio_title = str(Path("audio", v.meta.id + "_title.mp3"))
    subreddit_name = v.meta.subreddit_name_prefixed.replace("r/","")
    title_speech_text = f"From the subreddit {subreddit_name}. {v.meta.title}"

    speech.create_audio(audio_title, title_speech_text)

    audioclip_title = AudioFileClip(audio_title).volumex(2)

    subreddit_clip = TextClip(v.meta.subreddit_name_prefixed, 
                            font="Verdana-Bold",
                            fontsize = 60, 
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

    title_fontsize, lineheight = get_font_size(len(v.meta.title))

    title_clip = TextClip(v.meta.title, 
                            font="Verdana-Bold",
                            fontsize = title_fontsize, 
                            color = 'white',
                            size = txt_clip_size,
                            kerning=-1,
                            method='caption',
                            #bg_color='blue',
                            align='Center')\
                            .set_pos(("center","center"))\
                            .set_duration(audioclip_title.duration + pause)\
                            .set_audio(audioclip_title)\
                            .set_start(t)
                            
    v.clips.append(title_clip)

    t += audioclip_title.duration + pause
    v.duration += audioclip_title.duration + pause



    if v.meta.selftext:
        logging.info('========== Processing Submission SelfText ==========')
        logging.info(v.meta.selftext)

        selftext = v.meta.selftext
        selftext = os.linesep.join([s for s in selftext.splitlines() if s])

        logging.info("selftext Length  : " + str(len(selftext)))

        selftext_lines = selftext.splitlines()

        for selftext_line_count, selftext_line in enumerate(selftext_lines):
            logging.info("selftext_line     : " + selftext_line)
            selftext_audio_filepath = str(Path("audio", v.meta.id + "_selftext_" + str(selftext_line_count) + ".mp3"))
            speech.create_audio(selftext_audio_filepath, selftext_line)
            selftext_audioclip = AudioFileClip(selftext_audio_filepath)

            current_clip_text += selftext_line + "\n\n"
            logging.info("Current Clip Text :")
            logging.info(current_clip_text)

            selftext_clip = TextClip(current_clip_text, 
                                font="Verdana",
                                fontsize = fontsize, 
                                color = 'white',
                                size = txt_clip_size,
                                kerning=-1,
                                method='caption',
                                #bg_color='blue',
                                align='West')\
                                .set_pos((clip_margin,clip_margin_top))\
                                .set_duration(selftext_audioclip.duration + pause)\
                                .set_audio(selftext_audioclip)\
                                .set_start(t)\
                                .volumex(1.5)
                                

            if selftext_clip.h > height:
                logging.info("Text exceeded Video Height, reset text")
                current_clip_text = selftext_line + "\n\n"
                selftext_clip = TextClip(current_clip_text, 
                        font="Verdana",
                        fontsize = fontsize, 
                        color = 'white',
                        size = txt_clip_size,
                        kerning=-1,
                        method='caption',
                        #bg_color='blue',
                        align='West')\
                        .set_pos((clip_margin,clip_margin_top))\
                        .set_duration(selftext_audioclip.duration + pause)\
                        .set_audio(selftext_audioclip)\
                        .set_start(t)

                if selftext_clip.h > height:
                    logging.info("Comment Text Too Long, Skipping Comment")
                    continue   

            t += selftext_audioclip.duration + pause
            v.duration += selftext_audioclip.duration + pause
            

            v.clips.append(selftext_clip)
            logging.info("Video Clips : ")
            logging.info(str(len(v.clips)))

        logging.info("Current Video Duration : " + str(v.duration))



    static_clip = VideoFileClip("static.mp4")\
                    .set_duration(1)\
                    .resize(width=width, height=height)\
                    .set_start(t)

    v.clips.append(static_clip)
    t += static_clip.duration
    v.duration += static_clip.duration


    for count, c in enumerate(v.meta.comments):
        logging.info(f'========== Processing Reddit Comment {count}/{comment_limit} ==========')
        print_comment_details(c)
        logging.info("Comment #  : " + str(count))

        comment = c.body 

        if comment == "[removed]":
            logging.info("Skipping Comment : " + comment)
            continue


        comment = os.linesep.join([s for s in comment.splitlines() if s])

        logging.info("Comment Length  : " + str(len(comment)))



        if c.stickied:
            logging.info("Skipping Stickied Comment...")
            continue

        if contains_url(comment):
            logging.info("Skipping Comment with URL in it...")
            continue

        comment_lines = comment.splitlines()

        for comment_line_count, comment_line in enumerate(comment_lines):

            if comment == "[removed]":
                logging.info("Skipping Comment : " + comment)
                continue

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
                        .set_opacity(background_opacity)\
                        .set_start(tb)\
                        .volumex(0)

    logging.info("Video Clip Duration      : " + str(v.duration))
    logging.info("Background Clip Duration : " + str(background_clip.duration))

    if background_clip.duration < v.duration:
        logging.info("Looping Background")
        #background_clip = vfx.make_loopable(background_clip, cross=0)
        background_clip = vfx.loop(background_clip, duration=v.duration).without_audio()
        logging.info("Looped Background Clip Duration : " + str(background_clip.duration))
    else:
        logging.info("Not Looping Background")
        background_clip = background_clip.set_duration(v.duration)

    v.clips.insert(0,background_clip)

    post_video = CompositeVideoClip(v.clips)

    v.filepath = str(Path("final", v.meta.id + "_" + safe_filename(v.meta.title) + ".mp4"))
    v.json  = str(Path("final", v.meta.id + "_" + safe_filename(v.meta.title) + ".json"))

    data = {
        'title': v.title,
        'description': v.description,
        'thumbnail': v.thumbnail,
        'duration': v.duration,
        'height': height,
        'width': width
    }

    with open(v.json, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    post_video.write_videofile(v.filepath)
    
    youtube.publish(v)


