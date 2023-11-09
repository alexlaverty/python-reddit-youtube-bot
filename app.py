"""Main entrypoint for the bot."""
import logging
import os
import platform
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

from praw.models import Submission

import config.settings as settings
import reddit.reddit as reddit
import thumbnail.thumbnail as thumbnail
import video_generation.video as vid
from csvmgr import CsvWriter
from utils.common import create_directory, safe_filename

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log", "w", "utf-8"), logging.StreamHandler()],
)


class Video:
    """Metadata used to splice content together to form a video."""

    def __init__(self, submission):
        """Initialize a Video instance.

        Args:
            submission: The Reddit post to be converted into a video.
        """
        self.submission = submission
        self.comments = []
        self.clips = []
        self.background = None
        self.music = None
        self.thumbnail_path = None
        self.folder_path = None
        self.video_filepath = None


def process_submissions(submissions: List[Submission]) -> None:
    """Prepare multiple reddit posts for conversion into YouTube videos.

    Args:
        submissions: A list of zero or more Reddit posts to be converted.
    """
    post_total: int = settings.total_posts_to_process
    post_count: int = 0

    for submission in submissions:
        title_path: str = safe_filename(submission.title)
        folder_path: Path = Path(
            settings.videos_directory, f"{submission.id}_{title_path}"
        )
        video_filepath: Path = Path(folder_path, "final.mp4")
        if video_filepath.exists() or csvwriter.is_uploaded(submission.id):
            print(f"Final video already processed : {submission.id}")
        else:
            process_submission(submission)
            post_count += 1
            if post_count >= post_total:
                print("Reached post count total!")
                break


def process_submission(submission: Submission) -> None:
    """Prepare a reddit post for conversion into a YouTube video.

    Args:
        submission: The Reddit post to be converted into to a video.
    """
    print("===== PROCESSING SUBMISSION =====")
    print(
        f"{str(submission.id)}, {str(submission.score)}, \
            {str(submission.num_comments)}, \
            {len(submission.selftext)}, \
            {submission.subreddit_name_prefixed}, \
            {submission.title}"
    )
    video: Video = Video(submission)
    title_path: str = safe_filename(submission.title)

    if settings.background_music_path:
        video.music = settings.background_music_path

    # Create Video Directories
    video.folder_path: str = str(
        Path(settings.videos_directory, f"{submission.id}_{title_path}")
    )

    create_directory(video.folder_path)

    video.video_filepath = str(Path(video.folder_path, "final.mp4"))

    if os.path.exists(video.video_filepath):
        print(f"Final video already compiled : {video.video_filepath}")
    else:
        # Generate Thumbnail

        thumbnails: List[Path] = thumbnail.generate(
            video_directory=video.folder_path,
            subreddit=submission.subreddit_name_prefixed,
            title=submission.title,
            number_of_thumbnails=settings.number_of_thumbnails,
        )

        if thumbnails:
            video.thumbnail_path = thumbnails[0]

        if args.thumbnail_only:
            print("Generating Thumbnail only skipping video compile!")
        else:
            vid.create(
                video_directory=video.folder_path,
                post=submission,
                thumbnails=thumbnails,
            )


def banner():
    """Display the CLIs banner."""
    print("##### YOUTUBE REDDIT BOT #####")


def print_version_info():
    """Display basic environment information."""
    print(f"OS Version     : {platform.system()} {platform.release()}")
    print(f"Python Version : {sys.version}")


def get_args() -> Namespace:
    """Generate arguments supported by the CLI utility.

    Returns:
        An argparse Namepsace containing the supported CLI parameters.
    """
    parser: ArgumentParser = ArgumentParser()

    parser.add_argument(
        "--enable-mentions",
        action="store_true",
        help="Check reddit account for u mentions",
    )

    parser.add_argument(
        "--enable-saved",
        action="store_true",
        help="Check reddit account for saved posts",
    )

    parser.add_argument(
        "--disable-selftext",
        action="store_true",
        help="Disable selftext video generation",
    )

    parser.add_argument(
        "--voice-engine",
        help="Specify which text to speech engine to use",
        choices=["polly", "balcon", "gtts", "tiktok", "edge-tts", "streamlabspolly"],
    )

    parser.add_argument(
        "-c",
        "--comment-style",
        help="Specify text based or reddit image comments",
        choices=["text", "reddit"],
    )

    parser.add_argument(
        "-l", "--video-length", help="Set how long you want the video to be", type=int
    )

    parser.add_argument(
        "-n", "--enable-nsfw", action="store_true", help="Allow NSFW Content"
    )

    parser.add_argument(
        "-o", "--disable-overlay", action="store_true", help="Disable video overlay"
    )

    parser.add_argument(
        "-s",
        "--story-mode",
        action="store_true",
        help="Generate video for post title and selftext only,\
                            disables user comments",
    )

    parser.add_argument(
        "-t",
        "--thumbnail-only",
        action="store_true",
        help="Generate thumbnail image only",
    )

    parser.add_argument(
        "-p",
        "--enable-upload",
        action="store_true",
        help="Upload video to youtube, \
                             requires client_secret.json and \
                             credentials.storage to be valid",
    )

    parser.add_argument(
        "-u",
        "--url",
        help="Specify Reddit post url, \
                        seperate with a comma for multiple posts.",
    )

    parser.add_argument("--subreddits", help="Specify Subreddits, seperate with +")

    parser.add_argument(
        "-b",
        "--enable-background",
        action="store_true",
        help="Enable video backgrounds",
    )

    parser.add_argument(
        "-m",
        "--enable-background-music",
        action="store_true",
        help="Enable background music",
    )

    parser.add_argument(
        "--background-music-path",
        help="Path to background music file"
    )

    parser.add_argument(
        "--thumbnail-image-path",
        help="Path to thumbnail image file"
    )


    parser.add_argument("--total-posts", type=int, help="Enable video backgrounds")

    parser.add_argument(
        "--submission-score", type=int, help="Minimum submission score threshold"
    )

    parser.add_argument(
        "--background-directory", help="Folder path to video backgrounds"
    )

    parser.add_argument("--sort", choices=["top", "hot"], help="Sort Reddit posts by")

    parser.add_argument(
        "--time",
        choices=["all", "day", "hour", "month", "week", "year"],
        default="day",
        help="Filter by time",
    )

    parser.add_argument(
        "--orientation",
        choices=["landscape", "portrait"],
        default="landscape",
        help="Sort Reddit posts by",
    )

    parser.add_argument(
        "--shorts", action="store_true", help="Generate Youtube Shorts Video"
    )

    args = parser.parse_args()

    if args.orientation:
        settings.orientation = args.orientation
        if args.orientation == "portrait":
            settings.video_height = settings.vertical_video_height
            settings.video_width = settings.vertical_video_width

    if args.shorts:
        logging.info("Generating Youtube Shorts Video")
        settings.shorts_mode_enabled = True
        settings.orientation = "portrait"
        settings.video_height = settings.vertical_video_height
        settings.video_width = settings.vertical_video_width
        settings.add_hashtag_shorts_to_description = True
        settings.text_fontsize = 60
        settings.clip_margin = 100
        settings.clip_margin_top = settings.vertical_video_height / 3
        settings.reddit_comment_width = 0.90
        settings.commentstyle = "text"
        settings.enable_background = True
        settings.max_video_length = 59

    if args.enable_mentions:
        settings.enable_reddit_mentions = True
        logging.info("Enable Generate Videos from User Mentions")

    if args.enable_saved:
        settings.enable_reddit_saved = True
        logging.info("Enable Generate Videos from Saved Posts")


    if args.submission_score:
        settings.minimum_submission_score = args.submission_score
        logging.info(
            "Setting Reddit Post Minimum Submission Score : %s",
            settings.minimum_submission_score,
        )

    if args.sort:
        settings.reddit_post_sort = args.sort
        logging.info("Setting Reddit Post Sort : %s", settings.reddit_post_sort)
    if args.time:
        settings.reddit_post_time_filter = args.time
        logging.info(
            "Setting Reddit Post Time Filter : %s", settings.reddit_post_time_filter
        )

    if args.background_directory:
        logging.info(
            "Setting video background directory : %s", args.background_directory
        )
        settings.background_directory = args.background_directory

    if args.enable_background_music:
        # Enable background music, selects random music file from assets/music
        logging.info(
            "Enable Background Music : True",
        )
        settings.enable_background_music = True

    if args.background_music_path:
        # If you want specific music use this to specify the path to the mp3 file.
        logging.info(
            "Specify background music file : %s", args.background_music_path
        )
        settings.enable_background_music = True
        settings.background_music_path = args.background_music_path

    if args.thumbnail_image_path:
        # If you want a specific thumbnail image specify the path using this arg.
        logging.info(
            "Settings thumbnail image path : %s", args.thumbnail_image_path
        )
        settings.thumbnail_image_path = args.thumbnail_image_path

    if args.total_posts:
        logging.info("Total Posts to process : %s", args.total_posts)
        settings.total_posts_to_process = args.total_posts

    if args.comment_style:
        logging.info("Setting comment style to : %s", args.comment_style)
        settings.commentstyle = args.comment_style

    if args.voice_engine:
        logging.info("Setting speech engine to : %s", args.voice_engine)
        settings.voice_engine = args.voice_engine

    if args.video_length:
        logging.info("Setting video length to : %s seconds", args.video_length)
        settings.max_video_length = args.video_length

    if args.disable_overlay:
        logging.info("Disabling Video Overlay")
        settings.enable_overlay = False

    if args.enable_nsfw:
        logging.info("Enable NSFW Content")
        settings.enable_nsfw_content = True

    if args.story_mode:
        logging.info("Story Mode Enabled!")
        settings.enable_comments = False

    if args.disable_selftext:
        logging.info("Disabled SelfText!")
        settings.enable_selftext = False

    if args.enable_upload:
        logging.info("Upload video enabled!")
        settings.enable_upload = True

    if args.subreddits:
        logging.info("Subreddits :")
        settings.subreddits = args.subreddits.split("+")
        print(settings.subreddits)

    if args.enable_background:
        logging.info("Enabling Video Background!")
        settings.enable_background = True

    logging.info("Setting Orientation to : %s", settings.orientation)
    logging.info("Setting video_height to : %s", settings.video_height)
    logging.info("Setting video_width to : %s", settings.video_width)
    logging.info("Setting clip_margin to : %s", settings.clip_margin)
    logging.info("Setting reddit_comment_width to : %s", settings.reddit_comment_width)

    return args


if __name__ == "__main__":
    banner()
    print_version_info()
    args: Namespace = get_args()
    csvwriter: CsvWriter = CsvWriter()
    csvwriter.initialise_csv()

    submissions: List[Submission] = []

    if args.url:
        urls = args.url.split(",")
        for url in urls:
            submissions.append(reddit.get_reddit_submission(url))
    else:
        if settings.enable_reddit_mentions:
            logging.info("Getting Reddit Mentions")
            mention_posts = reddit.get_reddit_mentions()
            for mention_post in mention_posts:
                logging.info("Reddit Mention : %s", mention_post)
                submissions.append(reddit.get_reddit_submission(mention_post))

        if settings.enable_reddit_saved:
            logging.info("Getting Reddit Saved Posts")
            saved_posts = reddit.get_reddit_saved_posts()
            for saved_post in saved_posts:
                logging.info("Reddit Saved Post : %s", saved_post)
                submissions.append(reddit.get_reddit_submission(saved_post))

        reddit_posts: List[Submission] = reddit.posts()
        for reddit_post in reddit_posts:
            submissions.append(reddit_post)

        submissions = reddit.get_valid_submissions(submissions)

    if submissions:
        process_submissions(submissions)
