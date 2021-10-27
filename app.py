import praw 
import yaml
import config
import logging
import video 
import os


logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

r = praw.Reddit(client_id=config.praw_client_id,
                client_secret=config.praw_client_secret,
                user_agent=config.praw_user_agent)

class ttsvibelounge():
    subreddits = ['all']
    validposts = []
    videos = []
    directories = ["backgrounds","audio","output"]
    post_max = 2

    def get_valid_posts(self):
        logging.info('========== Scraping Reddit Posts =========')
        for subreddit in self.subreddits:
            logging.info('Getting Posts from subreddit : ' + subreddit)
            for submission in r.subreddit(subreddit).top(time_filter='day'):
                if self.valid_post(submission):
                    self.validposts.append(submission)

    def valid_post(self, submission):
        if not submission.stickied and submission.is_self:
            return True
        else:
            return False

    def create_directories(self):
        logging.info('Checking Directory Structure')
        for directory in self.directories:
            if not os.path.exists(directory):
                logging.info('Creating Directory : ' + directory)
                os.makedirs(directory)

def main():
    tvl = ttsvibelounge()
    tvl.create_directories()
    tvl.get_valid_posts()

    logging.info('Creating Videos from posts')
    i = 0
    for post in tvl.validposts:
        post.comments.replace_more(limit=0)
        post_video = video.create(post)
        tvl.videos.append(post_video)
        i += 1
        if i == tvl.post_max:
            break
    
    
    for v in tvl.videos:
        video.compile(v)


if __name__ == "__main__":
    main()