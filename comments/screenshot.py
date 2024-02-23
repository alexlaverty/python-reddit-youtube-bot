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

import pdb

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
    new_reddit_layout = False
    page.wait_for_selector('html')
    # Check if the element with tag name 'shreddit-app' exists on the page
    shreddit_app_element = page.locator('shreddit-app').first

    if shreddit_app_element:
        print("Element 'shreddit-app' exists on the page.")
        new_reddit_layout = True
    else:
        print("Element 'shreddit-app' exists on the page.")

    return new_reddit_layout

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
        print("Launching " + ("Headless " if settings.headless_browser else "") + "Browser...")

        browser = p.chromium.launch(headless=settings.headless_browser)
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
            frame_loc = page.frame_locator('[src^="https://www.reddit.com/account/login"]')
            username_loc = frame_loc.locator("#loginUsername").first
            password_loc = frame_loc.locator("#loginPassword").first
            button_loc = frame_loc.locator("[data-step='username-and-password'] button").first
            frame_loc_found = True
            if not (username_loc.is_visible() and password_loc.is_visible() and button_loc.is_visible()):
                frame_loc_found = False
                username_loc = page.locator("#login-username").first
                password_loc = page.locator("#login-password").first
                button_loc = page.locator("button.login").first
            if (username_loc.is_visible() and password_loc.is_visible() and button_loc.is_visible()):
                print("Username and password fields found" + (" (via frame_locator)" if frame_loc_found else "") + ". Logging in...") 
                username_loc.type(auth.praw_username)
                password_loc.type(auth.praw_password)
                button_loc.first.click()
                
                # Bypass "See Reddit in..."
                see_reddit_in_button = page.locator('#bottom-sheet button.continue').first
                if see_reddit_in_button.is_visible():
                    print("See Reddit in... [CONTINUE]")
                    see_reddit_in_button.dispatch_event('click')
                    see_reddit_in_button.wait_for(state='hidden')

                # Wait for navigation to page different from the login one
                not_login_url_regex = re.compile('^(https://www.reddit.com/)(?!login)(.*)')
                if settings.screenshot_debug:
                    try:
                        page.wait_for_url(not_login_url_regex)
                    except Exception as e:
                        print("[screenshot_debug]")
                        print(e)
                        breakpoint()
                else:
                    page.wait_for_url(not_login_url_regex)
                    
            else:
                # Print the HTML content if the selectors are not found.
                print("Username and password fields not found. Printing HTML:")
                if settings.screenshot_debug: 
                    print("[screenshot_debug]")
                    breakpoint()
                print(page.content())


        # Check if logged in (successful also if a user-drawer-button is visible)
        current_url = page.url
        # print(f"Current PageURL: {page.url}")
        user_drawer_button = page.locator("#expand-user-drawer-button").first
        # print(f"user_drawer_button.count(): {user_drawer_button.count()}")
        # breakpoint()
        if current_url == "https://www.reddit.com/" or user_drawer_button.count() == 1:
            print("Login successful!")
        else:
            print("Login failed.")
            if settings.screenshot_debug: 
                print("[screenshot_debug]")
                breakpoint()

        cookies = json.load(cookie_file)
        context.add_cookies(cookies)  # load preference cookies

        page.goto(url, timeout=0)

        #print(page.evaluate('() => document.querySelector("html").classList.toString()'))
        
        # Alternate method to try to set preferred theme
        dark_mode_setter_loc = page.locator('shreddit-darkmode-setter').first
        dark_mode_tracker_loc = page.locator('faceplate-tracker[noun="dark_mode"]').first
        if dark_mode_tracker_loc.count() == 1 and dark_mode_setter_loc.count() == 1:
            print("Try to set theme to " + ('dark' if settings.theme == 'dark' else 'light') + "...")
            is_dark_mode_enabled = dark_mode_setter_loc.get_attribute('enabled') is not None
            if (settings.theme == "dark" and not is_dark_mode_enabled) or (settings.theme != "dark" and is_dark_mode_enabled):
                dark_mode_tracker_loc.dispatch_event('click')
        
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
            
            # breakpoint()
            
            use_permalinks = False
            
            def print_comments_availability_on_page(comments):
                print()
                print("COMMENTS AVAILABILITY ON PAGE")
                on_page_comments = []
                off_page_comments = []
                for (_idx, comment) in enumerate(comments):
                    comment_excerpt = (comment.body.split("\n")[0])
                    if len(comment_excerpt) > 80: comment_excerpt = comment_excerpt[:80] + "…"
                    print(f" [{_idx + 1}/{len(accepted_comments)} {comment.id}] {comment.author}: {comment_excerpt}")
                    
                    # Locate comment
                    selector = f'shreddit-comment[thingid="t1_{comment.id}"]'
                    comment_loc = page.locator(selector).first
                    
                    if comment_loc.is_visible():
                        print("  ON PAGE")
                        on_page_comments.append(comment)
                    else:
                        print(" OFF PAGE")
                        off_page_comments.append(comment)
                print(f"ON PAGE: {len(on_page_comments)}  OFF PAGE: {len(off_page_comments)}")
                print()
                # breakpoint()
            
            for _idx, comment in enumerate(
                accepted_comments if settings.screenshot_debug else track(accepted_comments, "Downloading screenshots...")
            ):
                comment_path: Path = Path(f"{video_directory}/comment_{comment.id}.png")

                if comment_path.exists():
                    print(f"Comment Screenshot already downloaded : {comment_path}")
                else:
                    if page.locator('[data-testid="content-gate"]').is_visible():
                        page.locator('[data-testid="content-gate"] button').click()

                    # page.goto(f"https://reddit.com{comment.permalink}", timeout=0)

                    if new_reddit_ui_layout:
                        #print(f"https://reddit.com{comment.permalink}")
                        # Wait for the shreddit-comment to be present on the page
                        
                        comment_excerpt = (comment.body.split("\n")[0])
                        if len(comment_excerpt) > 80: comment_excerpt = comment_excerpt[:80] + "…"
                        print(f"[{_idx + 1}/{len(accepted_comments)} {comment.id}] {comment.author}: {comment_excerpt}")
                        
                        time.sleep(3)

                        # Locate comment
                        selector = f'shreddit-comment[thingid="t1_{comment.id}"]'
                        comment_loc = page.locator(selector).first
                        
                        # If comment not found on page, load single thread from permalink
                        if use_permalinks or (not use_permalinks and not comment_loc.is_visible()):
                            if not use_permalinks:
                                print(f"Comment not found on page, using permalink to '{comment.permalink}'...")
                                print("Use permalinks from now on...")
                                use_permalinks = True
                            # breakpoint()
                            page.goto(f"https://reddit.com{comment.permalink}", timeout=0)

                        # Bypass "See this post in..."
                        see_this_post_in_button = page.locator('#bottom-sheet button.continue').first
                        if see_this_post_in_button.is_visible():
                            print("See this post in... [CONTINUE]")
                            see_this_post_in_button.dispatch_event('click')
                            see_this_post_in_button.wait_for(state='hidden')
                        
                        # Click on "View more comments", if present
                        view_more_comments_button = page.locator('.overflow-actions-dialog ~ button').first
                        if view_more_comments_button.is_visible():
                            print("View more comments... [CLICK]")
                            view_more_comments_button.dispatch_event('click')
                            view_more_comments_button.wait_for(state='hidden')
                        
                        if _idx == 0 and False:
                            print_comments_availability_on_page(accepted_comments)
                        
                        # If the comment text itself is collapsed, expand it
                        comment_text_loc = comment_loc.locator("p").first
                        if not comment_text_loc.is_visible():
                            self_expand_button_loc = comment_loc.locator('summary button').first
                            if self_expand_button_loc.is_visible():
                                self_expand_button_loc.dispatch_event('click')
                            elif settings.screenshot_debug:
                                print("[screenshot_debug]")
                                breakpoint()
                        
                        # If replies are expanded toggle them
                        expanded_loc = comment_loc.locator('#comment-fold-button[aria-expanded="true"]').first
                        if expanded_loc.is_visible():
                            #print("If replies are expanded toggle them")
                            expanded_loc.dispatch_event("click")
                        
                        entry_element = comment_loc
                        
                        #print(is_new_layout(page))
                        
                        # Check if the element exists before taking a screenshot
                        print(f"Downloading screenshot '{comment_path}'...")
                        if entry_element.is_visible():
                            entry_element.scroll_into_view_if_needed()
                            entry_element.screenshot(path=comment_path)
                        else:
                            print("Mmmmhhh... could not create screenshot!")
                            print("2nd attempt, redirecting to comment permalink :")
                            print(f"https://reddit.com{comment.permalink}")
                            page.goto(f"https://reddit.com{comment.permalink}", timeout=0)
                            time.sleep(3)
                            if is_new_layout(page):
                                # Bypass "See this post in..."
                                see_this_post_in_button = page.locator('#bottom-sheet button.continue').first
                                if see_this_post_in_button.is_visible():
                                    print("See this post in... [CONTINUE]")
                                    see_this_post_in_button.dispatch_event('click')

                                comment_loc = page.locator(selector).first
                                if comment_loc:
                                    # If replies are expanded toggle them
                                    expanded_loc = comment_loc.locator('#comment-fold-button[aria-expanded="true"]').first
                                    if expanded_loc.is_visible():
                                        #print("Collapse the comment replies")
                                        expanded_loc.dispatch_event("click")
                                    time.sleep(2)
                                    comment_loc.screenshot(path=comment_path)
                                    page.goto(url, timeout=0)
                            else:
                                if page.locator(f"#t1_{comment.id}").first:
                                    page.locator(f"#t1_{comment.id}").screenshot(path=comment_path)

                            if settings.screenshot_debug: 
                                print("[screenshot_debug]")
                                breakpoint()
                    else:
                        page.goto(f"https://reddit.com{comment.permalink}", timeout=0)
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
        print("Launching " + ("Headless " if settings.headless_browser else "") + "Browser...")

        browser = p.chromium.launch(headless=settings.headless_browser)
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
