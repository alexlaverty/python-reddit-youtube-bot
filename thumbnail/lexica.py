"""Functions used to process and download images."""
import json
import logging
import os
import time
import urllib
from pathlib import Path
from typing import List
from urllib.request import Request, Response, urlopen

import requests

import config.settings as settings


def download_image(url: str, file_path: Path) -> None:
    """Download a single image.

    Args:
        url: URL to download the image from.
        file_path: Path to save the image to.
    """
    req: Request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    # FIXME: This is a potential security issue
    raw_img = urlopen(req).read()  # noqa: S310

    with open(file_path, "wb") as f:  # noqa: SCS109
        f.write(raw_img)
        f.close()

    # Sleeping to prevent being Rate LimitedF
    time.sleep(5)


def get_images(
    folder_path: Path, sentence: str, number_of_images: int = 1
) -> List[Path]:
    """Download random images that are relevant to the provided text.

    Args:
      folder_path: Path to save the images.
      sentence: Text used to find relevant images.
      number_of_images: Number of images to be downloaded.

    Returns:
        A list of files path to the downloaded images.
    """
    images: List[Path] = []

    if settings.lexica_download_enabled:
        if number_of_images > 0:
            safe_query: str = urllib.parse.quote(sentence.strip())
            lexica_url: str = f"https://lexica.art/api/v1/search?q={safe_query}"
            logging.info("Downloading Image From Lexica : %s", sentence)
            try:
                r: Response = requests.get(lexica_url, timeout=120)
                j: object = json.loads(r.text)
            except Exception:
                print("Error Retrieving Lexica Images")
                pass
                return

            for num in range(0, number_of_images):
                image_path: Path = Path(folder_path, f"lexica_{num}.png")
                if not os.path.exists(image_path):
                    image_url: str = j["images"][num]["src"]
                    download_image(image_url, image_path)
                else:
                    logging.info("Image already exists : %s - %s", id, sentence)
                images.append(image_path)
    else:
        logging.info("Downloading Images Set to False.......")

    return images
