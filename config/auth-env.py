"""Load authentication credentials from environment variables."""
import os

print("Getting Secrets from ENV's")
# Reddit Praw
praw_client_id = os.environ.get("PRAW_CLIENT_ID")
praw_client_secret = os.environ.get("PRAW_CLIENT_SECRET")
praw_user_agent = os.environ.get("PRAW_USER_AGENT")
praw_password = os.environ.get("PRAW_PASSWORD")
praw_username = os.environ.get("PRAW_USERNAME")

# Amazon Polly
aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

# Rumble
rumble_username = os.environ.get("RUMBLE_USERNAME")
rumble_password = os.environ.get("RUMBLE_PASSWORD")
