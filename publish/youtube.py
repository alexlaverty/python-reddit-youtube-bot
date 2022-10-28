import argparse
import logging
from argparse import ArgumentError
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.file_detector import LocalFileDetector
from selenium.webdriver.firefox.options import Options
from time import sleep

from publish.login import confirm_logged_in, login_using_cookie_file
from publish.upload import upload_file

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

    # # Docker Remote
    # driver = webdriver.Remote(
    #     command_executor="http://firefox:4444/wd/hub",
    #     desired_capabilities=DesiredCapabilities.FIREFOX,
    # )

    # Firefox Local
    options = Options()
    options.headless = True
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0")
    firefox_profile.update_preferences()
    #driver = webdriver.Firefox(firefox_profile,firefox_binary='C:\\Program Files\\Mozilla Firefox\\firefox.exe')

    options = Options()
    #options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_profile, options=options, firefox_binary='C:\\Program Files\\Mozilla Firefox\\firefox.exe')

    driver.set_window_size(1920, 1080)
    login_using_cookie_file(driver, cookie_file=login_cookies)
    driver.get("https://www.youtube.com")
    sleep(5)
    #assert "YouTube" in driver.title

    try:
        confirm_logged_in(driver)
        driver.get("https://studio.youtube.com")
        assert "Channel dashboard" in driver.title
        driver.file_detector = LocalFileDetector()
        upload_file(
            driver,
            video_path=video.filepath,
            title=video.title,
            thumbnail_path=video.thumbnail,
            description=video.description,
            kids=False
        )
    except:
        driver.close()
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath',default='C:\\src\\ttsvibelounge\\test_video.mp4', help='Specify path to video file')
    parser.add_argument('--title',default="What's the best non-alcoholic way to make a party crazy and fun? (r/AskReddit)", help='Video Title')
    parser.add_argument('--thumbnail',default='C:\\src\\ttsvibelounge\\test_thumbnail.png', help='Video Thumbnail Image')
    args = parser.parse_args()

    class Video():
        filepath = args.filepath
        title = args.title
        thumbnail = args.thumbnail
        description = "This is my videos description"

    video = Video()

    publish(video)

