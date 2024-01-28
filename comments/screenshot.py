"""Take screenshots of Reddit comments."""
import json
import os
import re
from io import TextIOWrapper
from pathlib import Path
from typing import List
import time

from playwright.sync_api import ViewportSize, sync_playwright
from praw.models import Comment
from rich.progress import track

import config.auth as auth
import config.settings as settings

storymode = False


def safe_filename(text: str):
    """Replace spaces with an underscore.

    Args:
        text: Filename to be sanitized.

    Returns:
        A sanitized filename, where spaces have been replaced with underscores.
    """
    text = text.replace(" ", "_")
    return "".join([c for c in text if re.match(r"\w", c)])[:50]

def is_new_layout(page):
    page.wait_for_selector('html')
    return 'is-shredtop-pdp' in page.eval_on_selector('html', '(htmlElement) => htmlElement.className')

def download_screenshots_of_reddit_posts(
    accepted_comments: List[Comment], url: str, video_directory: Path
) -> None:
    """Download screenshots of reddit posts as seen on the web.

    Downloads to `assets/temp/png`.

    Args:
        accepted_comments: List of comments to be included in the video.
        url: URL of the Reddit content to be screenshotted.
        video_directory: Path where the screenshots will be saved.
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
        ua = "Mozilla/5.0 (Linux; Android 8.0.0; MI 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Mobile Safari/537.36"
        context = browser.new_context(user_agent=ua)
        context.set_default_timeout(settings.comment_screenshot_timeout)
        if settings.theme == "dark":
            cookie_file: TextIOWrapper = open(
                f"{os.getcwd()}/comments/cookie-dark-mode.json", encoding="utf-8"
            )
        else:
            cookie_file: TextIOWrapper = open(
                f"{os.getcwd()}/comments/cookie-light-mode.json", encoding="utf-8"
            )

        # Get the thread screenshot
        page = context.new_page()

        page.goto("https://www.reddit.com/login")

        #time.sleep(5)
        # Wait for the page to finish loading
        page.wait_for_load_state("load")

        # Check if the first set of selectors exist and fill in the username and password.
        if page.query_selector("#loginUsername"):
            page.type("#loginUsername", auth.praw_username)
            page.type("#loginPassword", auth.praw_password)
            page.wait_for_selector('button[type="submit"]')
            page.click('button[type="submit"]')
            page.wait_for_url("https://www.reddit.com/")
        # If the first set of selectors don't exist, try the second set.
        elif page.query_selector("#login-username"):
            page.type("#login-username", auth.praw_username)
            page.type("#login-password", auth.praw_password)
            # Wait for the button to be visible
            button_selector = 'button.login'
            page.wait_for_selector(button_selector, state="visible")

            # Click the button
            page.click(button_selector)
            page.wait_for_url("https://www.reddit.com/")
        else:
            # Print the HTML content if the selectors are not found.
            print("Username and password fields not found. Printing HTML:")
            print(page.content())



        current_url = page.url
        if current_url == "https://www.reddit.com/":
            print("Login successful!")
        else:
            print("Login failed.")

        cookies = json.load(cookie_file)
        context.add_cookies(cookies)  # load preference cookies

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

        # Determine the Reddit UI Layout
        new_reddit_ui_layout=is_new_layout(page)

        if storymode:
            page.locator('[data-click-id="text"]').screenshot(
                path=f"assets/temp/{id}/png/story_content.png"
            )
        else:
            for _idx, comment in enumerate(
                track(accepted_comments, "Downloading screenshots...")
            ):
                comment_path: Path = Path(f"{video_directory}/comment_{comment.id}.png")

                if comment_path.exists():
                    print(f"Comment Screenshot already downloaded : {comment_path}")
                else:
                    if page.locator('[data-testid="content-gate"]').is_visible():
                        page.locator('[data-testid="content-gate"] button').click()

                    page.goto(f"https://reddit.com{comment.permalink}", timeout=0)

                    if new_reddit_ui_layout:
                        #print(f"https://reddit.com{comment.permalink}")
                        # Wait for the shreddit-comment to be present on the page
                        page.wait_for_selector('shreddit-comment')

                        selector = f'shreddit-comment[thingid="t1_{comment.id}"]'
                        entry_element = page.wait_for_selector(selector)

                        # Check if the has-children attribute exists on the shreddit-comment element
                        collapsed_attribute_exists = page.eval_on_selector(
                            selector,
                            '(comment) => comment.hasAttribute("collapsed")'
                        )

                        # Check if the has-children attribute exists on the shreddit-comment element
                        children_attribute_exists = page.eval_on_selector(
                            selector,
                            '(comment) => comment.hasAttribute("has-children")'
                        )

                        if collapsed_attribute_exists:
                            # Expanding Collapsed Comment
                            button_selector = f'{selector} details summary div button'
                            page.wait_for_selector(button_selector)
                            page.click(button_selector)
                            print(f"Expanded the collapsed shreddit-comment with thingid t1_{comment.id}.")

                        if children_attribute_exists:
                            #print("Collapsing comment thread")
                            comment_fold_button_selector = f'#comment-fold-button'
                            page.wait_for_selector(comment_fold_button_selector)
                            page.click(comment_fold_button_selector)


                        # Check if the element exists before taking a screenshot
                        if entry_element.is_visible():
                            entry_element.screenshot(path=comment_path)
                    else:
                        page.locator(f"#t1_{comment.id}").screenshot(path=comment_path)


            print("Screenshots downloaded Successfully.")


def download_screenshot_of_reddit_post_title(url: str, video_directory: Path) -> None:
    """Download screenshots of reddit posts as seen on the web.

    Downloads to `assets/temp/png`.

    Args:
        url: URL to take a screenshot of.
        video_directory: Path to save the screenshots to.
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
