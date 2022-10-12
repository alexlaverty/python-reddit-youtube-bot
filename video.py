from moviepy.editor import *
from pathlib import Path
import emoji 
import json 
import logging 
import os 
import random 
import re
import settings
import speech
import sys
import thumbnail
import youtube 
import bing



def give_emoji_free_text(data):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', data)

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])


def random_hex_colour():
    r = lambda: random.randint(0,255)
    rcolor = '#%02X%02X%02X' % (r(),r(),r()) 
    return rcolor

def print_post_details(post):
    logging.info("SubReddit : " + post.subreddit_name_prefixed)
    logging.info("Title     : " + post.title)
    logging.info("Score     : " + str(post.score))
    logging.info("ID        : " + str(post.id))
    logging.info("URL       : " + post.url)
    logging.info("SelfText  : " + post.selftext)
    logging.info("NSFW?     : " + str(post.over_18))

def print_comment_details(comment):
    logging.info("Author   : " + str(comment.author))
    logging.info("id       : " + str(comment.id))
    logging.info("Stickied : " + str(comment.stickied))
    logging.info("Body     : " + give_emoji_free_text(str(comment.body)))
    
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
                json="",
                theme=None
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
        self.theme = theme

    def get_background(self):
        self.background = random.choice(os.listdir(settings.background_directory))
        logging.info('Randomly Selecting Background : ' + self.background)
    
    def compile(self):
        pass

def contains_url(text):
    matches = ["http://", "https://"]
    if any(x in text for x in matches):
        return True

def convert_keywords_to_string(keywords):
    keyword_string = ""
    for keyword in keywords:
        keyword_string = keyword_string + str(keyword[0].encode('ascii', 'ignore').decode('ascii')) + " "
    return keyword_string.strip()

def create(video_directory, post):
    logging.info('========== Processing Reddit Post ==========')
    print_post_details(post)

    v = Video()
    v.meta = post
    v.clips = []
    v.get_background()

    thumbnail_name = v.meta.id + "_thumbnail.png"
    v.thumbnail = str(Path(video_directory, thumbnail_name))
    
    subreddit_name = v.meta.subreddit_name_prefixed.replace("r/","")

    v.description = f"{v.meta.subreddit_name_prefixed} \n\n{v.meta.title} \n{v.meta.url}\n\n{v.meta.selftext}\n\nCredits :\n\n Motion Graphics provided by https://www.tubebacks.com\n\nYouTube Channel: https://goo.gl/aayJRf\n\n#reddit #{subreddit_name} #tts"
    v.title = f"{v.meta.title} ({v.meta.subreddit_name_prefixed})"
    height = 720
    width = 1280
    clip_margin = 50 
    clip_margin_top = 30
    txt_clip_size = (width - (clip_margin * 2), None)

    current_clip_text =""
    t = 0

    # intro_clip = VideoFileClip("intro_welcome_crop.mp4")\
    #                 .set_start(0)
    
    # v.clips.append(intro_clip)

    # t += intro_clip.duration

    tb = t

    audio_title = str(Path(video_directory, v.meta.id + "_title.mp3"))
    
    title_speech_text = f"From the subreddit {subreddit_name}. {v.meta.title}"

    speech.create_audio(audio_title, title_speech_text)

    audioclip_title = AudioFileClip(audio_title).volumex(2)

    subreddit_clip = TextClip(v.meta.subreddit_name_prefixed, 
                            font="Impact",
                            fontsize = 60, 
                            color = settings.text_color,
                            size = txt_clip_size,
                            kerning=-1,
                            method='caption',
                            ##bg_color=settings.text_bg_color,
                            align='West')\
                            .set_position((40,40))\
                            .set_duration(audioclip_title.duration + settings.pause)\
                            .set_start(t)   

    v.clips.append(subreddit_clip)

    title_fontsize, lineheight = get_font_size(len(v.meta.title))

    title_clip = TextClip(v.meta.title, 
                            font="Impact",
                            fontsize = title_fontsize, 
                            color = settings.text_color,
                            size = txt_clip_size,
                            kerning=-1,
                            method='caption',
                            ##bg_color=settings.text_bg_color,
                            align='Center')\
                            .set_position(("center","center"))\
                            .set_duration(audioclip_title.duration + settings.pause)\
                            .set_audio(audioclip_title)\
                            .set_start(t)
                            
    v.clips.append(title_clip)

    t += audioclip_title.duration + settings.pause
    v.duration += audioclip_title.duration + settings.pause

    newcaster_start = t

    if v.meta.selftext :
        logging.info('========== Processing Submission SelfText ==========')
        logging.info(v.meta.selftext)

        selftext = v.meta.selftext

        selftext = give_emoji_free_text(selftext)
        selftext = os.linesep.join([s for s in selftext.splitlines() if s])

        logging.info("selftext Length  : " + str(len(selftext)))

        selftext_lines = selftext.splitlines()

        for selftext_line_count, selftext_line in enumerate(selftext_lines):
            logging.info("selftext_line     : " + selftext_line)
            selftext_audio_filepath = str(Path(video_directory, v.meta.id + "_selftext_" + str(selftext_line_count) + ".mp3"))
            speech.create_audio(selftext_audio_filepath, selftext_line)
            selftext_audioclip = AudioFileClip(selftext_audio_filepath)

            current_clip_text += selftext_line + "\n"
            logging.info("Current Clip Text :")
            logging.info(current_clip_text)
            logging.info(f"SelfText Fontsize : {settings.text_fontsize}")
            
            selftext_clip = TextClip(current_clip_text, 
                                font=settings.text_font,
                                fontsize = settings.text_fontsize, 
                                color = settings.text_color,
                                size = txt_clip_size,
                                kerning=-1,
                                method='caption',
                                #bg_color=settings.text_bg_color,
                                align='West')\
                                .set_position((clip_margin,clip_margin_top))\
                                .set_duration(selftext_audioclip.duration + settings.pause)\
                                .set_audio(selftext_audioclip)\
                                .set_start(t)\
                                .set_opacity(settings.text_bg_opacity)\
                                .volumex(1.5)
                                

            if selftext_clip.h > height:
                logging.info("Text exceeded Video Height, reset text")
                current_clip_text = selftext_line + "\n"
                selftext_clip = TextClip(current_clip_text, 
                        font=settings.text_font,
                        fontsize = settings.text_fontsize, 
                        color = settings.text_color,
                        size = txt_clip_size,
                        kerning=-1,
                        method='caption',
                        #bg_color=settings.text_bg_color,
                        align='West')\
                        .set_position((clip_margin,clip_margin_top))\
                        .set_opacity(settings.text_bg_opacity)\
                        .set_duration(selftext_audioclip.duration + settings.pause)\
                        .set_audio(selftext_audioclip)\
                        .set_start(t)

                if selftext_clip.h > height:
                    logging.info("Comment Text Too Long, Skipping Comment")
                    continue   

            t += selftext_audioclip.duration + settings.pause
            v.duration += selftext_audioclip.duration + settings.pause
            

            v.clips.append(selftext_clip)
            logging.info("Video Clips : ")
            logging.info(str(len(v.clips)))
            

        logging.info("Current Video Duration : " + str(v.duration))



    static_clip = VideoFileClip("static.mp4")\
                    .set_duration(1)\
                    .set_position(("center","center"))\
                    .set_start(t)\
                    .set_opacity(settings.background_opacity)\
                    .volumex(0.3)

    v.clips.append(static_clip)
    t += static_clip.duration
    v.duration += static_clip.duration

    current_clip_text = ""

    for count, c in enumerate(v.meta.comments):
        logging.info(f'========== Processing Reddit Comment {count}/{settings.comment_limit} ==========')
        print_comment_details(c)
        logging.info("Comment #  : " + str(count))

        comment = c.body 
        if len(comment) > 1000 :
            logging.info('Comment exceeds 1000 characeters, skipping post... :')
            logging.info(comment)
            continue
        
        if comment == "[removed]":
            logging.info("Skipping Comment : " + comment)
            continue

        comment = give_emoji_free_text(comment)
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
            audio_filepath = str(Path(video_directory, v.meta.id + "_" + c.id + "_" + str(comment_line_count) + ".mp3"))
            speech.create_audio(audio_filepath, comment_line)
            audioclip = AudioFileClip(audio_filepath)

            current_clip_text += comment_line + "\n\n"
            logging.info("Current Clip Text :")
            logging.info(current_clip_text)

            txt_clip = TextClip(current_clip_text, 
                                font=settings.text_font,
                                fontsize = settings.text_fontsize, 
                                color = settings.text_color,
                                size = txt_clip_size,
                                kerning=-1,
                                method='caption',
                                #bg_color=settings.text_bg_color,
                                align='West')\
                                .set_position((clip_margin,clip_margin_top))\
                                .set_duration(audioclip.duration + settings.pause)\
                                .set_audio(audioclip)\
                                .set_start(t)\
                                .set_opacity(settings.text_bg_opacity)\
                                .volumex(1.5)
                                

            if txt_clip.h > height:
                logging.info("Text exceeded Video Height, reset text")
                current_clip_text = comment_line + "\n\n"
                txt_clip = TextClip(current_clip_text, 
                        font=settings.text_font,
                        fontsize = settings.text_fontsize, 
                        color = settings.text_color,
                        size = txt_clip_size,
                        kerning=-1,
                        method='caption',
                        #bg_color=settings.text_bg_color,
                        align='West')\
                        .set_position((clip_margin,clip_margin_top))\
                        .set_duration(audioclip.duration + settings.pause)\
                        .set_audio(audioclip)\
                        .set_opacity(settings.text_bg_opacity)\
                        .set_start(t)

                if txt_clip.h > height:
                    logging.info("Comment Text Too Long, Skipping Comment")
                    continue   

            t += audioclip.duration + settings.pause
            v.duration += audioclip.duration + settings.pause
            

            v.clips.append(txt_clip)
            logging.info("Video Clips : ")
            logging.info(str(len(v.clips)))

        logging.info("Current Video Duration : " + str(v.duration))

        if v.duration > settings.max_video_length:
            logging.info("Reached Maximum Video Length : " + str(settings.max_video_length))
            logging.info("Exiting...")     
            break 

        if count == settings.comment_limit:
            logging.info("Reached Maximum Number of Comments Limit : " + str(settings.comment_limit))
            logging.info("Exiting...")
            break
        
    

    
    background_filepath = str(Path(settings.background_directory, v.background))
    
    background_clip = VideoFileClip(background_filepath)\
                        .set_start(tb)\
                        .volumex(settings.background_volume)

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

    if settings.enable_overlay :
        clip_video_overlay = VideoFileClip(settings.video_overlay_filepath)\
                                .set_start(tb)\
                                .resize(settings.clip_size)\
                                .set_opacity(0.8)\
                                .volumex(0)

        if clip_video_overlay.duration < v.duration:
            logging.info("Looping Overlay")
            #background_clip = vfx.make_loopable(background_clip, cross=0)
            clip_video_overlay = vfx.loop(clip_video_overlay, duration=v.duration).without_audio()
            logging.info("Looped Overlay Clip Duration : " + str(clip_video_overlay.duration))
        else:
            logging.info("Not Looping Overlay")
            clip_video_overlay = clip_video_overlay.set_duration(v.duration)

        v.clips.insert(1,clip_video_overlay)

    if settings.enable_newscaster and settings.newscaster_filepath :
        logging.info(f"Adding Newscaster : { settings.newscaster_filepath }")
        clip_video_newscaster = VideoFileClip( settings.newscaster_filepath )\
                                .set_position( settings.newscaster_position )\
                                .set_start(newcaster_start)\
                                .resize(settings.newcaster_size)\
                                .set_opacity(1)\
                                .volumex(0)

        if settings.newscaster_remove_greenscreen :
            # Green Screen Video https://github.com/Zulko/moviepy/issues/964
            clip_video_newscaster = clip_video_newscaster.fx(vfx.mask_color, 
                                                             color=settings.newscaster_greenscreen_color, 
                                                             thr=settings.newscaster_greenscreen_remove_threshold, 
                                                             s=5)

        if clip_video_newscaster.duration < v.duration:
            logging.info("Looping Newscaster")
            clip_video_newscaster = vfx.loop(clip_video_newscaster, duration=v.duration - newcaster_start).without_audio()
            logging.info("Looped Newscaster Clip Duration : " + str(clip_video_newscaster.duration))
        else:
            logging.info("Not Looping Newscaster")
            clip_video_newscaster = clip_video_newscaster.set_duration(v.duration - newcaster_start)

        v.clips.append(clip_video_newscaster)

    post_video = CompositeVideoClip(v.clips)

    v.filepath = str(Path(video_directory, v.meta.id + "_" + safe_filename(v.meta.title) + ".mp4"))
    v.json  = str(Path(video_directory, v.meta.id + "_" + safe_filename(v.meta.title) + ".json"))

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
    
    if settings.disablecompile:
        logging.info("Skipping Video Compilation --disablecompile passed")
    else:
        logging.info("Compiling video, this takes a while, please be patient : )")
        post_video.write_videofile(v.filepath)
    
    if settings.disablecompile or settings.disableupload:
        logging.info("Skipping Upload...")
    else:
        youtube.publish(v)
        print("skipping ")


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))