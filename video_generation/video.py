"""Generate videos from Reddit posts.

This module contains classes and helpers to combine the contents of Reddit
posts, comments, background clips, images relevant to the Reddit discussion,
voice narration and newscasters in to a single, (hopefully) coreherent video.
"""
import json
import logging
import os
from os import path
from pathlib import Path
from random import SystemRandom
from typing import Any, Dict, List, Optional
import random
import re 

from comments.screenshot import (
    download_screenshot_of_reddit_post_title,
    download_screenshots_of_reddit_posts,
)

import config.settings as settings

import csvmgr

import moviepy.video.fx.all as vfx
from moviepy.editor import (
    AudioFileClip,
    ColorClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
    TextClip,
    VideoFileClip
)

from praw.models import Comment, Submission
from praw.models.comment_forest import CommentForest

import publish.youtube as youtube

import speech.speech as speech

from thumbnail.thumbnail import get_font_size

from utils.common import contains_url, give_emoji_free_text, sanitize_text

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log", "w", "utf-8"), logging.StreamHandler()],
)


def log_group_header(title: str) -> str:
    """Create a log group heading.

    Args:
        title: Heading to be displayed in the log output.

    Returns:
        A formatted string that can be used to generate a log group heading.
    """
    return f"========== {title} =========="


def log_group_subheader(title: str) -> str:
    """Create a log group sub-heading.

    Args:
        title: Sub-heading to be displayed in the log output.

    Returns:
        A formatted string that can be used to generate a log group
        sub-heading.
    """
    return f"===== {title} ====="


def print_post_details(post: Submission) -> None:
    """Log the details of the Reddit post to be used to generate the video.

    Args:
        post: The Reddit post.
    """
    logging.info("SubReddit : %s", post.subreddit_name_prefixed)
    logging.info("Title     : %s", post.title)
    logging.info("Score     : %s", post.score)
    logging.info("ID        : %s", post.id)
    logging.info("URL       : %s", post.url)
    logging.info("SelfText  : %s", post.selftext)
    logging.info("NSFW?     : %s", post.over_18)


def print_comment_details(comment: Comment) -> None:
    """Log the details of the Reddit comment to be included in the video.

    Args:
        comment: The comment.
    """
    if comment.author:
        logging.debug("Author   : %s", comment.author)
    logging.debug("id       : %s", comment.id)
    logging.debug("Stickied : %s", comment.stickied)
    logging.info("Comment   : %s", give_emoji_free_text(str(comment.body)))
    logging.info("Length    : %s", len(comment.body))


class Video:
    """A video generated from a single Reddit post."""

    def __init__(
        self,
        background: Optional[Path] = None,
        clips: Optional[List[Path]] = None,
        description: str = "",
        duration: int = 0,
        meta: Optional[object] = None,
        script: str = "",
        thumbnail: Optional[Path] = None,
        title: str = "",
        filepath: Optional[Path] = None,
        json: str = "",
        theme: Optional[str] = None,
    ) -> None:
        """Initialise a new Video.

        Args:
            background: Path to the background image/video to be used in the
                clip.
            clips: List of paths to the segments used to generate the final
                video.
            description: Brief description to be added to the video.
            duration: Video duration, in seconds.
            meta: Additional video metadata.
            script: Voice script to be overlaid on to the video.
            thumbnail: Thumbnail to be displayed on the published video.
            title: Video title.
            filepath: Path where the video will be saved.
            json: Path where video metadata will be written, in json format.
            theme: Optional theme used to switch between normal, and 'dark'
                mode.
        """
        self.background = background

        if clips is None:
            self.clips = []
        else:
            self.clips = clips

        self.description = description
        self.duration = duration
        self.meta = meta
        self.script = script
        self.thumbnail = thumbnail
        self.title = title
        self.filepath = filepath
        self.json = json
        self.theme = theme

    def get_background(self) -> None:
        """Select a random background for the video."""
        rnd: SystemRandom = SystemRandom()
        self.background = rnd.choice(seq=os.listdir(settings.background_directory))
        logging.info("Randomly Selecting Background : %s", self.background)

    def compile(self) -> None:
        """Compile the video.

        This is a temporary placeholder.
        """
        pass


def get_random_lines(file_name: Path, num_lines: int) -> str:
    """Get a random selection of lines from a piece of text.

    Args:
        file_name: Text file containing one or more lines of text.
        num_lines: Number of lines to be returned.

    Returns:
        A string containing `num_lines` of text, where each line of text is
        separated by a newline.
    """
    with open(file_name, "r") as file:
        lines: List[str] = file.readlines()

        rnd: SystemRandom = SystemRandom()
        random_lines: List[str] = rnd.sample(lines, num_lines)
        return "\n".join(random_lines)


def create(video_directory: Path, post: Submission, thumbnails: List[Path]) -> None:
    """Generate a video from a processed reddit post.

    Args:
        video_directory: Path that the generated video will be saved to.
        post: Reddit post that's the main topic of the video.
        thumbnails: List of images to be embedded in the video. For example,
            screenshots of user comments.
    """
    logging.info(log_group_header(title="Processing Reddit Post"))
    print_post_details(post)

    v = Video()
    v.meta = post
    v.clips = []
    if settings.enable_background:
        v.get_background()

    if thumbnails:
        v.thumbnail = thumbnails[0]

    v.description = get_random_lines(Path("referral.txt"), 1)

    if settings.add_hashtag_shorts_to_description:
        v.description += " #shorts"

    v.title = f"{sanitize_text(v.meta.title)}"
    width: int = settings.video_width
    clip_margin: int = settings.clip_margin
    clip_margin_top: int = settings.clip_margin_top
    txt_clip_size = (width - (clip_margin * 2), None)

    current_clip_text: str = ""
    t: int = 0

    # intro_clip = VideoFileClip("intro_welcome_crop.mp4")\
    #                 .set_start(0)

    # v.clips.append(intro_clip)

    # t += intro_clip.duration

    tb: int = t
    speech_directory: Path = Path(settings.speech_directory, v.meta.id)
    speech_directory.mkdir(parents=True, exist_ok=True)

    audio_title: str = str(Path(speech_directory, "title.mp3"))

    title_speech_text: str = f"{sanitize_text(v.meta.title)}"

    speech.create_audio(audio_title, title_speech_text)

    audioclip_title: str = AudioFileClip(audio_title).volumex(2)

    # subreddit_clip = (
    #     TextClip(
    #         v.meta.subreddit_name_prefixed,
    #         font="Impact",
    #         fontsize=60,
    #         color=settings.text_color,
    #         size=txt_clip_size,
    #         kerning=-1,
    #         method="caption",
    #         ##bg_color=settings.text_bg_color,
    #         align="West",
    #     )
    #     .set_position((40, 40))
    #     .set_duration(audioclip_title.duration + settings.pause)
    #     .set_start(t)
    # )

    # v.clips.append(subreddit_clip)

    title_fontsize, lineheight = get_font_size(len(v.meta.title))
    margin_top = 245
    title_clip_position_vertical = "center"
    title_clip_duration = audioclip_title.duration + settings.pause

    if settings.shorts_mode_enabled:
        title_clip_position_vertical = margin_top
        title_clip_duration = settings.max_video_length

    if settings.enable_screenshot_title_image:
        screenshot_directory: Path = Path(settings.screenshot_directory, v.meta.id)
        download_screenshot_of_reddit_post_title(
            f"http://reddit.com{v.meta.permalink}", screenshot_directory
        )

        title_path: str = str(Path(screenshot_directory, "title.png"))

        title_clip: ImageClip = (
            ImageClip(title_path)
            .set_position(("center", title_clip_position_vertical))
            .set_duration(title_clip_duration)
            .set_audio(audioclip_title)
            .set_start(t)
            .set_opacity(settings.reddit_comment_opacity)
        )
        title_clip = title_clip.resize(
            width=settings.video_width * settings.reddit_comment_width
        )
        # if title_clip.w > title_clip.h:
        #     print("Resizing Horizontally")
        #     title_clip = title_clip.resize(
        #         width=settings.video_width * settings.reddit_comment_width
        #     )
        # else:
        #     print("Resizing Vertically")
        #     title_clip = title_clip.resize(height=settings.video_height * 0.95)
    else:
        title_clip = (
            (ImageClip(v.thumbnail) if v.thumbnail is not None else ColorClip((settings.video_width, settings.video_height)))
            .set_position(("center", title_clip_position_vertical))
            .set_duration(title_clip_duration)
            .set_audio(audioclip_title)
            .set_start(t)
            .set_opacity(settings.reddit_comment_opacity)
            .resize(width=settings.video_width * settings.reddit_comment_width)
        )

    v.clips.append(title_clip)

    t += audioclip_title.duration + settings.pause
    v.duration += audioclip_title.duration + settings.pause

    newcaster_start: int = t

    if settings.shorts_mode_enabled:
        text_clip_margin = title_clip.h + 10 + margin_top
    else:
        text_clip_margin = clip_margin_top

    if v.meta.selftext and settings.enable_selftext:
        logging.info(log_group_header(title="Processing SelfText"))
        logging.info(v.meta.selftext)

        selftext: str = sanitize_text(v.meta.selftext)
        selftext = give_emoji_free_text(selftext)
        selftext = os.linesep.join([s for s in selftext.splitlines() if s])

        logging.debug("selftext Length  : %s", len(selftext))

        selftext_lines: List[str] = selftext.splitlines()

        for selftext_line_count, selftext_line in enumerate(selftext_lines):
            # Skip zero space character comment
            if selftext_line == "&#x200B;":
                continue

            if selftext_line == " " or selftext_line == "  ":
                continue

            logging.debug("selftext length   : %s", len(selftext_line))
            logging.debug("selftext_line     : %s", selftext_line)
            selftext_audio_filepath: str = str(
                Path(speech_directory, f"selftext_{str(selftext_line_count)}.mp3")
            )
            speech.create_audio(selftext_audio_filepath, selftext_line)
            selftext_audioclip: AudioFileClip = AudioFileClip(selftext_audio_filepath)

            current_clip_text += f"{selftext_line}\n"
            logging.debug("Current Clip Text :")
            logging.debug(current_clip_text)
            logging.debug("SelfText Fontsize : %s", settings.text_fontsize)

            selftext_clip: TextClip = (
                TextClip(
                    current_clip_text,
                    font=settings.text_font,
                    fontsize=settings.text_fontsize,
                    color=settings.text_color,
                    size=txt_clip_size,
                    kerning=-1,
                    method="caption",
                    # bg_color=settings.text_bg_color,
                    align="West",
                )
                .set_position((clip_margin, text_clip_margin))
                .set_duration(selftext_audioclip.duration + settings.pause)
                .set_audio(selftext_audioclip)
                .set_start(t)
                .set_opacity(settings.text_bg_opacity)
                .volumex(1.5)
            )

            if selftext_clip.h > settings.video_height - text_clip_margin:
                logging.debug("Text exceeded Video Height, reset text")
                current_clip_text = f"{selftext_line}\n"
                selftext_clip = (
                    TextClip(
                        current_clip_text,
                        font=settings.text_font,
                        fontsize=settings.text_fontsize,
                        color=settings.text_color,
                        size=txt_clip_size,
                        kerning=-1,
                        method="caption",
                        # bg_color=settings.text_bg_color,
                        align="West",
                    )
                    .set_position((clip_margin, text_clip_margin))
                    .set_opacity(settings.text_bg_opacity)
                    .set_duration(selftext_audioclip.duration + settings.pause)
                    .set_audio(selftext_audioclip)
                    .set_start(t)
                )

                if selftext_clip.h > settings.video_height - text_clip_margin:
                    logging.debug("Comment Text Too Long, Skipping Comment")
                    continue

            t += selftext_audioclip.duration + settings.pause
            v.duration += selftext_audioclip.duration + settings.pause

            v.clips.append(selftext_clip)
            logging.debug("Video Clips : ")
            logging.debug(str(len(v.clips)))

        logging.info("Current Video Duration : %s", v.duration)
        logging.info(log_group_header(title="Finished Processing SelfText"))

        static_clip: VideoFileClip = (
            VideoFileClip("static.mp4")
            .set_duration(1)
            .set_position(("center", "center"))
            .set_start(t)
            .set_opacity(settings.background_opacity)
            .volumex(0.3)
        )

        v.clips.append(static_clip)
        t += static_clip.duration
        v.duration += static_clip.duration

    current_clip_text = ""

    if settings.enable_comments:
        all_comments: Optional[CommentForest] = v.meta.comments
        all_comments.replace_more(limit=0)

        accepted_comments: List[Comment] = []

        rejected_comments: List[Comment] = []

        logging.info(log_group_header(title="Filtering Reddit Comments"))

        for count, c in enumerate(all_comments):
            logging.info(log_group_subheader(title=f"Comment # {str(count)}"))
            print_comment_details(c)

            comment: str = c.body

            if len(comment) > settings.comment_length_max:
                logging.info(
                    "Status : REJECTED, Comment exceeds max character length : %s",
                    settings.comment_length_max,
                )
                rejected_comments.append(c)
                continue

            if comment == "[removed]" or comment == "[deleted]":
                logging.info("Status : REJECTED, Skipping Comment : %s", comment)
                rejected_comments.append(c)
                continue

            markdown_image_regex = r'!\[.*\]\(.*\)'
            if re.search(markdown_image_regex, comment):
                logging.info("Status : REJECTED, Markdown Image : %s", comment)
                rejected_comments.append(c)
                continue
    
            if "covid" in comment.lower() or "vaccine" in comment.lower():
                logging.info(
                    "Status : REJECTED, Covid related, \
                    Youtube will Channel Strike..: %s",
                    comment,
                )
                rejected_comments.append(c)
                continue

            comment = give_emoji_free_text(comment)
            comment = os.linesep.join([s for s in comment.splitlines() if s])

            logging.debug("Comment Length  : %s", len(comment))

            if c.stickied:
                logging.info("Status : REJECTED, Skipping Stickied Comment...")
                rejected_comments.append(c)
                continue

            if contains_url(comment):
                logging.info("Status : REJECTED, Skipping Comment with URL in it...")
                rejected_comments.append(c)
                continue

            logging.info("Status : ACCEPTED")
            accepted_comments.append(c)

            if len(accepted_comments) == settings.comment_limit:
                logging.info("Rejected Comments : %s", len(rejected_comments))
                logging.info("Accepted Comments : %s", len(accepted_comments))
                break

        screenshot_directory = Path(settings.screenshot_directory, v.meta.id)
        if settings.commentstyle == "reddit":
            download_screenshots_of_reddit_posts(
                accepted_comments,
                f"http://reddit.com{v.meta.permalink}",
                screenshot_directory,
            )

        if not settings.enable_comments_audio:
            print("Skipping comments' audio generation...")
        else:
            for count, accepted_comment in enumerate(accepted_comments):
                logging.info(
                    "=== Processing Reddit Comment %s/%s ===", count, len(accepted_comments)
                )

                if settings.commentstyle == "reddit":
                    audio_filepath: str = str(
                        Path(speech_directory, f"{accepted_comment.id}.mp3")
                    )
                    speech.create_audio(audio_filepath, accepted_comment.body)
                    audioclip: AudioFileClip = AudioFileClip(audio_filepath)

                    img_path: str = str(
                        Path(screenshot_directory, f"comment_{accepted_comment.id}.png")
                    )
                    if path.exists(img_path):
                        try:
                            img_clip: ImageClip = (
                                ImageClip(img_path)
                                .set_position(("center", "center"))
                                .set_duration(audioclip.duration + settings.pause)
                                .set_audio(audioclip)
                                .set_start(t)
                                .set_opacity(settings.reddit_comment_opacity)
                                .resize(
                                    width=settings.video_width
                                    * settings.reddit_comment_width
                                )
                            )
                        except Exception as e:
                            print(e)
                            continue
                    else:
                        logging.info("Comment image not found : %s", img_path)
                        continue

                    if img_clip.h > settings.video_height:
                        logging.info("Comment larger than video height : %s", img_path)
                        continue

                    if v.duration + audioclip.duration > settings.max_video_length:
                        logging.info(
                            "Reached Maximum Video Length : %s", settings.max_video_length
                        )
                        logging.info("Used %s/%s comments", count, len(accepted_comments))
                        logging.info("=== Finished Processing Comments ===")
                        break

                    t += audioclip.duration + settings.pause
                    v.duration += audioclip.duration + settings.pause

                    v.clips.append(img_clip)

                    logging.debug("Video Clips : ")
                    logging.debug(str(len(v.clips)))
                    logging.info("Current Video Duration : %s", v.duration)

                if settings.commentstyle == "text":
                    comment_lines: List[str] = accepted_comment.body.splitlines()

                    for ccount, comment_line in enumerate(comment_lines):
                        if comment_line == "&#x200B;":
                            logging.info("Skip zero space character comment : %s", comment)
                            continue

                        if comment_line == "" or comment_line == ' ':
                            logging.info("Skipping blank comment")
                            continue

                        logging.debug("comment_line     : %s", comment_line)
                        audio_filepath = str(
                            Path(
                                speech_directory,
                                f"{accepted_comment.id}_{str(ccount)}.mp3",
                            )
                        )

                        speech.create_audio(audio_filepath, comment_line)
                        print(f"Reading audio file: {audio_filepath}")
                        audioclip = AudioFileClip(audio_filepath)

                        current_clip_text += f"{comment_line}\n\n"
                        logging.debug("Current Clip Text :")
                        logging.debug(current_clip_text)

                        txt_clip: TextClip = (
                            TextClip(
                                accepted_comment.body,
                                font=settings.text_font,
                                fontsize=settings.text_fontsize,
                                color=settings.text_color,
                                size=txt_clip_size,
                                kerning=-1,
                                method="caption",
                                #bg_color=settings.text_bg_color,
                                align="West",
                            )
                            .set_position(("center", text_clip_margin))
                            .set_duration(audioclip.duration + settings.pause)
                            .set_audio(audioclip)
                            .set_start(t)
                            .set_opacity(settings.text_bg_opacity)
                            .volumex(1.5)
                        )

                        if txt_clip.h > settings.video_height - text_clip_margin:
                            logging.debug("Text exceeded Video Height, reset text")
                            current_clip_text = f"{comment_line}\n\n"
                            txt_clip = (
                                TextClip(
                                    current_clip_text,
                                    font=settings.text_font,
                                    fontsize=settings.text_fontsize,
                                    color=settings.text_color,
                                    size=txt_clip_size,
                                    kerning=-1,
                                    method="caption",
                                    # bg_color=settings.text_bg_color,
                                    align="West",
                                )
                                .set_position((clip_margin, text_clip_margin))
                                .set_duration(audioclip.duration + settings.pause)
                                .set_audio(audioclip)
                                .set_opacity(settings.text_bg_opacity)
                                .set_start(t)
                            )

                            if txt_clip.h > settings.video_height - text_clip_margin:
                                logging.debug("Comment Text Too Long, Skipping Comment")
                                continue

                            total_duration: int = v.duration + audioclip.duration
                            if total_duration > settings.max_video_length:
                                logging.info(
                                    "Reached Maximum Video Length : %s",
                                    settings.max_video_length,
                                )
                                logging.info(
                                    "Used %s/%s comments",
                                    ccount,
                                    len(accepted_comments),
                                )
                                logging.info("=== Finished Processing Comments ===")
                                break

                        t += audioclip.duration + settings.pause
                        v.duration += audioclip.duration + settings.pause

                        v.clips.append(txt_clip)
                        logging.debug("Video Clips : ")
                        logging.debug(str(len(v.clips)))

                    logging.info("Current Video Duration : %s", v.duration)

                    if v.duration > settings.max_video_length:
                        logging.info(
                            "Reached Maximum Video Length : %s", settings.max_video_length
                        )
                        logging.info("Used %s/%s comments", ccount, len(accepted_comments))
                        logging.info("=== Finished Processing Comments ===")
                        break

                    if count == settings.comment_limit:
                        logging.info(
                            "Reached Maximum Number of Comments Limit : %s",
                            settings.comment_limit,
                        )
                        logging.info("Used %s/%s comments", ccount, len(accepted_comments))
                        logging.info("=== Finished Processing Comments ===")
                        break
    else:
        logging.info("Skipping comments!")

    logging.info(log_group_subheader(title="Adding Background Clip"))

    if settings.enable_background:
        background_filepath: Path = Path(
            settings.background_directory, str(v.background)
        )
        logging.info("Background : %s", background_filepath)

        background_clip: VideoFileClip = (
            VideoFileClip(background_filepath)
            .set_start(tb)
            .set_opacity(settings.background_opacity)
            .volumex(0)
        )


        if settings.orientation == "portrait":
            print("Portrait mode, cropping and resizing!")
            # background_clip = background_clip.crop(
            #     x1=1166.6, 
            #     x2=2246.6, 
            #     y1=0, 
            #     y2=1920
            # ).resize((settings.vertical_video_width, settings.vertical_video_height))
            
            original_width, original_height = background_clip.size

            # Check if resizing is necessary
            if original_width < settings.vertical_video_width or original_height < settings.vertical_video_height:
                print("Scaling background video to minimum size required for vertical video")

                # Calculate the scaling factors for width and height
                width_scale = settings.vertical_video_width / original_width
                height_scale = settings.vertical_video_height / original_height

                # Choose the minimum scaling factor to ensure the video fits the desired dimensions
                scaling_factor = max(width_scale, height_scale)

                # Calculate the new dimensions
                new_width = int(original_width * scaling_factor)
                new_height = int(original_height * scaling_factor)

                background_clip = background_clip.resize((new_width, new_height))
                original_width, original_height = background_clip.size
            # Calculate the crop dimensions

            print(f"original_width: {original_width}")
            print(f"original_height: {original_height}")
            print(f"settings.vertical_video_width: {settings.vertical_video_width}")
            print(f"settings.vertical_video_height: {settings.vertical_video_height}")
            x1 = (original_width - settings.vertical_video_width) // 2
            x2 = x1 + settings.vertical_video_width
            y1 = (original_height - settings.vertical_video_height) // 2
            y2 = y1 + settings.vertical_video_height
            print(f"x1: {x1}")
            print(f"x2: {x2}")
            print(f"y1: {y1}")
            print(f"y2: {y2}")
            # Crop the video clip
            background_clip = background_clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)

        if background_clip.duration < v.duration:
            logging.debug("Looping Background")
            # background_clip = vfx.make_loopable(background_clip, cross=0)
            background_clip = vfx.loop(
                background_clip, duration=v.duration
            ).without_audio()
            video_duration: str = str(background_clip.duration)
            logging.debug("Looped Background Clip Duration : %s", video_duration)
        else:
            logging.debug("Not Looping Background")
            background_clip = background_clip.set_duration(v.duration)
    else:
        logging.info("Background not enabled...")
        background_clip = ColorClip(
            size=(settings.video_width, settings.video_height),
            color=settings.background_colour,
        ).set_duration(v.duration)

    v.clips.insert(0, background_clip)

    if settings.enable_background_music:
        print(f"Creating background music audio")
        if settings.background_music_path:
            background_music_filepath = settings.background_music_path
            logging.info(f"Using specified background music : {background_music_filepath}")
        else:
            rnd: SystemRandom = SystemRandom()
            background_music_path = rnd.choice(seq=os.listdir(settings.music_directory))
            background_music_filepath: Path = Path(
                settings.music_directory,
                str(background_music_path)
            )
            logging.info("Randomly Selected Background Music : %s", background_music_filepath)

        background_music_audio = AudioFileClip(background_music_filepath)

        # Adjust audio clip to match video duration
        if background_music_audio.duration < v.duration:
            # Loop the audio to match the video duration
            background_music_audio = background_music_audio.volumex(0).loop(-1, duration=v.duration)
        elif background_music_audio.duration > v.duration:
            # Trim the audio to match the video duration
            background_music_audio = background_music_audio.subclip(0, v.duration)

        background_music_audio = background_music_audio.volumex(settings.background_music_volume)

    if settings.enable_overlay:
        logging.info(log_group_subheader(title="Adding Overlay Clip"))
        clip_video_overlay: VideoFileClip = (
            VideoFileClip(settings.video_overlay_filepath)
            .set_start(tb)
            .resize(settings.clip_size)
            .set_opacity(0.8)
            .volumex(0)
        )

        if clip_video_overlay.duration < v.duration:
            logging.debug("Looping Overlay")
            # background_clip = vfx.make_loopable(background_clip, cross=0)
            clip_video_overlay = vfx.loop(
                clip_video_overlay, duration=v.duration
            ).without_audio()
            video_duration = str(clip_video_overlay.duration)
            logging.debug("Looped Overlay Clip Duration : %s", video_duration)
        else:
            logging.debug("Not Looping Overlay")
            clip_video_overlay = clip_video_overlay.set_duration(v.duration)

        v.clips.insert(1, clip_video_overlay)

    if settings.enable_newscaster and settings.newscaster_filepath:
        logging.info(log_group_subheader(title="Adding Newcaster Clip"))
        logging.info("Newscaster File Path: %s", settings.newscaster_filepath)
        clip_video_newscaster: VideoFileClip = (
            VideoFileClip(settings.newscaster_filepath)
            .set_position(settings.newscaster_position)
            .set_start(newcaster_start)
            .resize(settings.newcaster_size)
            .set_opacity(1)
            .volumex(0)
        )

        if settings.newscaster_remove_greenscreen:
            logging.info(log_group_subheader(title="Removing Newcaster Green Screen"))
            # Green Screen Video https://github.com/Zulko/moviepy/issues/964
            clip_video_newscaster = clip_video_newscaster.fx(
                vfx.mask_color,
                color=settings.newscaster_greenscreen_color,
                thr=settings.newscaster_greenscreen_remove_threshold,
                s=5,
            )

        if clip_video_newscaster.duration < v.duration:
            logging.debug("Looping Newscaster")
            clip_video_newscaster = vfx.loop(
                clip_video_newscaster, duration=v.duration - newcaster_start
            ).without_audio()
            logging.debug(
                "Looped Newscaster Clip Duration : %s", clip_video_newscaster.duration
            )
        else:
            logging.debug("Not Looping Newscaster")
            clip_video_newscaster = clip_video_newscaster.set_duration(
                v.duration - newcaster_start
            )

        v.clips.append(clip_video_newscaster)

    post_video: CompositeVideoClip = CompositeVideoClip(v.clips)

    if settings.enable_background_music:
        print(f"Adding background music")
        # Create a composite audio clip with both original audio and adjusted background music
        composite_audio = CompositeAudioClip([post_video.audio, background_music_audio])

        # Set the audio of the video clip to the composite audio
        post_video = post_video.set_audio(composite_audio)

    v.filepath = Path(video_directory, "final.mp4")
    v.json = str(Path(video_directory, "meta.json"))

    data: Dict[str, Any] = {
        "title": str(v.title),
        "description": str(v.description),
        "thumbnail": str(v.thumbnail),
        "file": str(v.filepath),
        "duration": str(v.duration),
        "height": str(settings.video_height),
        "width": str(settings.video_width),
        "url": f"http://reddit.com{v.meta.permalink}",
    }

    with open(v.json, "w") as outfile:  # noqa: SCS109
        json.dump(data, outfile, indent=4)

    csvwriter = csvmgr.CsvWriter()

    row: Dict[str, Any] = {
        "id": v.meta.id,
        "title": v.title,
        "thumbnail": v.thumbnail,
        "file": v.filepath,
        "duration": v.duration,
        "compiled": "false",
        "uploaded": "false",
        "url": f"http://reddit.com{v.meta.permalink}",
    }

    csvwriter.write_entry(row=row)

    if settings.enable_compilation:
        logging.info(log_group_subheader(title="Compiling Video Clip"))
        logging.info("Compiling video, this takes a while, please be patient : ")
        post_video.write_videofile(v.filepath, fps=24)

    else:
        logging.info("Skipping Video Compilation --enable_compilation passed")

    if settings.enable_compilation and settings.enable_upload:
        if path.exists("client_secret.json") and path.exists("credentials.storage"):
            if csvwriter.is_uploaded(v.meta.id):
                logging.info("Already uploaded according to data.csv")
            else:
                logging.info(
                    log_group_subheader(title="Uploading Video Clip to YouTube")
                )
                try:
                    youtube.publish(v)
                except Exception as e:
                    print(e)
                else:
                    csvwriter.set_uploaded(v.meta.id)
        else:
            logging.info(
                "Skipping upload, missing either \
                client_secret.json or credentials.storage file."
            )
    else:
        logging.info("Skipping Upload...")
