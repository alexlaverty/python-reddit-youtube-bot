from moviepy.editor import *  
import random 
from pathlib import Path
import textwrap
import nltk
from nltk.corpus import stopwords
import random
import logging 
import settings
import lexica 

logging.basicConfig(
    format=u'%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log", 'w', 'utf-8'),
        logging.StreamHandler()
    ])

def random_hex_colour():
    r = lambda: random.randint(0,255)
    rcolor = '#%02X%02X%02X' % (r(),r(),r())
    print("Generated random hex colour") 
    print(rcolor)
    return rcolor

def random_rgb_colour():
    rbg_colour = random.choices(range(256), k=3)
    print("Generated random rgb colour") 
    print(rbg_colour)
    return rbg_colour

def get_font_size(length):

    fontsize = 50
    lineheight = 60

    if length < 10 :
        fontsize = 190
        lineheight = 200

    if length >= 10 and length < 20:
        fontsize = 180
        lineheight = 190

    if length >= 20 and length < 30:
        fontsize = 170
        lineheight = 180

    if length >= 30 and length < 40:
        fontsize = 130
        lineheight = 150

    if length >= 40 and length < 50:
        fontsize = 140
        lineheight = 150

    if length >= 50 and length < 60:
        fontsize = 130
        lineheight = 140

    if length >= 60 and length < 70:
        fontsize = 120
        lineheight = 120

    if length >= 70 and length < 80:
        fontsize = 115
        lineheight = 110

    if length >= 80 and length < 90:
        fontsize = 115
        lineheight = 110

    if length >= 90 and length < 100:
        fontsize = 80
        lineheight = 100

    logging.info(f"Title Length       : {length}")
    logging.info(f"Setting Fontsize   : {fontsize} " )
    logging.info(f"Setting Lineheight : {lineheight} " )

    return fontsize, lineheight


def generate(video_directory, subreddit, title, number_of_thumbnails=settings.number_of_thumbnails):
    logging.info('========== Generating Thumbnail ==========')

    colors = ["#FFA500","#B8FF72","#FFC0CB","#89cff0","#ADD8E6","green","yellow","red"]
    stop_word_colour = random.choice(colors)

    
    #image = random.choice(os.listdir(settings.images_directory))
    image_path = str(Path(video_directory, "lexica.png").absolute())

    images = lexica.get_images(video_directory, title, number_of_images=number_of_thumbnails)

    #image_path = str(Path(settings.images_directory, image))
    #logging.info('Randomly Selecting Background : ' + image_path)
    text = title
    nltk.download('stopwords')
    s=set(stopwords.words('english'))
    words = text.split(" ")
    unique_words = list(filter(lambda w: not w in s,text.split()))

    thumbnails = []

    for index, image in enumerate(images):
        clips = []
        thumbnail_path = str(Path(video_directory, f"thumbnail_{index}.png").absolute())
        margin = 40
        txt_y = 0 
        txt_x = 0 + margin
        width = 1280
        height = 720
        #fontsize = get_font_size(len(title))
        fontsize, lineheight = get_font_size(len(title))


        background_clip = TextClip("",
                                size=(width,height), 
                                bg_color="#000000",
                                method="caption").margin(20, color=random_rgb_colour())

        clips.append(background_clip)

        img_width = width/2
        img_clip = ImageClip(image).resize(width=img_width)\
                                        .set_position(("right","center"))\
                                        .set_opacity(0.8)

        clips.append(img_clip)

        subreddit_clip = TextClip(subreddit,
                            fontsize = 85, 
                            color="white", 
                            align='center', 
                            font="Verdana-Bold", 
                            bg_color="#000000",
                            method="caption")\
                            .set_position((margin, 20))\
                            #.set_opacity(0.8)

        clips.append(subreddit_clip)

        txt_y += subreddit_clip.h

        for word in words:
            if word in unique_words:
                word_color = "white"
            else:
                word_color = stop_word_colour

            if txt_x > (width / 2):
                txt_x = 0 + margin
                txt_y += lineheight

            txt_clip = TextClip(word,
                                fontsize = fontsize, 
                                color=word_color, 
                                align='center', 
                                font="Impact", 
                                #bg_color="#000000",
                                stroke_color="#000000",
                                stroke_width=3,
                                method="caption")\
                                .set_position((txt_x, txt_y))
                                #.set_opacity(0.8)

            clips.append(txt_clip)
            txt_x += txt_clip.w + 15
            

        txt_clip = txt_clip.set_duration(10)
        txt_clip = txt_clip.set_position(("center","center"))


        final_video = CompositeVideoClip(clips)
        logging.info('Saving Thumbnail to : ' + thumbnail_path)
        final_video.save_frame(thumbnail_path, 1)
        thumbnails.append(final_video)
    return thumbnails


if __name__ == "__main__":
    class meta():
        title = "What do you desire more than anything else in this world?"
        subreddit_name_prefixed = "r/AskMen"
        id = "4hdu7"

    class Video():
        meta=None

    meta = meta()
    video = Video()
    video.meta = meta

    generate(video, "thumbnail.png", None)