"""Commands that can be executed by the rybo CLI utility."""

import logging
from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List

from praw.models import Submission

import rybo.config.settings as settings
import rybo.thumbnail.thumbnail as thumbnail
import rybo.video_generation.video as vid
from rybo.reddit import reddit
from rybo.utils.common import create_directory, safe_filename
from rybo.utils.csvmgr import CsvWriter

logger = logging.getLogger(__name__)


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


class CommandBase(ABC):
    """Base class for CLI commands."""

    def __init__(self, cli: ArgumentParser) -> None:
        """Initialise the sub-command.

        Args:
            cli: ArgParse action that will execute this command.
        """
        self._cli = cli
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def execute(self, args: Namespace) -> None:
        """Execute the command.

        Args:
            args: User provided CLI arguments.
        """
        pass


class RyboCommand(CommandBase):
    """Top level command for the rybo utility.

    _See Also_:
        [CommandBase][zfr.commands.CommandBase]
    """

    def execute(self, args: Namespace) -> None:
        """Execute the command.

        This will simply display help information, as the ```FolderCommand```
        command acts as a wrapper for sub-commands used to create/update
        Zephyr folders.

        Args:
            args: User provided CLI arguments.
        """
        csvwriter: CsvWriter = CsvWriter()
        csvwriter.initialise_csv()

        submissions: List[Submission] = []

        if args.url:
            urls: List[str] = args.url.split(",")
            for url in urls:
                submissions.append(
                    reddit.get_reddit_submission(
                        url=url,
                        client_id=args.reddit["client_id"],
                        client_secret=args.reddit["client_secret"],
                    )
                )
        else:
            if settings.enable_reddit_mentions:
                logger.info("Getting Reddit Mentions")
                mention_posts = reddit.get_reddit_mentions(
                    client_id=args.reddit["client_id"],
                    client_secret=args.reddit["client_secret"],
                )
                for mention_post in mention_posts:
                    logger.info("Reddit Mention : %s", mention_post)
                    submissions.append(
                        reddit.get_reddit_submission(
                            url=mention_post,
                            client_id=args.reddit["client_id"],
                            client_secret=args.reddit["client_secret"],
                        )
                    )

            reddit_posts: List[Submission] = reddit.posts(
                client_id=args.reddit["client_id"],
                client_secret=args.reddit["client_secret"],
            )
            for reddit_post in reddit_posts:
                submissions.append(reddit_post)

            submissions = reddit.get_valid_submissions(submissions)

        if submissions:
            self._process_submissions(
                submissions=submissions,
                csvwriter=csvwriter,
                thumbnail_only=args.thumbnail_only,
                username=args.reddit["username"],
                password=args.reddit["password"],
            )

    def _process_submissions(
        self,
        username: str,
        password: str,
        submissions: List[Submission],
        csvwriter: CsvWriter,
        thumbnail_only: bool = False,
    ) -> None:
        """Prepare multiple reddit posts for conversion into YouTube videos.

        Args:
            submissions: A list of zero or more Reddit posts to be converted.
            csvwriter: Helper object used to manage CSV files.
            thumbnail_only: `True` to only generate a thumbnail and skip generating a
                video, ottherwise `False` (default: False)
            username: Reddit username.
            password: Reddit password.
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
                logger.info(f"Final video already processed : {submission.id}")
            else:
                self._process_submission(
                    submission=submission,
                    thumbnail_only=thumbnail_only,
                    username=username,
                    password=password,
                )
                post_count += 1
                if post_count >= post_total:
                    logger.info("Reached post count total!")
                    break

    def _process_submission(
        self,
        username: str,
        password: str,
        submission: Submission,
        thumbnail_only: bool = False,
    ) -> None:
        """Prepare a reddit post for conversion into a YouTube video.

        Args:
            submission: The Reddit post to be converted into to a video.
            thumbnail_only: `True` to only generate a thumbnail and skip generating a
                video, ottherwise `False` (default: False)
            username: Reddit username.
            password: Reddit password.
        """
        logger.info("===== PROCESSING SUBMISSION =====")
        logger.info(
            f"{str(submission.id)}, {str(submission.score)}, \
                {str(submission.num_comments)}, \
                {len(submission.selftext)}, \
                {submission.subreddit_name_prefixed}, \
                {submission.title}"
        )
        video: Video = Video(submission)
        title_path: str = safe_filename(submission.title)

        # Create Video Directories
        video.folder_path: str = str(
            Path(settings.videos_directory, f"{submission.id}_{title_path}")
        )

        create_directory(video.folder_path)

        video.video_filepath: Path = Path(video.folder_path, "final.mp4")

        if video.video_filepath.exists():
            logger.info(f"Final video already compiled : {video.video_filepath}")
        else:
            # Generate Thumbnail
            thumbnails: List[Path] = thumbnail.generate(
                video_directory=str(video.folder_path),
                subreddit=submission.subreddit_name_prefixed,
                title=submission.title,
                number_of_thumbnails=settings.number_of_thumbnails,
            )

            if thumbnails:
                video.thumbnail_path = thumbnails[0]

            if thumbnail_only:
                logger.info("Generating Thumbnail only skipping video compile!")
            else:
                vid.create(
                    video_directory=video.folder_path,
                    post=submission,
                    thumbnails=thumbnails,
                    username=username,
                    password=password,
                )
