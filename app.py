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
from csvmgr import CsvWriter

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
                                  "final.mp4"))
        if os.path.exists(video_filepath) or csvwriter.is_uploaded(submission.id):
            print(f"Final video already processed : {submission.id}")
        else:
            process_submission(submission)
            post_count += 1
            if post_count >= post_total:
                print("Reached post count total!")
                break


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

    create_directory(video.folder_path)

    video.video_filepath = str(Path(video.folder_path,
                               "final.mp4"))

    if os.path.exists(video.video_filepath):
        print(f"Final video already compiled : {video.video_filepath}")
    else:
        # Generate Thumbnail

        thumbnails = thumbnail.generate(
                    video_directory=video.folder_path,
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

    parser.add_argument('--enable-mentions',
                        action='store_true',
                        help='Check reddit account for u mentions')

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

    parser.add_argument('-p', '--enable-upload',
                        action='store_true',
                        help='Upload video to youtube, \
                             requires client_secret.json and \
                             credentials.storage to be valid')

    parser.add_argument('-u', '--url',
                        help='Specify Reddit post url, \
                        seperate with a comma for multiple posts.')

    parser.add_argument('--subreddits',
                        help='Specify Subreddits, seperate with +')

    parser.add_argument('-b', '--enable-background',
                        action='store_true',
                        help='Enable video backgrounds')

    parser.add_argument('--total-posts', type=int,
                        help='Enable video backgrounds')

    parser.add_argument('--submission-score', type=int,
                        help='Minimum submission score threshold')

    parser.add_argument('--background-directory',
                        help='Folder path to video backgrounds')

    parser.add_argument('--sort', choices=['top', 'hot'],
                        help='Sort Reddit posts by')

    parser.add_argument('--time',
                        choices=["all",
                                 "day",
                                 "hour",
                                 "month",
                                 "week",
                                 "year"],
                        default="day",
                        help='Filter by time')

    parser.add_argument('--orientation', choices=['landscape', 'portrait'],
                        default='landscape',
                        help='Sort Reddit posts by')

    parser.add_argument('--shorts',
                        action='store_true',
                        help='Generate Youtube Shorts Video')

    args = parser.parse_args()

    if args.orientation:
        settings.orientation = args.orientation
        if args.orientation == "portrait":
            settings.video_height = settings.vertical_video_height
            settings.video_width = settings.vertical_video_width
        logging.info(f'Setting Orientation to : \
                     {str(settings.orientation)}')
        logging.info(f'Setting video_height to : \
                     {str(settings.video_height)}')
        logging.info(f'Setting video_width to : \
                    {str(settings.video_width)}')

    if args.shorts:
        logging.info("Generating Youtube Shorts Video")
        settings.orientation = "portrait"
        settings.video_height = settings.vertical_video_height
        settings.video_width = settings.vertical_video_width
        settings.max_video_length = 59
        settings.add_hashtag_shorts_to_description = True

    if args.enable_mentions:
        settings.enable_reddit_mentions = True
        logging.info('Enable Generate Videos from User Mentions')

    if args.submission_score:
        settings.minimum_submission_score = args.submission_score
        logging.info(f'Setting Reddit Post Minimum Submission Score : \
                     {str(settings.minimum_submission_score)}')

    if args.sort:
        settings.reddit_post_sort = args.sort
        logging.info(f'Setting Reddit Post Sort : \
                     {settings.reddit_post_sort}')
    if args.time:
        settings.reddit_post_time_filter = args.time
        logging.info(f'Setting Reddit Post Time Filter : \
                     {settings.reddit_post_time_filter}')

    if args.background_directory:
        logging.info(f'Setting video background directory : \
                     {args.background_directory}')
        settings.background_directory = args.background_directory

    if args.total_posts:
        logging.info(f'Total Posts to process : {str(args.total_posts)}')
        settings.total_posts_to_process = args.total_posts

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

    if args.enable_upload:
        logging.info('Upload video enabled!')
        settings.enable_upload = True

    if args.subreddits:
        logging.info('Subreddits :')
        settings.subreddits = args.subreddits.split("+")
        print(settings.subreddits)

    if args.enable_background:
        logging.info('Enabling Video Background!')
        settings.enable_background = True

    return args


if __name__ == "__main__":
    banner()
    print_version_info()
    args = get_args()
    csvwriter = CsvWriter()
    csvwriter.initialise_csv()

    submissions = []

    if args.url:
        urls = args.url.split(",")
        for url in urls:
            submissions.append(reddit.get_reddit_submission(url))

    if settings.enable_reddit_mentions:
        logging.info('Getting Reddit Mentions')
        mention_posts = reddit.get_reddit_mentions()
        for mention_post in mention_posts:
            logging.info(f'Reddit Mention : {mention_post}')
            submissions.append(reddit.get_reddit_submission(mention_post))

    reddit_posts = reddit.posts()
    for reddit_post in reddit_posts:
        submissions.append(reddit_post)

    if submissions:
        process_submissions(submissions)
