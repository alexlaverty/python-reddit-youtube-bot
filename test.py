import logging 
from moviepy.editor import *
import random 

height = 720
width = 1280

clip_margin = 50 
fontsize = 32
txt_clip_size = (width - (clip_margin * 2), None)

print(txt_clip_size)

texts = ["Why do billionaires and other very rich individuals try so hard to avoid paying taxes when they will still be rich whether they pay the taxes or not?",
        "Overall, people get taxed on yearly income or capital gains. If you dont claim an income... no tax. Your business took a loss? No corporate tax this year. Capital gains tax kicks in once you pull out of your portfolio.",
        "There's something else that I need you to know and it's going to happen soon."]

clip_list = []

for text in texts:
    txt_clip = TextClip(text, 
                        font="Verdana",
                        fontsize = 32, 
                        color = 'white',
                        size = txt_clip_size,
                        kerning=-1,
                        method='caption',
                        bg_color='blue',
                        align='West')\
                        .set_duration(3)\
                        .set_pos((clip_margin,40))\
                        #.resize(0.33)
                        #.margin(20)\
    clip_list.append(txt_clip)
                        
                    
text_clip = concatenate(clip_list, method = "compose")

text_clip.write_videofile("test_cat.mp4", fps = 24, codec = 'mpeg4')

background = random.choice(os.listdir("backgrounds"))

print("Randomly Selected Background : " + background)

background_clip = VideoFileClip("backgrounds\\" + background)\
                                                .set_duration(text_clip.duration)\
                                                .set_opacity(0.1)


post_video = CompositeVideoClip([background_clip, 
                                text_clip.set_position("40","40")])

video_filename = "test_final.mp4"
post_video.write_videofile(video_filename)