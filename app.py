import praw 
import yaml
import config
import logging
import video 
import os
from pathlib import Path
import re 

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
    directories = ["backgrounds","audio","final","tmp","thumbnails"]
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
            if not os.path.exists(directory):
                logging.info('Creating Directory : ' + directory)
                os.makedirs(directory)

def main():
    tvl = ttsvibelounge()
    tvl.create_directories()
    tvl.download_assets()
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

        post.comments.replace_more(limit=0)
        post_video = video.create(post)
        tvl.videos.append(post_video)
        i += 1
        if i == tvl.post_max:
            break
    
    

if __name__ == "__main__":
    main()