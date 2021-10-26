import praw 
import yaml
import config
import logging 
import video 

logging.basicConfig(level=logging.INFO)

r = praw.Reddit(client_id=config.praw_client_id,
                client_secret=config.praw_client_secret,
                user_agent=config.praw_user_agent)

class ttsvibelounge():
    subreddits = ['all']
    validposts = []
    videos = []
    
    def get_valid_posts(self):
        for subreddit in self.subreddits:
            for submission in r.subreddit(subreddit).top(time_filter='day'):
                if self.valid_post(submission):
                    self.validposts.append(submission)

    def valid_post(self, submission):
        if not submission.stickied and submission.is_self:
            return True
        else:
            return False


def main():
    tvl = ttsvibelounge()

    logging.info('Getting Valid Posts')
    tvl.get_valid_posts()

    logging.info('Create Videos from posts')
    for post in tvl.validposts:
        video.create(post)


if __name__ == "__main__":
    main()