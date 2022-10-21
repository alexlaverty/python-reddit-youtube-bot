import praw
import settings 
import config 
import base64

def is_valid_submission(submission):
    if submission.stickied:
        return False
    if not submission.is_self:
        return False
    if len(submission.title) < settings.title_length_minimum or len(submission.title) > settings.title_length_maximum :
        return False
    if submission.over_18 :
        return False
    for banned_keyword in base64.b64decode(settings.banned_keywords_base64.encode('ascii')).decode('ascii').split(","):
        if banned_keyword in submission.title.lower():
            print("Skipping post, title contains banned keyword!")
            return False
    if submission.subreddit_name_prefixed in settings.subreddits_excluded:
        return False
    if submission.score < settings.minimum_submission_score:
        return False
    if len(submission.selftext) > settings.maximum_length_self_text:
        return False
    if submission.num_comments < settings.minimum_num_comments:
        return False
    return True

def get_reddit_submission(url):
    r = praw.Reddit(client_id=config.praw_client_id,
                    client_secret=config.praw_client_secret,
                    user_agent=config.praw_user_agent)
    submission = r.submission(url=url)
    return submission

def get_reddit_submissions():
    r = praw.Reddit(client_id=config.praw_client_id,
                    client_secret=config.praw_client_secret,
                    user_agent=config.praw_user_agent)

    if settings.subreddits:
        subreddits = "+".join(settings.subreddits)
    else:
        subreddits = "all"
    print("Retrieving posts from subreddit :")
    print(subreddits)
    submissions = r.subreddit(subreddits).top(limit=settings.submission_limit, time_filter="day")
    return submissions

def get_valid_submissions(submissions):
    post_total = settings.total_posts_to_process
    post_count = 0
    valid_submissions = []
    print("Retrieving valid Reddit submissions...")
    print("ID, SCORE, NUM_COMMENTS, LEN_SELFTEXT, SUBREDDIT, TITLE")
    for submission in submissions:
        if post_count >= post_total:
            print("Reached post count total!")
            break
        if is_valid_submission(submission) :
            print(f"{str(submission.id)}, {str(submission.score)}, {str(submission.num_comments)}, {len(submission.selftext)}, {submission.subreddit_name_prefixed}, {submission.title}") 
            valid_submissions.append(submission)
            post_count += 1
        
    return valid_submissions

def posts():
    submissions = get_reddit_submissions()
    valid_submissions = get_valid_submissions(submissions)
    return valid_submissions
