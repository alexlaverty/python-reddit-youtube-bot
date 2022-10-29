import argparse
import logging
from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

login_cookies="cookies.json"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])

def publish(video):
    logging.info('========== Uploading Video To Youtube ==========')
    logging.info(f'video.filepath  : {video.filepath}')
    logging.info(f'video.title     : {video.title}')
    logging.info(f'video.thumbnail : {video.thumbnail}')

    # loggin into the channel
    channel = Channel()
    channel.login("client_secret.json", "credentials.storage")

    # setting up the video that is going to be uploaded
    youtube_upload = LocalVideo(file_path=video.filepath)

    # setting snippet
    youtube_upload.set_title(video.title)
    youtube_upload.set_description(video.description)
    youtube_upload.set_tags(["reddit", "tts"])
    youtube_upload.set_category("gaming")
    youtube_upload.set_default_language("en-US")

    # setting status
    youtube_upload.set_embeddable(True)
    youtube_upload.set_license("creativeCommon")
    youtube_upload.set_privacy_status("public")
    youtube_upload.set_public_stats_viewable(True)

    # setting thumbnail
    youtube_upload.set_thumbnail_path(video.thumbnail)

    try:
        # uploading video and printing the results
        uploaded_video = channel.upload_video(youtube_upload)
        print(uploaded_video.id)
        print(uploaded_video)
    except:
        logging.info("ERROR UPLOADING:")
        logging.info(uploaded_video)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath',
                        default='C:\\src\\ttsvibelounge\\test_video.mp4',
                        help='Specify path to video file')
    parser.add_argument('--title',
                        default="What's the best non-alcoholic way to make a party crazy and fun? (r/AskReddit)",
                        help='Video Title')
    parser.add_argument('--thumbnail',
                        default='C:\\src\\ttsvibelounge\\test_thumbnail.png',
                        help='Video Thumbnail Image')
    args = parser.parse_args()

    class Video():
        filepath = args.filepath
        title = args.title
        thumbnail = args.thumbnail
        description = "This is my videos description"

    video = Video()

    publish(video)
