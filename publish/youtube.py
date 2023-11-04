"""Upload a single video to YouTube."""

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from pathlib import Path
import httplib2
import logging
import os
import random
import sys
import time

#import config.settings as settings

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)

CLIENT_SECRETS_FILE = "client_secret.json"
MAX_RETRIES = 10
MISSING_CLIENT_SECRETS_MESSAGE = "MISSING_CLIENT_SECRETS_MESSAGE"
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

@dataclass
class Video:
    """A video to be uploaded to YouTube."""

    filepath: Path = field(default_factory=Path)
    title: str = field(default_factory=str)
    thumbnail: Path = field(default_factory=Path)
    description: str = "This is my videos description"

# Call the API's thumbnails.set method to upload the thumbnail image and
# associate it with the appropriate video.
def upload_thumbnail(youtube, video_id, file):
    print("Uploading and setting Youtube Thumbnail..")
    print(f"video_id: {video_id}")
    print(f"file: {file}")
    youtube.thumbnails().set(
        videoId=video_id,
        media_body=MediaFileUpload(file)
    ).execute()

def publish(video: Video) -> None:
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("credentials.storage")
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        print("Credentials invalid...")

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

    body = dict(
        snippet=dict(
            title=video.title,
            description=video.description,
            tags=["Reddit","Australia","Aussie","Banter"],
            categoryId="24"
        ),
        status=dict(
            privacyStatus="public",
            selfDeclaredMadeForKids=False
        )
    )

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(video.filepath, chunksize=-1, resumable=True)
    )

    resumable_upload(video, youtube, insert_request)



# This method implements an exponential backoff strategy to resume a
# failed upload.


def resumable_upload(video, youtube, insert_request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print("Video id '%s' was successfully uploaded." %
                          response['id'])
                    upload_thumbnail(youtube, response['id'], video.thumbnail)
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                     e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            print(error)
            retry += 1
            if retry > MAX_RETRIES:
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            print("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--filepath",
        default="D:\\src\\aussie-banter\\videos\\13r3zri_Is_a_sausage_roll_with_tomato_sauce_for_breakfast_\\final.mp4",
        help="Specify path to video file",
    )
    parser.add_argument(
        "--title",
        default="r/AusFinance Is a sausage roll with tomato sauce for breakfast common?",
        help="Video Title",
    )
    parser.add_argument(
        "--thumbnail",
        default="D:\\src\\aussie-banter\\videos\\13r3zri_Is_a_sausage_roll_with_tomato_sauce_for_breakfast_\\thumbnail_0.png",
        help="Video Thumbnail Image",
    )
    args: Namespace = parser.parse_args()

    video: Video = Video(
        filepath=args.filepath,
        title=args.title,
        thumbnail=args.thumbnail
    )

    publish(video)