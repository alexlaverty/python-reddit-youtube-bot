from pathlib import Path
import argparse
import logging
import os
import reddit.reddit as reddit
import config.settings as settings
import sys
import thumbnail.thumbnail as thumbnail
import video_generation.video as vid
import platform
from utils.common import (safe_filename, create_directory)

logging.basicConfig(
    format=u'%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log", 'w', 'utf-8'),
        logging.StreamHandler()
    ])


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


def process_submissions(submissions):
    post_total = settings.total_posts_to_process
    post_count = 0

    for submission in submissions:
        title_path = safe_filename(submission.title)
        folder_path = str(Path(settings.videos_directory,
                          f"{submission.id}_{title_path}"))
        video_filepath = str(Path(folder_path,
                             f"{submission.id}_{title_path}.mp4"))
        if os.path.exists(str(Path(folder_path,
                          f"{submission.id}_{title_path}.mp4"))):
            print(f"Final video already compiled : {video_filepath}")
        else:
            if post_count >= post_total:
                print("Reached post count total!")
                break
            process_submission(submission)
            post_count += 1


def process_submission(submission):
    print("===== PROCESSING SUBMISSION =====")
    print(f"{str(submission.id)}, {str(submission.score)}, \
            {str(submission.num_comments)}, \
            {len(submission.selftext)}, \
            {submission.subreddit_name_prefixed}, \
            {submission.title}")
    video = Video(submission)
    title_path = safe_filename(submission.title)

    # Create Video Directories
    video.folder_path = str(Path(settings.videos_directory,
                            f"{submission.id}_{title_path}"))

    video.video_filepath = str(Path(video.folder_path,
                               "final.mp4"))
    create_directory(video.folder_path)

    if os.path.exists(video.video_filepath):
        print(f"Final video already compiled : {video.video_filepath}")
    else:
        # Generate Thumbnail

        thumbnails = thumbnail.generate(video_directory=video.folder_path,
                            subreddit=submission.subreddit_name_prefixed,
                            title=submission.title,
                            number_of_thumbnails=settings.number_of_thumbnails)
        if thumbnails:
            video.thumbnail_path = thumbnails[0]

        if args.thumbnail_only:
            print("Generating Thumbnail only skipping video compile!")
        else:
            vid.create(video_directory=video.folder_path,
                       post=submission,
                       thumbnails=thumbnails)


def banner():
    print("##### YOUTUBE REDDIT BOT #####")


def print_version_info():
    print(f"OS Version     : {platform.system()} {platform.release()}")
    print(f"Python Version : {sys.version}")


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--disable-selftext',
                        action='store_true',
                        help='Disable selftext video generation')

    parser.add_argument('--voice-engine',
                        help='Specify which text to speech engine to use',
                        choices=["polly",
                                 "balcon",
                                 "gtts",
                                 "tiktok",
                                 "edge-tts",
                                 "streamlabspolly"])

    parser.add_argument('-c',
                        '--comment-style',
                        help='Specify text based or reddit image comments',
                        choices=['text', 'reddit'])

    parser.add_argument('-l', '--video-length',
                        help='Set how long you want the video to be',
                        type=int)

    parser.add_argument('-n', '--enable-nsfw',
                        action='store_true',
                        help='Allow NSFW Content')

    parser.add_argument('-o', '--disable-overlay',
                        action='store_true',
                        help='Disable video overlay')

    parser.add_argument('-s', '--story-mode',
                        action='store_true',
                        help='Generate video for post title and selftext only,\
                            disables user comments')

    parser.add_argument('-t', '--thumbnail-only',
                        action='store_true',
                        help='Generate thumbnail image only')

    parser.add_argument('-p', '--publish',
                        action='store_true',
                        help='Publish video to youtube, \
                            requires cookies.json to be valid')

    parser.add_argument('-u', '--url',
                        help='Specify Reddit post url, \
                        seperate with a comma for multiple posts.')

    args = parser.parse_args()

    if args.comment_style:
        logging.info(f'Setting comment style to : {args.comment_style}')
        settings.commentstyle = args.comment_style

    if args.voice_engine:
        logging.info(f'Setting speech engine to : {args.voice_engine}')
        settings.voice_engine = args.voice_engine

    if args.video_length:
        logging.info(f'Setting video length to : \
                    {str(args.video_length)} seconds')
        settings.max_video_length = args.video_length

    if args.disable_overlay:
        logging.info('Disabling Video Overlay')
        settings.enable_overlay = False

    if args.enable_nsfw:
        logging.info('Enable NSFW Content')
        settings.enable_nsfw_content = True

    if args.story_mode:
        logging.info('Story Mode Enabled!')
        settings.enable_comments = False

    if args.disable_selftext:
        logging.info('Disabled SelfText!')
        settings.enable_selftext = False

    if args.publish:
        logging.info('Publish video enabled!')
        settings.disable_upload = False

    return args

if __name__ == "__main__":
    banner()
    print_version_info()
    args = get_args()

    if args.url:
        urls = args.url.split(",")
        submissions = []
        for url in urls:
            submissions.append(reddit.get_reddit_submission(url))
    else:
        submissions = reddit.posts()

    if submissions:
        process_submissions(submissions)
