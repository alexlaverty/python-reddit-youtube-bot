from moviepy.editor import (AudioFileClip,
                            ColorClip,
                            CompositeVideoClip,
                            ImageClip,
                            TextClip,
                            VideoFileClip
                            )
from pathlib import Path
import json
import logging
import os
from os.path import exists
import random
import config.settings as settings
import speech.speech as speech
import sys
from comments.screenshot import (download_screenshots_of_reddit_posts,
                                 download_screenshot_of_reddit_post_title)
from thumbnail.thumbnail import get_font_size
from utils.common import (give_emoji_free_text, contains_url, sanitize_text)
import publish.youtube as youtube
import moviepy.video.fx.all as vfx
import csvmgr

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log", "w", "utf-8"),
              logging.StreamHandler()],
)


def print_post_details(post):
    logging.info("SubReddit : " + post.subreddit_name_prefixed)
    logging.info("Title     : " + post.title)
    logging.info("Score     : " + str(post.score))
    logging.info("ID        : " + str(post.id))
    logging.info("URL       : " + post.url)
    logging.info("SelfText  : " + post.selftext)
    logging.info("NSFW?     : " + str(post.over_18))


def print_comment_details(comment):
    if comment.author:
        logging.debug("Author   : " + str(comment.author))
    logging.debug("id       : " + str(comment.id))
    logging.debug("Stickied : " + str(comment.stickied))
    logging.info("Comment   : " + give_emoji_free_text(str(comment.body)))
    logging.info("Length    : " + str(len(comment.body)))


class Video:
    def __init__(
        self,
        background=None,
        clips=[],
        description="",
        duration=0,
        meta=None,
        script="",
        thumbnail=None,
        title="",
        filepath="",
        json="",
        theme=None,
    ):
        self.background = background
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

    def get_background(self):
        self.background = random.choice(
            os.listdir(settings.background_directory))
        logging.info("Randomly Selecting Background : " + self.background)

    def compile(self):
        pass


def convert_keywords_to_string(keywords):
    keyword_string = ""
    for keyword in keywords:
        keyword_string = (
            keyword_string
            + str(keyword[0].encode("ascii", "ignore").decode("ascii"))
            + " "
        )
    return keyword_string.strip()


def get_random_lines(file_name, num_lines):
    with open(file_name, 'r') as file:
        lines = file.readlines()
        random_lines = random.sample(lines, num_lines)
        return '\n'.join(random_lines)


def create(video_directory, post, thumbnails):
    logging.info("========== Processing Reddit Post ==========")
    print_post_details(post)

    v = Video()
    v.meta = post
    v.clips = []
    if settings.enable_background:
        v.get_background()

    if thumbnails:
        v.thumbnail = thumbnails[0]

    subreddit_name = v.meta.subreddit_name_prefixed.replace("r/", "")

    v.description = get_random_lines('referral.txt', 5)

    if settings.add_hashtag_shorts_to_description:
        v.description += " #shorts"

    v.title = f"{sanitize_text(v.meta.title)}"
    height = settings.video_height
    width = settings.video_width
    clip_margin = 50
    clip_margin_top = 30
    txt_clip_size = (width - (clip_margin * 2), None)

    current_clip_text = ""
    t = 0

    # intro_clip = VideoFileClip("intro_welcome_crop.mp4")\
    #                 .set_start(0)

    # v.clips.append(intro_clip)

    # t += intro_clip.duration

    tb = t
    speech_directory = Path(settings.speech_directory, v.meta.id)
    speech_directory.mkdir(parents=True, exist_ok=True)

    audio_title = str(Path(speech_directory, "title.mp3"))

    title_speech_text = f"{sanitize_text(v.meta.title)}"

    speech.create_audio(audio_title, title_speech_text)

    audioclip_title = AudioFileClip(audio_title).volumex(2)

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

    # Generate Title Clip

    if settings.enable_screenshot_title_image:
        screenshot_directory = Path(settings.screenshot_directory, v.meta.id)
        download_screenshot_of_reddit_post_title(
            f"http://reddit.com{v.meta.permalink}", screenshot_directory
        )
        title_path = str(
            Path(screenshot_directory, "title.png")
        )
        title_clip = (
            ImageClip(title_path)
            .set_position(("center", "center"))
            .set_duration(audioclip_title.duration + settings.pause)
            .set_audio(audioclip_title)
            .set_start(t)
            .set_opacity(settings.reddit_comment_opacity)
        )
        if title_clip.w > title_clip.h:
            print("Resizing Horizontally")
            title_clip = title_clip.resize(width=settings.video_width *
                                           settings.reddit_comment_width)
        else:
            print("Resizing Vertically")
            title_clip = title_clip.resize(height=settings.video_height * 0.95)
    else:
        title_clip = (
            ImageClip(v.thumbnail)
            .set_position(("center", "center"))
            .set_duration(audioclip_title.duration + settings.pause)
            .set_audio(audioclip_title)
            .set_start(t)
            .set_opacity(settings.reddit_comment_opacity)
            .resize(width=settings.video_width * settings.reddit_comment_width)
        )

    v.clips.append(title_clip)

    t += audioclip_title.duration + settings.pause
    v.duration += audioclip_title.duration + settings.pause

    newcaster_start = t

    if v.meta.selftext and settings.enable_selftext:
        logging.info("========== Processing SelfText ==========")
        logging.info(v.meta.selftext)

        selftext = sanitize_text(v.meta.selftext)

        selftext = give_emoji_free_text(selftext)
        selftext = os.linesep.join([s for s in selftext.splitlines() if s])

        logging.debug("selftext Length  : " + str(len(selftext)))

        selftext_lines = selftext.splitlines()

        for selftext_line_count, selftext_line in enumerate(selftext_lines):

            # Skip zero space character comment
            if selftext_line == "&#x200B;":
                continue

            if selftext_line == ' ' or selftext_line == '  ':
                continue

            logging.debug("selftext length   : " + str(len(selftext_line)))
            logging.debug("selftext_line     : " + selftext_line)
            selftext_audio_filepath = str(
                Path(
                    speech_directory,
                    "selftext_" + str(selftext_line_count) + ".mp3"
                )
            )
            speech.create_audio(selftext_audio_filepath, selftext_line)
            selftext_audioclip = AudioFileClip(selftext_audio_filepath)

            current_clip_text += selftext_line + "\n"
            logging.debug("Current Clip Text :")
            logging.debug(current_clip_text)
            logging.debug(f"SelfText Fontsize : {settings.text_fontsize}")

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
                .set_position((clip_margin, clip_margin_top))
                .set_duration(selftext_audioclip.duration + settings.pause)
                .set_audio(selftext_audioclip)
                .set_start(t)
                .set_opacity(settings.text_bg_opacity)
                .volumex(1.5)
            )

            if selftext_clip.h > settings.video_height:
                logging.debug("Text exceeded Video Height, reset text")
                current_clip_text = selftext_line + "\n"
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
                    .set_position((clip_margin, clip_margin_top))
                    .set_opacity(settings.text_bg_opacity)
                    .set_duration(selftext_audioclip.duration + settings.pause)
                    .set_audio(selftext_audioclip)
                    .set_start(t)
                )

                if selftext_clip.h > settings.video_height:
                    logging.debug("Comment Text Too Long, Skipping Comment")
                    continue

            t += selftext_audioclip.duration + settings.pause
            v.duration += selftext_audioclip.duration + settings.pause

            v.clips.append(selftext_clip)
            logging.debug("Video Clips : ")
            logging.debug(str(len(v.clips)))

        logging.info("Current Video Duration : " + str(v.duration))
        logging.info("========== Finished Processing SelfText ==========")

        static_clip = (
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

        all_comments = v.meta.comments
        all_comments.replace_more(limit=0)

        accepted_comments = []

        rejected_comments = []

        logging.info(f"========== Filtering Reddit Comments ==========")
        for count, c in enumerate(all_comments):

            logging.info("===== Comment #" + str(count) + "=====")

            print_comment_details(c)

            comment = c.body

            if len(comment) > settings.comment_length_max:
                logging.info(
                    f"Status : REJECTED, \
                    Comment exceeds max character length : \
                    {str(settings.comment_length_max)}"
                )
                rejected_comments.append(c)
                continue

            if comment == "[removed]" or comment == "[deleted]":
                logging.info("Status : REJECTED, Skipping Comment : " + comment)
                rejected_comments.append(c)
                continue

            comment = give_emoji_free_text(comment)
            comment = os.linesep.join([s for s in comment.splitlines() if s])

            logging.debug("Comment Length  : " + str(len(comment)))

            if c.stickied:
                logging.info("Status : REJECTED, Skipping Stickied Comment...")
                rejected_comments.append(c)
                continue

            if contains_url(comment):
                logging.info(
                    "Status : REJECTED, \
                    Skipping Comment with URL in it..."
                )
                rejected_comments.append(c)
                continue

            logging.info("Status : ACCEPTED")
            accepted_comments.append(c)

            if len(accepted_comments) == settings.comment_limit:
                logging.info(
                    f"Rejected Comments : \
                    {str(len(rejected_comments))}"
                )
                logging.info(
                    f"Accepted Comments : \
                    {str(len(accepted_comments))}"
                )
                break
        screenshot_directory = Path(settings.screenshot_directory, v.meta.id)
        if settings.commentstyle == "reddit":
            download_screenshots_of_reddit_posts(
                accepted_comments,
                f"http://reddit.com{v.meta.permalink}",
                screenshot_directory
            )

        for count, accepted_comment in enumerate(accepted_comments):

            logging.info(
                f"=== Processing Reddit Comment \
                    {str(count)}/{str(len(accepted_comments))} ==="
            )


            if settings.commentstyle == "reddit":

                audio_filepath = str(
                    Path(
                        speech_directory,
                        accepted_comment.id + ".mp3"
                    )
                )
                speech.create_audio(audio_filepath, accepted_comment.body)
                audioclip = AudioFileClip(audio_filepath)

                img_path = str(
                    Path(screenshot_directory,
                         "comment_" + accepted_comment.id + ".png")
                )
                if exists(img_path):
                    try:
                        img_clip = (
                            ImageClip(img_path)
                            .set_position(("center", "center"))
                            .set_duration(audioclip.duration + settings.pause)
                            .set_audio(audioclip)
                            .set_start(t)
                            .set_opacity(settings.reddit_comment_opacity)
                            .resize(width=settings.video_width
                                    * settings.reddit_comment_width)
                        )
                    except Exception as e:
                        print(e)
                        continue
                else:
                    logging.info(f"Comment image not found : {img_path}")
                    continue

                if img_clip.h > settings.video_height:
                    logging.info(f"Comment larger than video height : {img_path}")
                    continue

                if v.duration + audioclip.duration > settings.max_video_length:
                    logging.info(
                        "Reached Maximum Video Length : "
                        + str(settings.max_video_length)
                    )
                    used_comment_ratio = f"{str(count)}/{str(len(accepted_comments))}"
                    logging.info(f"Used {used_comment_ratio} comments")
                    logging.info("=== Finished Processing Comments ===")
                    break

                t += audioclip.duration + settings.pause
                v.duration += audioclip.duration + settings.pause

                v.clips.append(img_clip)

                logging.debug("Video Clips : ")
                logging.debug(str(len(v.clips)))

                logging.info("Current Video Duration : " + str(v.duration))

            if settings.commentstyle == "text":

                comment_lines = accepted_comment.body.splitlines()

                for ccount, comment_line in enumerate(comment_lines):

                    if comment_line == "&#x200B;":
                        logging.info("Skip zero space character comment : " + comment)
                        continue

                    if comment_line == "":
                        logging.info("Skipping blank comment")
                        continue

                    logging.debug("comment_line     : " + comment_line)
                    audio_filepath = str(
                        Path(
                            speech_directory,
                            c.id + "_" + str(ccount) + ".mp3",
                        )
                    )
                    speech.create_audio(audio_filepath, comment_line)
                    audioclip = AudioFileClip(audio_filepath)

                    current_clip_text += comment_line + "\n\n"
                    logging.debug("Current Clip Text :")
                    logging.debug(current_clip_text)

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
                        .set_position((clip_margin, clip_margin_top))
                        .set_duration(audioclip.duration + settings.pause)
                        .set_audio(audioclip)
                        .set_start(t)
                        .set_opacity(settings.text_bg_opacity)
                        .volumex(1.5)
                    )

                    if txt_clip.h > settings.video_height:
                        logging.debug("Text exceeded Video Height, reset text")
                        current_clip_text = comment_line + "\n\n"
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
                            .set_position((clip_margin, clip_margin_top))
                            .set_duration(audioclip.duration + settings.pause)
                            .set_audio(audioclip)
                            .set_opacity(settings.text_bg_opacity)
                            .set_start(t)
                        )

                        if txt_clip.h > settings.video_height:
                            logging.debug(
                                "Comment Text Too Long, \
                                Skipping Comment"
                            )
                            continue

                        if v.duration + audioclip.duration > settings.max_video_length:
                            logging.info(
                                "Reached Maximum Video Length : "
                                + str(settings.max_video_length)
                            )
                            logging.info(f"Used {str(count)}/{str(len(accepted_comments))} comments")
                            logging.info("=== Finished Processing Comments ===")
                            break

                    t += audioclip.duration + settings.pause
                    v.duration += audioclip.duration + settings.pause

                    v.clips.append(txt_clip)
                    logging.debug("Video Clips : ")
                    logging.debug(str(len(v.clips)))

                logging.info("Current Video Duration : " + str(v.duration))

                if v.duration > settings.max_video_length:
                    logging.info(
                        "Reached Maximum Video Length : "
                        + str(settings.max_video_length)
                    )
                    logging.info(f"Used {str(ccount)}/{str(len(accepted_comments))} comments")
                    logging.info("=== Finished Processing Comments ===")
                    break

                if count == settings.comment_limit:
                    logging.info(
                        "Reached Maximum Number of Comments Limit : "
                        + str(settings.comment_limit)
                    )
                    logging.info(f"Used {str(ccount)}/{str(len(accepted_comments))} comments")
                    logging.info("=== Finished Processing Comments ===")
                    break
    else:
        logging.info("Skipping comments!")

    logging.info("===== Adding Background Clip =====")

    if settings.enable_background:
        background_filepath = str(Path(settings.background_directory,
                                       v.background))
        logging.info(f"Background : {background_filepath}")

        background_clip = (
            VideoFileClip(background_filepath)
            .set_start(tb)
            .volumex(settings.background_volume)
            .set_opacity(settings.background_opacity)
        )

        if settings.orientation == "portrait":
            print("Portrait mode, cropping and resizing!")
            background_clip = background_clip.crop(x1=1166.6,
                                                   y1=0,
                                                   x2=2246.6,
                                                   y2=1920)\
                                             .resize((settings.vertical_video_width,
                                                      settings.vertical_video_height))

        if background_clip.duration < v.duration:
            logging.debug("Looping Background")
            # background_clip = vfx.make_loopable(background_clip, cross=0)
            background_clip = vfx.loop(
                background_clip, duration=v.duration
            ).without_audio()
            logging.debug(
                "Looped Background Clip Duration : " + str(background_clip.duration)
            )
        else:
            logging.debug("Not Looping Background")
            background_clip = background_clip.set_duration(v.duration)
    else:
        logging.info("Background not enabled...")
        background_clip = ColorClip(
            size=(settings.video_width, settings.video_height),
            color=settings.background_colour
        ).set_duration(v.duration)

    v.clips.insert(0, background_clip)

    if settings.enable_overlay:
        logging.info("===== Adding Overlay Clip =====")
        clip_video_overlay = (
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
            logging.debug(
                "Looped Overlay Clip Duration : " + str(clip_video_overlay.duration)
            )
        else:
            logging.debug("Not Looping Overlay")
            clip_video_overlay = clip_video_overlay.set_duration(v.duration)

        v.clips.insert(1, clip_video_overlay)

    if settings.enable_newscaster and settings.newscaster_filepath:
        logging.info("===== Adding Newcaster Clip =====")
        logging.info(f"Newscaster File Path: { settings.newscaster_filepath }")
        clip_video_newscaster = (
            VideoFileClip(settings.newscaster_filepath)
            .set_position(settings.newscaster_position)
            .set_start(newcaster_start)
            .resize(settings.newcaster_size)
            .set_opacity(1)
            .volumex(0)
        )

        if settings.newscaster_remove_greenscreen:
            logging.info("===== Removing Newcaster Green Screen =====")
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
                "Looped Newscaster Clip Duration : "
                + str(clip_video_newscaster.duration)
            )
        else:
            logging.debug("Not Looping Newscaster")
            clip_video_newscaster = clip_video_newscaster.set_duration(
                v.duration - newcaster_start
            )

        v.clips.append(clip_video_newscaster)

    post_video = CompositeVideoClip(v.clips)

    v.filepath = str(
        Path(video_directory, "final.mp4")
    )

    v.json = str(
        Path(video_directory, "meta.json")
    )

    data = {
        "title": v.title,
        "description": v.description,
        "thumbnail": v.thumbnail,
        "file": v.filepath,
        "duration": v.duration,
        "height": settings.video_height,
        "width": settings.video_width,
    }

    with open(v.json, "w") as outfile:
        json.dump(data, outfile, indent=4)

    csvwriter = csvmgr.CsvWriter()

    row = {"id": v.meta.id,
           "title": v.title,
           "thumbnail": v.thumbnail,
           "file": v.filepath,
           "duration": v.duration,
           "compiled": "false",
           "uploaded": "false",
           }

    csvwriter.write_entry(row=row)

    if settings.enable_compilation:
        logging.info("===== Compiling Video Clip =====")
        logging.info(
            "Compiling video, \
            this takes a while, please be patient : )"
        )
        post_video.write_videofile(v.filepath, fps=24)

    else:
        logging.info("Skipping Video Compilation --enable_compilation passed")

    if settings.enable_compilation and settings.enable_upload:
        if exists("client_secret.json") and exists("credentials.storage"):
            if csvwriter.is_uploaded(v.meta.id):
                logging.info("Already uploaded according to data.csv")
            else:
                logging.info("===== Uploading Video Clip to YouTube =====")
                try:
                    youtube.publish(v)
                except Exception as e:
                    print(e)
                else:
                    csvwriter.set_uploaded(v.meta.id)
        else:
            logging.info("Skipping upload, missing either \
                         client_secret.json or credentials.storage file.")
    else:
        logging.info("Skipping Upload...")


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))
