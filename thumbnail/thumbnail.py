from moviepy.editor import CompositeVideoClip, TextClip, ImageClip

from pathlib import Path
# from nltk.corpus import stopwords
import random
import logging
import config.settings as settings
import thumbnail.lexica as lexica
from utils.common import random_rgb_colour, sanitize_text
import sys
import os
from PIL import Image

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log", "w", "utf-8"),
              logging.StreamHandler()],
)


def apply_black_gradient(path_in, path_out='out.png',
                         gradient=1., initial_opacity=1.):
    """
    Applies a black gradient to the image, going from left to right.

    Arguments:
    ---------
        path_in: string
            path to image to apply gradient to
        path_out: string (default 'out.png')
            path to save result to
        gradient: float (default 1.)
            gradient of the gradient; should be non-negative;
            if gradient = 0., the image is black;
            if gradient = 1., the gradient smoothly varies over the full width;
            if gradient > 1., the gradient terminates before the end of the width;
        initial_opacity: float (default 1.)
            scales the initial opacity of the gradient (i.e. on the far left of the image);
            should be between 0. and 1.; values between 0.9-1. give good results
    """

    # get image to operate on
    input_im = Image.open(path_in)
    if input_im.mode != 'RGBA':
        input_im = input_im.convert('RGBA')
    width, height = input_im.size

    # create a gradient that
    # starts at full opacity * initial_value
    # decrements opacity by gradient * x / width
    alpha_gradient = Image.new('L', (width, 1), color=0xFF)
    for x in range(width):
        a = int((initial_opacity * 255.) * (1. - gradient * float(x)/width))
        if a > 0:
            alpha_gradient.putpixel((x, 0), a)
        else:
            alpha_gradient.putpixel((x, 0), 0)
        # print '{}, {:.2f}, {}'.format(x, float(x) / width, a)
    alpha = alpha_gradient.resize(input_im.size)

    # create black image, apply gradient
    black_im = Image.new('RGBA', (width, height), color=0)  # i.e. black
    black_im.putalpha(alpha)

    # make composite with original image
    output_im = Image.alpha_composite(input_im, black_im)
    output_im.save(path_out, 'PNG')

    return


def get_font_size(length):

    fontsize = 50
    lineheight = 60

    if length < 10:
        fontsize = 190

    if length >= 10 and length < 20:
        fontsize = 140

    if length >= 20 and length < 30:
        fontsize = 170

    if length >= 30 and length < 40:
        fontsize = 120

    if length >= 40 and length < 50:
        fontsize = 110

    if length >= 50 and length < 60:
        fontsize = 110

    if length >= 60 and length < 70:
        fontsize = 90

    if length >= 70 and length < 80:
        fontsize = 85

    if length >= 80 and length < 90:
        fontsize = 90

    if length >= 90 and length < 100:
        fontsize = 80

    logging.debug(f"Title Length       : {length}")
    logging.debug(f"Setting Fontsize   : {fontsize} ")
    logging.debug(f"Setting Lineheight : {lineheight} ")

    return fontsize, lineheight


def generate(
    video_directory,
    subreddit,
    title,
    number_of_thumbnails=1,
):
    logging.info("========== Generating Thumbnail ==========")

    # image_path = str(Path(video_directory, "lexica.png").absolute())

    title = sanitize_text(title).strip()

    # Get rid of double spaces
    title = title.replace("  ", " ")

    logging.info(title)

    if settings.thumbnail_image_source == "random":
        random_image = random.choice(os.listdir(settings.images_directory))
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


def create_thumbnail(video_directory, subreddit, title, image, index=0):
    clips = []
    thumbnail_path = str(
        Path(video_directory, f"thumbnail_{str(index)}.png").absolute()
    )
    if os.path.exists(thumbnail_path):
        logging.info(f"Thumbnail already exists : {thumbnail_path}")
        return thumbnail_path

    height = 720
    width = 1280
    border_width = 15

    background_clip = TextClip(
        "", size=(width, height), bg_color="#000000", method="caption"
    )
    #  .margin(border_width, color=random_rgb_colour())

    clips.append(background_clip)

    gradient_out = str(
        Path(video_directory, "gradient.png").absolute()
    )

    if settings.enable_thumbnail_image_gradient:
        apply_black_gradient(image, path_out=gradient_out,
                             gradient=1.3, initial_opacity=0.9)
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

    def get_text_clip(fs, txt_color="#FFFFFF"):
        txt_clip = TextClip(
            title.upper(),
            fontsize=fs,
            color=txt_color,
            align="west",
            font="Impact",
            #bg_color="#ADD8E6",
            stroke_color="#000000",
            stroke_width=2,
            method="caption",
            size=(settings.thumbnail_text_width, 0),
        ).set_position((10 + border_width, "center"))
        return txt_clip

    # fontsize = 40
    fontsize, lineheight = get_font_size(len(title))
    logging.info(f"Optimising Font Size : {str(len(title))}")
    sys.stdout.write(str(fontsize))

    while True:
        previous_fontsize = fontsize
        fontsize += 1
        txt_clip = get_text_clip(fontsize)
        sys.stdout.write(".")
        if txt_clip.h > height:
            optimal_font_size = previous_fontsize
            print(optimal_font_size)
            break

    word_height = TextClip(
            "Hello",
            fontsize=optimal_font_size,
            font="Impact",
            method="caption",
        )

    txt_y = 0
    txt_x = 0

    words = title.upper().split(" ")
    word_color = "#FFFFFF"
    line_number = 1
    line_colours = ["#46F710",
                    "#F9CD10",
                    "#04FF74",
                    "#FF5252",
                    "#FF7545",
                    "#09C1F9",
                    "#EFFF00",
                    "#E7AD61",
                    "#00677B"]
    random.shuffle(line_colours)

    for word in words:

        if (line_number % 2) == 0:
            word_color = line_colours[line_number]
        else:
            word_color = "#FFFFFF"

        txt_clip = TextClip(
            word,
            fontsize=optimal_font_size,
            color=word_color,
            align="center",
            font="Impact",
            stroke_color="#000000",
            stroke_width=3,
            method="caption",
        ).set_position((txt_x, txt_y))

        current_text_width = txt_x + txt_clip.w

        if current_text_width > settings.thumbnail_text_width:
            txt_x = 0
            txt_y += word_height.h
            line_number += 1

            if (line_number % 2) == 0:
                word_color = line_colours[line_number]
            else:
                word_color = "#FFFFFF"

            txt_clip = TextClip(
                word,
                fontsize=optimal_font_size,
                color=word_color,
                align="center",
                font="Impact",
                stroke_color="#000000",
                stroke_width=3,
                method="caption",
            ).set_position((txt_x, txt_y))

        clips.append(txt_clip)
        txt_x += txt_clip.w + 15

    txt_clip = txt_clip.set_duration(10)
    txt_clip = txt_clip.set_position(("center", "center"))

    final_video = CompositeVideoClip(clips)
    final_video = final_video.margin(border_width, color=random_rgb_colour())
    logging.info("Saving Thumbnail to : " + thumbnail_path)
    final_video.save_frame(thumbnail_path, 1)
    return thumbnail_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
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
        default=str(Path(settings.images_directory, "woman.jpg").absolute()),
    )
    args = parser.parse_args()

    generate(args.directory,
             args.subreddit,
             args.title,
             number_of_thumbnails=1)
