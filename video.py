import logging 

logging.basicConfig(level=logging.INFO)

def print_post(post):
    logging.info('Creating Video')
    logging.info("SubReddit : " + post.subreddit_name_prefixed)
    logging.info("Title     : " + post.title)
    logging.info("Score     : " + str(post.score))
    logging.info("ID        : " + str(post.id))
    logging.info("URL       : " + post.url)

class Video():
    title = ""
    
def create(post):
    logging.info('Video Create Post')
    print_post(post)
