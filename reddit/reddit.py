import praw
import config.settings as settings
import config.auth as auth
import base64
import re


def is_valid_submission(submission):
    if submission.stickied:
        return False

    if not settings.enable_screenshot_title_image and not submission.is_self:
        return False

    if (
        len(submission.title) < settings.title_length_minimum
        or len(submission.title) > settings.title_length_maximum
    ):
        f"{submission.title} <-- Does not meet title length requirements!"
        return False
    if not settings.enable_nsfw_content:
        if submission.over_18:
            print("Skipping NSFW...")
            return False
        for banned_keyword in (
            base64.b64decode(settings.banned_keywords_base64.encode("ascii"))
            .decode("ascii")
            .split(",")
        ):
            if banned_keyword in submission.title.lower():
                print(
                    f"{submission.title} <-- Skipping post, title contains banned keyword!"
                )
                return False
    if submission.subreddit_name_prefixed in settings.subreddits_excluded:
        return False
    if submission.score < settings.minimum_submission_score:
        print(
            f"{submission.title} <-- Submission score too low!"
        )
        return False
    if len(submission.selftext) > settings.maximum_length_self_text:
        return False
    if settings.enable_comments and submission.num_comments < settings.minimum_num_comments:
        print(
            f"{submission.title} <-- Number of comments too low!"
        )
        return False
    if "update" in submission.title.lower():
        return False
    if "covid" in submission.title.lower() or "vaccine" in submission.title.lower():
        print(
            f"{submission.title} <-- Youtube Channel Strikes if Covid content...!"
        )
        return False
    return True


def get_reddit_submission(url):
    r = praw.Reddit(
        client_id=auth.praw_client_id,
        client_secret=auth.praw_client_secret,
        user_agent=auth.praw_user_agent,
    )
    submission = r.submission(url=url)
    return submission


def get_reddit_mentions():
    r = praw.Reddit(
        client_id=auth.praw_client_id,
        client_secret=auth.praw_client_secret,
        user_agent=auth.praw_user_agent,
        username=auth.praw_username,
        password=auth.praw_password,
    )
    mention_urls = []
    for mention in r.inbox.mentions(limit=None):
        post_url = re.sub(f"/{mention.id}/\?context=\d", '', mention.context, flags=re.IGNORECASE)
        mention_urls.append(
            f"https://www.reddit.com{post_url}"
        )
    return mention_urls

def get_reddit_saved():
    r = praw.Reddit(
        client_id=auth.praw_client_id,
        client_secret=auth.praw_client_secret,
        user_agent=auth.praw_user_agent,
        username=auth.praw_username,
        password=auth.praw_password,
    )
    return list(r.user.me().saved(limit=None))



def get_reddit_submissions():
    r = praw.Reddit(
        client_id=auth.praw_client_id,
        client_secret=auth.praw_client_secret,
        user_agent=auth.praw_user_agent,
    )

    if settings.subreddits:
        subreddits = "+".join(settings.subreddits)
    else:
        subreddits = "all"
    print("Retrieving posts from subreddit :")
    print(subreddits)

    # Get Reddit Hot Posts
    if settings.reddit_post_sort == "hot":
        submissions = r.subreddit(subreddits)\
                       .hot(limit=settings.submission_limit)

    if settings.reddit_post_sort == "top":
        # Get Reddit Top Posts
        # "all", "day", "hour", "month", "week", or "year" (default: "all"

        submissions = r.subreddit(subreddits).top(
            limit=settings.submission_limit,
            time_filter=settings.reddit_post_time_filter
        )
    return submissions


def get_valid_submissions(submissions):
    valid_submissions = []
    print("===== Retrieving valid Reddit submissions =====")
    print("ID, SCORE, NUM_COMMENTS, LEN_SELFTEXT, SUBREDDIT, TITLE")
    for submission in submissions:
        if is_valid_submission(submission):
            print(
                f"{str(submission.id)}, {str(submission.score)}, {str(submission.num_comments)}, {len(submission.selftext)}, {submission.subreddit_name_prefixed}, {submission.title}"
            )
            valid_submissions.append(submission)

    return valid_submissions


def posts():
    submissions = get_reddit_submissions()
    return submissions
