"""Configuration settings for the bot."""
from sys import platform
from pathlib import Path

subreddits = [
    "askreddit",
    # "AmItheAsshole",
    "antiwork",
    "AskMen",
    "ChoosingBeggars",
    "hatemyjob",
    "NoStupidQuestions",
    "pettyrevenge",
    "Showerthoughts",
    "TooAfraidToAsk",
    "TwoXChromosomes",
    "unpopularopinion",
    "confessions",
    "confession",
]

subreddits_excluded = [
    "r/CFB",
]

# Sort reddit posts by choices ["hot","top"]
reddit_post_sort = "hot"
# Sort by "all", "day", "hour", "month", "week", or "year"
reddit_post_time_filter = "day"

# Speech Settings
edge_tts_voice = "en-GB-RyanNeural"
pause = 1  # Pause after speech
streamlabs_polly_voice = "Brian"
tiktok_voice = "en_us_006"

# Set the gtts language, examples :
# English (en)
# Spanish (es)
# French (fr)
# German (de)
# Italian (it)
# Portuguese (pt)
# Dutch (nl)
# Russian (ru)
# Mandarin Chinese (zh-cn)
# Japanese (ja)
gtts_language = "en"

# Choices ["polly","balcon","gtts","tiktok","edge-tts","streamlabspolly"]
voice_engine = "edge-tts"

# Comment Settings
banned_keywords_base64 = "cG9ybixzZXgsamVya2luZyBvZmYsc2x1dCxyYXB\
                          lLGZ1Y2sscmV0YXJkLG1vdGhlcmZ1Y2tlcixyYXBpc3Q="
theme = "dark"
minimum_num_comments = 200
reddit_comment_opacity = 1
reddit_comment_width = 0.95
comment_length_max = 600
comment_limit = 100
comment_screenshot_timeout = 30000

# Video settings
background_colour = [26, 26, 27]
background_opacity = 0.5
background_volume = 0.5
# commentstyle = ["reddit", "text"]
commentstyle = "reddit"
enable_background = False
enable_comments = True
enable_compilation = True
enable_nsfw_content = False
enable_overlay = False
enable_selftext = True
enable_upload = False
enable_screenshot_title_image = False
enable_reddit_mentions = False
enable_reddit_saved = False
enable_background_music = False
background_music_path = ""
background_music_volume = 0.3  # 30 percent (0.3) of the original volume
thumbnail_image_path = ""
lexica_download_enabled = True  # Download files from Lexica
max_video_length = 600  # Seconds
maximum_length_self_text = 3000
minimum_submission_score = 2000
number_of_thumbnails = 1
submission_limit = 500
text_bg_color = "#1A1A1B"
text_bg_opacity = 1
text_color = "white"
text_font = "Verdana-Bold"
text_fontsize = 32
clip_margin = 50
clip_margin_top = 30
title_length_maximum = 100
title_length_minimum = 20
total_posts_to_process = 10
video_height = 720
video_width = 1280
vertical_video_width = 1080
vertical_video_height = 1920
# Video Orientation choices ["landscape","portrait"]
orientation = "landscape"


clip_size = (video_width, video_height)

# Thumbnail settings choices ['random','lexica']
thumbnail_image_source = "lexica"
thumbnail_text_width = video_width * 0.65
enable_thumbnail_image_gradient = True

# Directories and paths
assets_directory = "assets"
temp_directory = str(Path(assets_directory, "work_dir"))
audio_directory = temp_directory
speech_directory = temp_directory
screenshot_directory = temp_directory
fonts_directory = str(Path(assets_directory, "fonts"))
image_backgrounds_directory = str(Path(assets_directory, "image_backgrounds"))
images_directory = str(Path(assets_directory, "images"))
thumbnails_directory = str(Path(assets_directory, "images"))
background_directory = str(Path(assets_directory, "backgrounds"))
music_directory = str(Path(assets_directory, "music"))
soundeffects_directory = str(Path(assets_directory, "soundeffects"))
video_overlay_filepath = str(Path(assets_directory, "particles.mp4"))
videos_directory = "videos"
add_hashtag_shorts_to_description = False
shorts_mode_enabled = False

# Youtube
# Choices ['private', 'unlisted', 'public']
youtube_privacy_status = "public"

# Newcaster Settings
enable_newscaster = False
newscaster_remove_greenscreen = True
newscaster_greenscreen_color = [1, 255, 17]  # Enter Green Screen RGB Colour
newscaster_greenscreen_remove_threshold = 100
newscaster_filepath = str(Path(assets_directory, "newscaster.mp4").resolve())
newscaster_position = ("left", "bottom")
newcaster_size = (video_width * 0.5, video_height * 0.5)

# Tweak for performance, set number of cores
threads = 4

if platform == "linux" or platform == "linux2":
    firefox_binary = "/opt/firefox/firefox"
elif platform == "win32":
    firefox_binary = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
