from moviepy.editor import *  
import random 
from pathlib import Path
import textwrap
import nltk
from nltk.corpus import stopwords
import random
import logging 

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])

def generate(video, filepath):
    logging.info('========== Generating Thumbnail ==========')

    colors = ["blue","green","yellow","red"]
    stop_word_colour = random.choice(colors)

    image = random.choice(os.listdir("images"))
    image_path = str(Path("images", image))
    logging.info('Randomly Selecting Background : ' + image_path)
    text = video.meta.title
    subreddit = video.meta.subreddit_name_prefixed
    print("Title Length :")
    print(len(text))

    s=set(stopwords.words('english'))
    words = text.split(" ")
    unique_words = list(filter(lambda w: not w in s,text.split()))

    clips = []

    margin = 40
    txt_y = 0 + margin
    txt_x = 0 + margin
    width = 1280
    height = 720
    fontsize = 50
    lineheight = 60

    if len(text) < 100:
        print("Increasing Font Size")
        fontsize = 70
        lineheight = 90 

    print("fontsize")
    print(fontsize)

    print("lineheight")
    print(lineheight)

    background_clip = TextClip("",
                            size=(width,height), 
                            bg_color="#404040",
                            method="caption")

    clips.append(background_clip)

    img_width = width/2
    img_clip = ImageClip(image_path).resize(width=img_width, height=height)\
                                    .set_position(("right","bottom"))\
                                    .set_opacity(0.8)

    clips.append(img_clip)

    subreddit_clip = TextClip(subreddit,
                        fontsize = 45, 
                        color="white", 
                        align='center', 
                        font="Verdana-Bold", 
                        bg_color="#404040",
                        method="caption")\
                        .set_pos((margin, margin))\
                        .set_opacity(0.8)

    clips.append(subreddit_clip)

    txt_y += 50

    for word in words:
        if word in unique_words:
            word_color = "white"
        else:
            word_color = stop_word_colour

        if txt_x > (width / 3):
            txt_x = 0 + margin
            txt_y += lineheight

        txt_clip = TextClip(word,
                            fontsize = fontsize, 
                            color=word_color, 
                            align='center', 
                            font="Verdana-Bold", 
                            bg_color="#404040",
                            method="caption")\
                            .set_pos((txt_x, txt_y))\
                            .set_opacity(0.8)

        clips.append(txt_clip)
        txt_x += txt_clip.w + 15
        

    txt_clip = txt_clip.set_duration(10)
    txt_clip = txt_clip.set_position(("center","center"))


    final_video = CompositeVideoClip(clips)
    logging.info('Save Thumbnail to : ' + filepath)
    final_video.save_frame(filepath, 1)

