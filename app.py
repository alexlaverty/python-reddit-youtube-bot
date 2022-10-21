import praw 
# import yaml
import config
import logging
# import video 
import os
from pathlib import Path
import re 
# import argparse
import settings 
from tabulate import tabulate
import thumbnail
import reddit 
import video as vid
import argparse

logging.basicConfig(
    format=u'%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log", 'w', 'utf-8'),
        logging.StreamHandler()
    ])

def process_submissions(submissions):
    for submission in submissions:
        process_submission(submission)

def process_submission(submission):
    print("PROCESSING SUBMISSION")
    print(f"{str(submission.id)}, {str(submission.score)}, {str(submission.num_comments)}, {len(submission.selftext)}, {submission.subreddit_name_prefixed}, {submission.title}") 
    video = Video(submission)
    title_path = safe_filename(submission.title)

    # Create Video Directories
    video.folder_path = str(Path(settings.videos_directory,f"{submission.id}_{title_path}")) 
    video.thumbnail_path = str(Path(video.folder_path,"thumbnail.png")) 
    video.video_filepath = str(Path(video.folder_path,f"{submission.id}_{title_path}.mp4")) 
    create_directory(video.folder_path)

    if os.path.exists(video.video_filepath):
        print(f"Final video already compiled : {video.video_filepath}")
    else:
        # Generate Thumbnail
        thumbnail.generate(video_directory=video.folder_path,
                            subreddit=submission.subreddit_name_prefixed, 
                            title=submission.title,
                            number_of_thumbnails=settings.number_of_thumbnails)
        if args.thumbnail_only:
            print("Generating Thumbnail only skipping video compile!")
        else:
            vid.create(video_directory=video.folder_path, post=submission)


def safe_filename(text):
    text = text.replace(" ","_")
    return "".join([c for c in text if re.match(r'\w', c)])[:50]

def create_directory(folder_path):
    if not os.path.exists(folder_path):
        logging.info('Creating Directory : ' + folder_path)
        os.makedirs(folder_path)

class Video:
    def __init__(self, submission):
        self.submission = submission
        self.comments = []
        self.clips = []
        self.background = None
        self.music = None
        self.thumbnail_path = None
        self.folder_path = None
        self.video_filepath = None


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='Reddit Post Url')
    parser.add_argument('-t','--thumbnail-only', action='store_true', help='Generate a Thumbnail Only')
    parser.add_argument('-l','--video-length', help='Set the length of the outputted video in seconds')
    args = parser.parse_args()

    if args.video_length:
        settings.max_video_length = args.video_length
    if args.url:
        urls = args.url.split(",")
        submissions = []
        for url in urls:
            submissions.append(reddit.get_reddit_submission(url))
    else:
        submissions = reddit.posts()
    if submissions:
        process_submissions(submissions)
