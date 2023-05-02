"""Upload a single video to YouTube."""
import logging
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from pathlib import Path

from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo
from simple_youtube_api.youtube_video import YouTubeVideo

import config.settings as settings

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)


@dataclass
class Video:
    """A video to be uploaded to YouTube."""

    filepath: Path = field(default_factory=Path)
    title: str = field(default_factory=str)
    thumbnail: Path = field(default_factory=Path)
    description: str = "This is my videos description"


def publish(video: Video) -> None:
    """Upload a video to YouTube.

    Args:
        video: Metadata describing the video to be uploaded.
    """
    logging.info("========== Uploading Video To Youtube ==========")
    logging.info("video.filepath  : %s", video.filepath)
    logging.info("video.title     : %s", video.title)
    logging.info("video.thumbnail : %s", video.thumbnail)

    # loggin into the channel
    channel: Channel = Channel()
    channel.login("client_secret.json", "credentials.storage")

    # setting up the video that is going to be uploaded
    youtube_upload: LocalVideo = LocalVideo(file_path=video.filepath)

    # setting snippet
    youtube_upload.set_title(video.title[0:99])
    youtube_upload.set_description(video.description[0:4999])
    youtube_upload.set_tags(["reddit", "tts"])
    youtube_upload.set_category("gaming")
    youtube_upload.set_default_language("en-US")

    # setting status
    youtube_upload.set_embeddable(True)
    youtube_upload.set_license("creativeCommon")
    youtube_upload.set_privacy_status(settings.youtube_privacy_status)
    youtube_upload.set_public_stats_viewable(True)

    # setting thumbnail
    youtube_upload.set_thumbnail_path(video.thumbnail)

    try:
        # uploading video and printing the results
        uploaded_video: YouTubeVideo = channel.upload_video(youtube_upload)
        print(uploaded_video.id)
        print(uploaded_video)
    except Exception as e:
        logging.info("Error uploading video : %s", video.title)
        print(e)


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--filepath",
        default="C:\\src\\ttsvibelounge\\test_video.mp4",
        help="Specify path to video file",
    )
    parser.add_argument(
        "--title",
        default="What's the best non-alcoholic way to make \
                 a party crazy and fun? (r/AskReddit)",
        help="Video Title",
    )
    parser.add_argument(
        "--thumbnail",
        default="C:\\src\\ttsvibelounge\\test_thumbnail.png",
        help="Video Thumbnail Image",
    )
    args: Namespace = parser.parse_args()

    video: Video = Video(
        filepath=args.filepath, title=args.title, thumbnail=args.thumbnail
    )

    publish(video)
