"""Functions used to download random images associated with a reddit post.

This module also contains functions that can take those images and generate
a series of video clips that can be spliced together to form the final video.
"""
import logging
import os
import sys
from pathlib import Path

# from nltk.corpus import stopwords
from random import SystemRandom
from typing import Any, List

from moviepy.editor import CompositeVideoClip, ImageClip, TextClip
from PIL import Image

import config.settings as settings
import thumbnail.lexica as lexica
from utils.common import random_rgb_colour, sanitize_text

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log", "w", "utf-8"), logging.StreamHandler()],
)


def apply_black_gradient(
    path_in: Path,
    path_out: Path = "out.png",
    gradient: float = 1.0,
    initial_opacity: float = 1.0,
) -> None:
    """Apply a black gradient to the image, going from left to right.

    Args:
        path_in: Path to image to apply gradient to.
        path_out: Path to save result to (default 'out.png').
        gradient: Gradient of the gradient, should be non-negative (default 1.0).
            if gradient = 0., the image is black;
            if gradient = 1., the gradient smoothly varies over the full width;
            if gradient > 1., the gradient terminates before the end of the width;
        initial_opacity: Scales the initial opacity of the gradient, eg: on the
            far left of the image (default 1.0).

            Should be between 0.0 and 1.0. Values between 0.9-1.0 generally
            give good results.
    """
    # get image to operate on
    input_im: Image = Image.open(path_in)
    if input_im.mode != "RGBA":
        input_im = input_im.convert("RGBA")
    width, height = input_im.size

    # create a gradient that
    # starts at full opacity * initial_value
    # decrements opacity by gradient * x / width
    alpha_gradient: Image = Image.new("L", (width, 1), color=0xFF)
    for x in range(width):
        a: int = int((initial_opacity * 255.0) * (1.0 - gradient * float(x) / width))
        if a > 0:
            alpha_gradient.putpixel((x, 0), a)
        else:
            alpha_gradient.putpixel((x, 0), 0)
        # print '{}, {:.2f}, {}'.format(x, float(x) / width, a)
    alpha: Any = alpha_gradient.resize(input_im.size)

    # create black image, apply gradient
    black_im: Image = Image.new("RGBA", (width, height), color=0)  # i.e. black
    black_im.putalpha(alpha)

    # make composite with original image
    output_im: Image = Image.alpha_composite(input_im, black_im)
    output_im.save(path_out, "PNG")

    return


def get_font_size(length: int) -> int:
    """Select a preset font size based on the amount of available space.

    Args:
        length: The amount of horizontal space available to insert text.

    Returns:
        A suggested font size.
    """
    fontsize = 50
    lineheight = 60

    if length < 10:
        fontsize = 190

    if length >= 10 and length < 20:
        fontsize = 150

    if length >= 20 and length < 30:
        fontsize = 150

    if length >= 30 and length < 40:
        fontsize = 130

    if length >= 40 and length < 50:
        fontsize = 110

    if length >= 50 and length < 60:
        fontsize = 100

    if length >= 60 and length < 70:
        fontsize = 90

    if length >= 70 and length < 80:
        fontsize = 85

    if length >= 80 and length < 90:
        fontsize = 90

    if length >= 90 and length < 100:
        fontsize = 80

    logging.debug("Title Length       : %s", length)
    logging.debug("Setting Fontsize   : %s", fontsize)
    logging.debug("Setting Lineheight : %s", lineheight)

    return fontsize, lineheight


def generate(
    video_directory: Path,
    subreddit: str,
    title: str,
    number_of_thumbnails: int = 1,
) -> List[Path]:
    """Generate a series of thumbnails to be included in the generated video.

    The images will be randomly selected by lexica using the name of the
    subreddit, and post title as keywords to find relevant images.

    Args:
        video_directory: Path to save the images to.
        subreddit: Name of the subreddit that contains the post.
        title: Name of the reddit post.
        number_of_thumbnails: Number of relevant images to download
            (default=1).

    Returns:
        A list of paths where the downloaded images can be found.
    """
    logging.info("========== Generating Thumbnail ==========")

    # image_path = str(Path(video_directory, "lexica.png").absolute())

    title = sanitize_text(title).strip()

    # Get rid of double spaces
    title = title.replace("  ", " ")
    title = title.replace("’", "")

    logging.info(title)

    if settings.thumbnail_image_source == "random":
        rnd: SystemRandom = SystemRandom()
        random_image = rnd.choice(os.listdir(settings.images_directory))
        random_image_filepath = str(
            Path(settings.images_directory, random_image).absolute()
        )
        images = [random_image_filepath]

    if settings.thumbnail_image_source == "lexica":
        images = lexica.get_images(
            video_directory, title, number_of_images=number_of_thumbnails
        )

    thumbnails = []

    if images:
        for index, image in enumerate(images):
            thumbnail = create_thumbnail(
                video_directory, subreddit, title, image, index
            )
            thumbnails.append(thumbnail)

    return thumbnails


def create_thumbnail(
    video_directory: Path, subreddit: str, title: str, image: Path, index: int = 0
) -> Path:
    """Generate a thumbnail image for the video.

    Args:
        video_directory: Path to save the thumbnail in.
        subreddit: Name of the subreddit that the post was made in.
        title: Name of the Reddit post.
        image: Path to the image used to create the thumbnail.
        index: Image offset.

    Returns:
        The full path to the updated video containing the thumbnail.
    """
    clips: List[Any] = []

    thumbnail_path: Path = Path(
        video_directory, f"thumbnail_{str(index)}.png"
    ).absolute()
    if thumbnail_path.exists():
        logging.info("Thumbnail already exists : %s", thumbnail_path)
        return thumbnail_path

    border_width: int = 20
    height: int = 720 - (border_width * 2)
    width: int = 1280 - (border_width * 2)

    background_clip: Any = TextClip(
        "", size=(width, height), bg_color="#000000", method="caption"
    )

    #  .margin(border_width, color=random_rgb_colour())

    clips.append(background_clip)

    gradient_out: Path = Path(video_directory, "gradient.png").absolute()

    if settings.enable_thumbnail_image_gradient:
        apply_black_gradient(
            image, path_out=gradient_out, gradient=1.3, initial_opacity=0.9
        )
        image = gradient_out

    # img_width = width / 2

    img_clip = (
        ImageClip(image)
        .resize(height=height)
        .set_position(("right", "center"))
        .set_opacity(1)
    )

    img_clip = img_clip.set_position(("right", "center"))

    # img_clip = img_clip.set_position((width - img_clip.w , 0 + border_width))

    clips.append(img_clip)

    def get_text_clip(text: str, fs: int, txt_color: str = "#FFFFFF") -> TextClip:
        """Generate a video containing text.

        Args:
            text: The text to include in the video.
            fs: The font-size, expressed as an integer.
            txt_color: Colour to be used for the text, expressed in hex format.

        Returns:
            The generated video clip containing the specified text.
        """
        txt_clip = TextClip(
            text,
            fontsize=fs,
            color=txt_color,
            align="west",
            font="Impact",
            stroke_color="#000000",
            stroke_width=3,
            method="caption",
            size=(settings.thumbnail_text_width, 0),
        )
        return txt_clip

    # fontsize = 40
    title = title.replace("’", "")
    fontsize, lineheight = get_font_size(len(title))
    logging.info("Title Length : %s", len(title))
    logging.info("Optimising Font Size : ")
    sys.stdout.write(fontsize)

    while True:
        previous_fontsize: int = fontsize
        fontsize += 1
        txt_clip: TextClip = get_text_clip(title.upper(), fontsize)
        sys.stdout.write(".")
        if txt_clip.h > height:
            optimal_font_size: int = previous_fontsize
            print(optimal_font_size)
            break

    word_height: TextClip = get_text_clip(
        "Hello", fs=optimal_font_size, txt_color="#FFFFFF"
    )
    # word_height = TextClip(
    #         "Hello",
    #         fontsize=optimal_font_size,
    #         align="center",
    #         font="Impact",
    #         stroke_color="#000000",
    #         stroke_width=3,
    #     )

    txt_y: int = 0
    txt_x: int = 15

    words: List[str] = title.upper().split(" ")
    word_color: str = "#FFFFFF"
    line_number: int = 1
    space_width: int = 9
    line_colours: List[str] = [
        "#46F710",
        "#F9CD10",
        "#04FF74",
        "#FF5252",
        "#FF7545",
        "#09C1F9",
        "#EFFF00",
        "#E7AD61",
        "#00677B",
    ]

    rnd = SystemRandom()
    rnd.shuffle(line_colours)

    for word in words:
        if (line_number % 2) == 0:
            word_color: str = line_colours[line_number]
        else:
            word_color: str = "#FFFFFF"

        # txt_clip = get_text_clip(word,
        #                          optimal_font_size,
        #                          txt_color=word_color)\
        #     .set_position((txt_x, txt_y))

        txt_clip: TextClip = TextClip(
            word,
            fontsize=optimal_font_size,
            color=word_color,
            align="west",
            font="Impact",
            stroke_color="#000000",
            stroke_width=3,
            method="caption",
        ).set_position((txt_x, txt_y))

        current_text_width: int = txt_x + space_width + txt_clip.w

        if current_text_width > settings.thumbnail_text_width:
            txt_x = 15
            txt_y += word_height.h * 0.85
            line_number += 1

            if (line_number % 2) == 0:
                word_color: str = line_colours[line_number]
            else:
                word_color: str = "#FFFFFF"

            # txt_clip = get_text_clip(word,
            #                          fs=optimal_font_size,
            #                          txt_color=word_color)\
            #     .set_position((txt_x, txt_y))
            txt_clip: TextClip = TextClip(
                word,
                fontsize=optimal_font_size,
                color=word_color,
                align="west",
                font="Impact",
                stroke_color="#000000",
                stroke_width=3,
                method="caption",
            ).set_position((txt_x, txt_y))

        clips.append(txt_clip)
        txt_x += txt_clip.w + space_width

    txt_clip = txt_clip.set_duration(10)
    txt_clip = txt_clip.set_position(("center", "center"))

    final_video: CompositeVideoClip = CompositeVideoClip(clips)
    final_video = final_video.margin(border_width, color=random_rgb_colour())

    logging.info("Saving Thumbnail to : %s", thumbnail_path)
    final_video.save_frame(thumbnail_path, 1)
    return thumbnail_path


if __name__ == "__main__":
    from argparse import ArgumentParser, Namespace

    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        help="Specify directory to save thumbnail image to",
        default=".",
    )
    parser.add_argument(
        "-s", "--subreddit", help="Specify subreddit", default="r/AskReddit"
    )
    parser.add_argument(
        "-t",
        "--title",
        help="Specify Post Title",
        default="What's your most gatekeeping culinary opinion?",
    )
    parser.add_argument(
        "-i",
        "--image",
        help="Specify Thumbnail Image",
        default=Path(settings.images_directory, "woman.jpg").absolute(),
    )

    args: Namespace = parser.parse_args()

    create_thumbnail(".", "Something", args.title, args.image, index=0)

    # generate(args.directory,
    #          args.subreddit,
    #          args.title,
    #          number_of_thumbnails=1)
