from pathlib import Path
from playwright.async_api import async_playwright  # pylint: disable=unused-import
from playwright.sync_api import sync_playwright, ViewportSize
from rich.progress import track
from typing import Dict
import config.settings as settings
import json
import os
import re

storymode = False


def safe_filename(text):
    text = text.replace(" ", "_")
    return "".join([c for c in text if re.match(r"\w", c)])[:50]


def download_screenshots_of_reddit_posts(accepted_comments, url, video_directory):
    """Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png

    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_num (int): Number of screenshots to download
    """
    print("Downloading screenshots of reddit posts...")
    # id = re.sub(r"[^\w\s-]", "", reddit_object.meta.id)
    # # ! Make sure the reddit screenshots folder exists
    # title_path = safe_filename(reddit_object.title)
    # folder_path = str(Path(settings.videos_directory,f"{id}_{title_path}"))
    # #Path(f"assets/temp/{id}/png").mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        print("Launching Headless Browser...")

        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.set_default_timeout(settings.comment_screenshot_timeout)
        if settings.theme == "dark":
            cookie_file = open(
                f"{os.getcwd()}/comments/cookie-dark-mode.json", encoding="utf-8"
            )
        else:
            cookie_file = open(
                f"{os.getcwd()}/comments/cookie-light-mode.json", encoding="utf-8"
            )
        cookies = json.load(cookie_file)
        context.add_cookies(cookies)  # load preference cookies
        # Get the thread screenshot
        page = context.new_page()
        page.goto(url, timeout=0)
        page.set_viewport_size(ViewportSize(width=1920, height=1080))
        if page.locator('[data-testid="content-gate"]').is_visible():
            # This means the post is NSFW and requires to click the proceed button.

            print("Post is NSFW. You are spicy...")
            page.locator('[data-testid="content-gate"] button').click()
            page.wait_for_load_state()  # Wait for page to fully load

            if page.locator('[data-click-id="text"] button').is_visible():
                page.locator(
                    '[data-click-id="text"] button'
                ).click()  # Remove "Click to see nsfw" Button in Screenshot

        if storymode:
            page.locator('[data-click-id="text"]').screenshot(
                path=f"assets/temp/{id}/png/story_content.png"
            )
        else:
            page.locator('[data-test-id="post-content"]').screenshot(
                path=f"{video_directory}/title.png"
            )
            for idx, comment in enumerate(
                track(accepted_comments, "Downloading screenshots...")
            ):
                comment_path = f"{video_directory}/comment_{comment.id}.png"

                if os.path.exists(comment_path):
                    print(f"Comment Screenshot already downloaded : {comment_path}")
                else:
                    if page.locator('[data-testid="content-gate"]').is_visible():
                        page.locator('[data-testid="content-gate"] button').click()

                    page.goto(f"https://reddit.com{comment.permalink}", timeout=0)

                    try:
                        page.locator(f"#t1_{comment.id}").screenshot(path=comment_path)
                    except Exception:
                        pass

            print("Screenshots downloaded Successfully.")


def download_screenshot_of_reddit_post_title(url, video_directory):
    """Downloads screenshots of reddit posts as seen on the web. Downloads to assets/temp/png

    Args:
        reddit_object (Dict): Reddit object received from reddit/subreddit.py
        screenshot_num (int): Number of screenshots to download
    """
    print("Downloading screenshots of reddit title...")
    print(url)
    with sync_playwright() as p:
        print("Launching Headless Browser...")

        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        if settings.theme == "dark":
            cookie_file = open(
                f"{os.getcwd()}/comments/cookie-dark-mode.json", encoding="utf-8"
            )
        else:
            cookie_file = open(
                f"{os.getcwd()}/comments/cookie-light-mode.json", encoding="utf-8"
            )
        cookies = json.load(cookie_file)
        context.add_cookies(cookies)  # load preference cookies
        # Get the thread screenshot
        page = context.new_page()
        page.goto(url, timeout=0)
        page.set_viewport_size(ViewportSize(width=1920, height=1080))
        if page.locator('[data-testid="content-gate"]').is_visible():
            # This means the post is NSFW and requires to click the proceed button.

            print("Post is NSFW. You are spicy...")
            page.locator('[data-testid="content-gate"] button').click()
            page.wait_for_load_state()  # Wait for page to fully load

            if page.locator('[data-click-id="text"] button').is_visible():
                page.locator(
                    '[data-click-id="text"] button'
                ).click()  # Remove "Click to see nsfw" Button in Screenshot

        # page.locator('[data-click-id="text"]').screenshot(
        #     path=f"{video_directory}/story_content.png"
        # )

        page.locator('[data-test-id="post-content"]').screenshot(
            path=f"{video_directory}/title.png"
        )

        print("Title Screenshot downloaded Successfully.")
