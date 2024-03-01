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
import datetime as dt
import json
from jinja2 import Environment, FileSystemLoader

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

def set_inner_html(page, selector, inner_html=''):
    el = page.locator(selector).first
    # Escape inner_html
    #TODO: probably more cases are to be handled
    escaped_inner_html = inner_html.replace("\n", "\\n").replace('"', '\\"').replace("'", "\\'")
    evaluate_context_data = escaped_inner_html
    el.first.evaluate(f"el => el.innerHTML = \'{escaped_inner_html}\';", evaluate_context_data)

def fill_template(template, values):
    filled_template = template # a copy of template
    for k, v in values.items():
        filled_template = filled_template.replace(k, v)

    return filled_template

# Formats `datetime` to something like '1 year ago', '25 minutes ago', etc.
# TODO: check if it works properly (for now it only tries to handle past dates)
def datetime_to_human_timedelta(datetime):
    now = dt.datetime.now()
    delta = now - datetime
    total_seconds = delta.total_seconds()
    years = total_seconds // (3600 * 24 * 30 * 12)
    months = total_seconds // (3600 * 24 * 30)
    days = total_seconds // (3600 * 24)
    hours = total_seconds // 3600
    minutes = total_seconds // 60
    seconds = total_seconds

    human_timedelta = "just now"
    suffixes = ["year", "month", "day", "hour", "minute", "second"]
    elapsed = [years, months, days, hours, minutes, seconds]
    # print(list(zip(suffixes, elapsed)))
    for idx, t in enumerate(elapsed):
        if t > 0:
            human_timedelta = f"{t:.0f} {suffixes[idx]}"
            if t > 1:
                human_timedelta += "s"
            human_timedelta += " ago"
            break

    return human_timedelta

# Formats `number` to something like '12.2k', '1.1M', etc.
# (note that the threshold for using 'k' is 10000, i.e. 9500 will still be converted to '9500' and NOT to '9.5k')
def number_to_abbreviated_string(number):
    abbreviated_str = f"{number:.0f}"
    millions = number / 1000000
    thousands = number / 1000
    suffixes = ["M", "k"]
    counts = [millions, thousands]
    thresholds = [1, 10]
    # print(list(zip(suffixes, counts)))
    for idx, n in enumerate(counts):
        if n >= thresholds[idx]:
            abbreviated_str = f"{n:.1f}{suffixes[idx]}"
            break

    return abbreviated_str

def get_comment_excerpt(comment):
    comment_excerpt = (comment.body.split("\n")[0])
    if len(comment_excerpt) > 80: comment_excerpt = comment_excerpt[:80] + "…"

    return comment_excerpt


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
    # print("Downloading screenshots of reddit posts...")
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

        if settings.use_template:
            template_url = str(Path("comment_templates", settings.template_url))
            # Read the Jinja template from a file
            print(f"Using Comment Template : {template_url}")

            # Create a Jinja environment with UTF-8 encoding
            env = Environment(loader=FileSystemLoader(template_url))
            # Load the template
            template = env.get_template('index.html')
            for _idx, comment in enumerate(
                accepted_comments if settings.screenshot_debug else track(accepted_comments, "Downloading screenshots...")
            ):
                comment_path: Path = Path(f"{video_directory}/comment_{comment.id}.png")

                if comment_path.exists():
                    print(f"Comment Screenshot already downloaded : {comment_path}")
                else:
                    comment_excerpt = get_comment_excerpt(comment)
                    print(f"[{_idx + 1}/{len(accepted_comments)} {comment.id}] {comment.author}: {comment_excerpt}")

                    # Fill template fields and update page
                    values = {
                        'author': comment.author.name if comment.author else '[unknown]',
                        'id': comment.id,
                        'score': number_to_abbreviated_string(comment.score),
                        'avatar': comment.author.icon_img if comment.author else '[unknown]',
                        'date': datetime_to_human_timedelta(dt.datetime.fromtimestamp(comment.created)),
                        'body_text': comment.body,
                        'body_html': comment.body_html,
                    }
                    # Render the template with variables
                    output = template.render(values)

                    # # Save the rendered output to a file
                    # print("Jinja Comment Output :")
                    # print(output)
                    # with open(f"{video_directory}/comment_{comment.id}.html", "w", encoding="utf-8") as output_file:
                    #     output_file.write(output)

                    # Option 1: Pass HTML content
                    page.set_content(output)

                    page.locator('#comment-container').screenshot(path=str(comment_path.resolve()))
                    #browser.close()


        else:


            reddit_login_url = "https://old.reddit.com/login" if settings.use_old_reddit_login else "https://www.reddit.com/login"

            print(f"Trying to login ({reddit_login_url})...")
            page.goto(reddit_login_url)

            #time.sleep(5)
            # Wait for the page to finish loading
            page.wait_for_load_state("load")

            # Attempt to login
            # TODO: to be refactored!
            username_loc = None
            password_loc = None
            button_loc = None
            login_fields_found = False
            login_fields_found_using = ""
            # Attempt to login using old.reddit.com/login
            if settings.use_old_reddit_login:
                username_loc = page.locator("#login-form #user_login").first
                password_loc = page.locator("#login-form #passwd_login").first
                button_loc = page.locator("#login-form button[type='submit']").first
                if (username_loc.is_visible() and password_loc.is_visible() and button_loc.is_visible()):
                    login_fields_found = True
                    login_fields_found_using = "old.reddit.com"
            # Check if the first set of selectors exist.
            elif not login_fields_found and page.query_selector("#loginUsername"):
                username_loc = page.locator("#loginUsername").first
                password_loc = page.locator("#loginPassword").first
                button_loc = page.locator('button[type="submit"]').first
                if (username_loc.is_visible() and password_loc.is_visible() and button_loc.is_visible()):
                    login_fields_found = True
                    login_fields_found_using = "1st set of selectors"
            # If the first set of selectors don't exist, try the second set.
            elif not login_fields_found and page.query_selector("#login-username"):
                page.type("#login-username", auth.praw_username)
                page.type("#login-password", auth.praw_password)
                # Wait for the button to be visible
                button_selector = 'button.login'
                username_loc = page.locator("#login-username").first
                password_loc = page.locator("#login-password").first
                button_loc = page.locator('button.login').first
                if (username_loc.is_visible() and password_loc.is_visible()):
                    page.wait_for_selector(button_selector, state="visible")
                    login_fields_found = True
                    login_fields_found_using = "2st set of selectors"
            # Alternative method
            elif not login_fields_found:
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
                    login_fields_found = True
                    login_fields_found_using = "frame_locator" if frame_loc_found else "3rd set of selectors"

            # Login fields found: fill fields and click login button
            if login_fields_found:
                print("Username and password fields found" + (f" (using {login_fields_found_using})" if login_fields_found_using else "") + ". Logging in...")
                username_loc.fill(auth.praw_username)
                password_loc.fill(auth.praw_password)
                button_loc.first.click()

                # Bypass "See Reddit in..."
                see_reddit_in_button = page.locator('#bottom-sheet button.continue').first
                if see_reddit_in_button.is_visible():
                    print("See Reddit in... [CONTINUE]")
                    see_reddit_in_button.dispatch_event('click')
                    see_reddit_in_button.wait_for(state='hidden')

                # Wait for navigation to page different from the login one
                login_url = page.url
                not_login_url_regex = re.compile('^(?!' + login_url + ')')
                if settings.screenshot_debug:
                    try:
                        page.wait_for_url(not_login_url_regex, wait_until="commit") # wait_until='commit' -> wait until another url started loading
                    except Exception as e:
                        print("[screenshot_debug]")
                        print(e)
                        breakpoint()
                else:
                    page.wait_for_url(not_login_url_regex, wait_until="commit") # wait_until='commit' -> wait until another url started loading

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

            if current_url == "https://www.reddit.com/" or (settings.use_old_reddit_login and current_url == "https://old.reddit.com/") or user_drawer_button.count() == 1:
                print("Login successful!")
            else:
                print("Login failed.")
                if settings.screenshot_debug:
                    print("[screenshot_debug]")
                    breakpoint()

            cookies = json.load(cookie_file)
            context.add_cookies(cookies)  # load preference cookies

            page.goto(url, timeout=0)
            reddit_base_url = "http://old.reddit.com" if settings.use_old_reddit else "https://reddit.com"

            #print(page.evaluate('() => document.querySelector("html").classList.toString()'))

            # Alternate method to try to set preferred theme
            dark_mode_setter_loc = page.locator('shreddit-darkmode-setter').first
            dark_mode_tracker_loc = page.locator('faceplate-tracker[noun="dark_mode"]').first
            if dark_mode_tracker_loc.count() == 1 and dark_mode_setter_loc.count() == 1:
                print("Try to set theme to " + ('dark' if settings.theme == 'dark' else 'light') + "...")
                is_dark_mode_enabled = dark_mode_setter_loc.get_attribute('enabled') is not None
                if (settings.theme == "dark" and not is_dark_mode_enabled) or (settings.theme != "dark" and is_dark_mode_enabled):
                    dark_mode_tracker_loc.dispatch_event('click')

            print("Downloading screenshots of reddit posts...")

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

                use_permalinks = settings.use_comments_permalinks
                if settings.use_comments_permalinks:
                    print("Using comment permalinks...")

                def get_comment_selector(comment):
                    selector = f'shreddit-comment[thingid="t1_{comment.id}"]'
                    if settings.use_old_reddit: selector = f'#thing_t1_{comment.id} .entry'

                    return selector

                def print_comments_availability_on_page(comments, detailed=False):
                    print()
                    print("COMMENTS AVAILABILITY ON PAGE")
                    on_page_comments = []
                    off_page_comments = []
                    for (_idx, comment) in enumerate(comments):
                        comment_excerpt = get_comment_excerpt(comment)
                        if detailed: print(f" [{_idx + 1}/{len(accepted_comments)} {comment.id}] {comment.author}: {comment_excerpt}")

                        # Locate comment
                        selector = get_comment_selector(comment)
                        comment_loc = page.locator(selector).first

                        if comment_loc.is_visible():
                            if detailed: print("  ON PAGE")
                            on_page_comments.append(comment)
                        else:
                            if detailed: print(" OFF PAGE")
                            off_page_comments.append(comment)
                    print(f"ON PAGE: {len(on_page_comments)} | OFF PAGE: {len(off_page_comments)} | TOTAL: {len(comments)}")
                    print()

                try:

                    if False:
                        print_comments_availability_on_page(accepted_comments)

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

                            if new_reddit_ui_layout or settings.use_old_reddit:
                                #print(f"https://reddit.com{comment.permalink}")
                                # Wait for the shreddit-comment to be present on the page

                                comment_excerpt = get_comment_excerpt(comment)
                                print(f"[{_idx + 1}/{len(accepted_comments)} {comment.id}] {comment.author}: {comment_excerpt}")

                                time.sleep(3)

                                # Locate comment
                                selector = get_comment_selector(comment)
                                comment_loc = page.locator(selector).first

                                # If comment not found on page, load single thread from permalink
                                if use_permalinks or (not use_permalinks and not comment_loc.is_visible()):
                                    if not use_permalinks:
                                        print(f"Comment not found on page, using permalink to '{comment.permalink}'...")
                                        print("Use permalinks from now on...")
                                        use_permalinks = True

                                    page.goto(f"{reddit_base_url}{comment.permalink}", timeout=0)

                                # Bypass "See this post in..."
                                see_this_post_in_button = page.locator('#bottom-sheet button.continue').first
                                if see_this_post_in_button.is_visible():
                                    print("See this post in... [CONTINUE]")
                                    see_this_post_in_button.dispatch_event('click')
                                    see_this_post_in_button.wait_for(state='hidden')
                                else:
                                    # Ensure to hide backdrop
                                    backdrop_loc = page.locator('#bottom-sheet #backdrop').first
                                    if backdrop_loc.count() > 0:
                                        if settings.screenshot_debug:
                                            print("Hiding backdrop...")
                                        backdrop_loc.evaluate('node => node.style.display="none"')

                                # Click on "View more comments", if present
                                view_more_comments_button = page.locator('.overflow-actions-dialog ~ button').first
                                if settings.use_old_reddit: view_more_comments_button = page.locator(".commentarea > .sitetable > .thing:not(.comment) .button").first
                                if view_more_comments_button.is_visible() and not use_permalinks:
                                    print("View more comments... [CLICK]")
                                    view_more_comments_button.dispatch_event('click')
                                    if not settings.use_old_reddit: view_more_comments_button.wait_for(state='hidden')

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

                                    if settings.use_old_reddit: # inject css
                                        # Set max-width (as it would be too big normally, with lots of empty space)
                                        # Change background-color (as it would be ~yellow for single-thread posts (permalinks))
                                        entry_element.evaluate("""el => {
                                            el.style.maxWidth = '750px';
                                            let commentBody = el.querySelector('.usertext-body');
                                            if (commentBody) commentBody.style.backgroundColor = 'inherit';
                                        }""")

                                    if settings.screenshot_debug: entry_element.scroll_into_view_if_needed()
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

                except Exception as e:
                    print(f"Error: {e}")
                    print("Taking screenshot and re-throwing Exception...")
                    error_path = Path(f"{video_directory}/error.png")
                    page.screenshot(path=error_path)
                    print(f"See '{error_path}'")
                    print()
                    raise

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
