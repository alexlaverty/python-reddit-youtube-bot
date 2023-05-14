"""Helpers used to retreive, filter and process reddit posts."""
import base64
import logging
import re
from typing import List

import praw
from praw.models import Submission

from rybo.config import settings

logger = logging.getLogger(__name__)


def get_reddit_mentions(client_id: str, client_secret: str) -> List[str]:
    """Get a list of comments where ttvibe has been mentioned.

    Args:
        client_id: Client ID used to access the Reddit API.
        client_secret: Client secret used to access the Reddit API.

    Returns:
        A list containing zero or more URLs where ttvibe has been mentioned.
    """
    r: praw.Reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 \
                    Firefox/112.0",
    )

    mention_urls: List[str] = []
    for mention in r.inbox.mentions(limit=None):
        post_url: str = re.sub(
            rf"/{mention.id}/\?context=\d", "", mention.context, flags=re.IGNORECASE
        )
        mention_urls.append(f"https://www.reddit.com{post_url}")

    return mention_urls


def get_reddit_submission(url: str, client_id: str, client_secret: str) -> Submission:
    """Get a single Reddit post.

    Args:
        url: URL to the post to be retrieved.
        client_id: Client ID used to access the Reddit API.
        client_secret: Client secret used to access the Reddit API.

    Returns:
        The post contents.
    """
    r: praw.Reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 \
                    Firefox/112.0",
    )

    submission: Submission = r.submission(url=url)
    return submission


def get_reddit_submissions(client_id: str, client_secret: str) -> List[Submission]:
    """Get the latest Reddit posts.

    Posts will be retrieved according to the sort order defined in settings.

    Args:
        client_id: Client ID used to access the Reddit API.
        client_secret: Client secret used to access the Reddit API.

    Returns:
        A list containing zero or more Reddit posts.
    """
    r: praw.Reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101\
                    Firefox/112.0",
    )

    if settings.subreddits:
        subreddits: str = "+".join(settings.subreddits)
    else:
        subreddits: str = "all"
    logger.info("Retrieving posts from subreddit %s", subreddits)

    # Get Reddit Hot Posts
    if settings.reddit_post_sort == "hot":
        submissions: List[Submission] = r.subreddit(subreddits).hot(
            limit=settings.submission_limit
        )

    if settings.reddit_post_sort == "top":
        # Get Reddit Top Posts
        # "all", "day", "hour", "month", "week", or "year" (default: "all"

        submissions: List[Submission] = r.subreddit(subreddits).top(
            limit=settings.submission_limit,
            time_filter=settings.reddit_post_time_filter,
        )

    return submissions


def get_valid_submissions(submissions: List[Submission]) -> List[Submission]:
    """Get Reddit posts deemed suitable for use as source material.

    Args:
        submissions: List of Reddit posts to validate.

    Returns:
        A list of zero or more Reddit posts that are suitable for use as source
        material, to generate a video.
    """
    valid_submissions: List[Submission] = []
    logger.info("===== Retrieving valid Reddit submissions =====")
    logger.info("ID, SCORE, NUM_COMMENTS, LEN_SELFTEXT, SUBREDDIT, TITLE")
    for submission in submissions:
        if is_valid_submission(submission):
            msg: str = ", ".join(
                [
                    str(submission.id),
                    str(submission.score),
                    str(submission.num_comments),
                    str(len(submission.selftext)),
                    submission.subreddit_name_prefixed,
                    submission.title,
                ]
            )
            logger.info(msg)
            valid_submissions.append(submission)

    return valid_submissions


def is_valid_submission(submission: Submission) -> bool:
    """Determine whether a Reddit post is worth turning in to a video.

    A post is deemed "worthy", if:
        - It isn't stickied.
        - It was submitted by ttvibe.
        - The posts title is within the min/max ranges defined in settings.
        - The post hasn't been flagged as NSFW.
        - The post doesn't contain banned keywords.
        - The post wasn't made in a subreddit that has been added to the
          ignore list.
        - The submission score is within range.
        - The length of the post content is less than the configured maximum
          length.
        - The post has more than a minimum number of comments.
        - The post is not an update on a previous post.
        - The post doesn't contain 'covid' or 'vaccine' in the title, as these
          tend to trigger Youtube strikes. Censorship is double-plus good...

    Args:
        submission: A single Reddit post.

    Returns:
        `True` if the Reddit post is deemed worthy of turning in to a video,
        otherwise returns `False`.
    """
    if submission.stickied:
        return False

    if not settings.enable_screenshot_title_image and not submission.is_self:
        return False

    if (
        len(submission.title) < settings.title_length_minimum
        or len(submission.title) > settings.title_length_maximum
    ):
        return False

    if not settings.enable_nsfw_content:
        if submission.over_18:
            logger.info("Skipping NSFW...")
            return False
        for banned_keyword in (
            base64.b64decode(settings.banned_keywords_base64.encode("ascii"))
            .decode("ascii")
            .split(",")
        ):
            if banned_keyword in submission.title.lower():
                logger.info(
                    f"{submission.title} \
                    <-- Skipping post, title contains banned keyword!"
                )
                return False

    if submission.subreddit_name_prefixed in settings.subreddits_excluded:
        return False

    if submission.score < settings.minimum_submission_score:
        logger.info(f"{submission.title} <-- Submission score too low!")
        return False

    if len(submission.selftext) > settings.maximum_length_self_text:
        return False

    if (
        settings.enable_comments
        and submission.num_comments < settings.minimum_num_comments
    ):
        logger.info(f"{submission.title} <-- Number of comments too low!")
        return False

    if "update" in submission.title.lower():
        return False

    if "covid" in submission.title.lower() or "vaccine" in submission.title.lower():
        logger.info(
            f"{submission.title} <-- Youtube Channel Strikes if Covid content...!"
        )
        return False

    return True


def posts(client_id: str, client_secret: str) -> List[Submission]:
    """Get a list of available Reddit posts.

    Args:
        client_id: Client ID used to access the Reddit API.
        client_secret: Client secret used to access the Reddit API.

    Returns:
        A list of zero or more Reddit submissions.
    """
    submissions: List[Submission] = get_reddit_submissions(
        client_id=client_id, client_secret=client_secret
    )
    return submissions
