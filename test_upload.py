from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

import os

directory = os.getcwd()
print(directory)

class Video():
    video = f"{directory}\\videos\\yf93yg_What_city_will_you_NEVER_visit_based_on_its_reputa\\final.mp4"
    title = "What city will you NEVER visit based on it's reputation? (r\\AskReddit)"
    thumbnail = f"{directory}\\videos\\yf93yg_What_city_will_you_NEVER_visit_based_on_its_reputa\\thumbnail_2.png"
    description = "TTSVibeLounge"

v = Video()


# loggin into the channel
channel = Channel()
channel.login("client_secret.json", "credentials.storage")

# setting up the video that is going to be uploaded
video = LocalVideo(file_path=v.video)

# setting snippet
video.set_title(v.title)
video.set_description(v.description)
video.set_tags(["reddit", "tts"])
video.set_category("gaming")
video.set_default_language("en-US")

# setting status
video.set_embeddable(True)
video.set_license("creativeCommon")
video.set_privacy_status("public")
video.set_public_stats_viewable(True)

# setting thumbnail
video.set_thumbnail_path(v.thumbnail)

# uploading video and printing the results
video = channel.upload_video(video)
print(video.id)
print(video)