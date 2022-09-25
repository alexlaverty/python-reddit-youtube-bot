
from pathlib import Path

subreddits = [
    "AmItheAsshole",
    "antiwork",
    "AskMen",
    "ChoosingBeggars",
    "hatemyjob",
    "NoStupidQuestions",
    "pettyrevenge",
    "Showerthoughts",
    "TooAfraidToAsk",
    "TwoXChromosomes",
    "unpopularopinion"
    ]
    
max_video_length = 600 # Seconds
comment_limit = 600

assets_directory = "assets"
audio_directory = str(Path("temp"))

background_directory = str(Path(assets_directory,"backgrounds"))
background_opacity = 0.5
background_volume = 0.5

video_height = 720
video_width = 1280
clip_size = (video_width, video_height)

disablecompile = False
disableupload = False

enable_overlay = True

fonts_directory = str(Path(assets_directory,"fonts"))
image_backgrounds_directory = str(Path(assets_directory,"image_backgrounds"))
images_directory = str(Path(assets_directory,"images"))
thumbnails_directory = str(Path(assets_directory,"images"))

pause = 1 # Pause after speech
soundeffects_directory = str(Path(assets_directory,"soundeffects"))

text_bg_color = "#1A1A1B"
text_bg_opacity = 1
text_color = "white"
text_font = "Verdana-Bold"
text_fontsize = 32

download_enabled = True