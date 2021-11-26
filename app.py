import praw 
import yaml
import config
import logging
import video 
import os
from pathlib import Path
import re 
import argparse
import settings 


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])
    
r = praw.Reddit(client_id=config.praw_client_id,
                client_secret=config.praw_client_secret,
                user_agent=config.praw_user_agent)

def safe_filename(text):
    text = text.replace(" ","_")
    return "".join([c for c in text if re.match(r'\w', c)])[:50]

class ttsvibelounge():
    subreddits = ['NoStupidQuestions+AmItheAsshole+antiwork+AskMen+unpopularopinion+Showerthoughts+TooAfraidToAsk+TwoXChromosomes+pettyrevenge']
    validposts = []
    videos = []
    directories = ["final","temp","assets"]
    asset_directories = ["audio","backgrounds","fonts","images","soundeffects"]
    post_max = 10

    def valid_post(self, submission):
        if not submission.stickied and submission.is_self:
            return True
        else:
            return False

    def get_valid_posts(self):
        logging.info('========== Scraping Reddit Posts ==========')
        for subreddit in self.subreddits:
            logging.info('Getting Posts from subreddit : ' + subreddit)
            for submission in r.subreddit(subreddit).hot(limit=50):
                if self.valid_post(submission):
                    self.validposts.append(submission)

    def download_assets(self):
        logging.info('Downloading Assets')
        # Get latest Royalty Free Lofi Videos

    def create_directories(self):
        logging.info('Checking Directory Structure')
        for directory in self.directories:
            self.create_directory(directory)

        for asset_directory in self.asset_directories:
            self.create_directory(str(Path("assets", asset_directory)))

    def create_directory(self, path):
        logging.info(f'Checking Directory : {path}')
        if not os.path.exists(path):
            logging.info('Creating Directory : ' + path)
            os.makedirs(path)

    def clean_temp_dir(self):
        logging.info(f'Cleaning Files')
        audio_files = os.listdir(settings.audio_directory)
        for item in audio_files:
            if item.endswith(".mp3"):
                os.remove(os.path.join(settings.audio_directory, item))

        final_files = os.listdir("final")
        for item in final_files:
            if item.endswith(".mp4"):
                os.remove(os.path.join(final_files, item))

def main(args):
    tvl = ttsvibelounge()
    tvl.create_directories()
    tvl.download_assets()
    if args.clean:
        tvl.clean_temp_dir()
        
    if args.disableupload:
        settings.disableupload = True

    if args.disablecompile:
        settings.disablecompile = True

    tvl.get_valid_posts()

    i = 0
    for post in tvl.validposts:
        video_final_path = str(Path("final", post.id + "_" + safe_filename(post.title) + ".mp4"))
        if os.path.exists(video_final_path):
            logging.info('Post Video already exists, skipping post : ' + video_final_path)
            continue

        post_title = f"{post.title} - {post.subreddit_name_prefixed}"
        if len(post_title) > 100 :
            logging.info('Post title exceeds 100 characeters, skipping post... :')
            logging.info(post_title)
            continue

        if len(post.selftext) > 1000 :
            logging.info('SelfText exceeds 1000 characeters, skipping post... :')
            logging.info(post_title)
            continue

        if post.over_18 :
            logging.info('Skipping NSFW Post... :')
            logging.info(post_title)
            continue

        post.comments.replace_more(limit=0)
        post_video = video.create(post)
        tvl.videos.append(post_video)
        i += 1
        if i == tvl.post_max:
            logging.info('Reached Max Posts Limit : ' + str(tvl.post_max))
            break
    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TTS Vibe Lounge')
    parser.add_argument('-c','--clean', help='Clean Temp Working Directory', action='store_true')
    parser.add_argument('-z','--disableupload', help='Dont Upload Video', action='store_true')
    parser.add_argument('-x','--disablecompile', help='Dont Compile Video', action='store_true')
    args = parser.parse_args()
    main(args)