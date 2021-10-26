import praw 
import yaml

config_file = "config.yml"

stream = open(config_file, 'r')
data = yaml.safe_load(stream)

praw_client_id = data.get('praw_client_id')
praw_client_secret = data.get('praw_client_secret')
praw_user_agent = data.get('praw_user_agent')
reddit = praw.Reddit(client_id=praw_client_id,
                    client_secret=praw_client_secret,
                    user_agent=praw_user_agent)

comments = reddit.replace_more(limit=0)

for comment in comments:
    print (comment)