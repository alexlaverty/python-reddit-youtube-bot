from pathlib import Path
from urllib.request import Request, urlopen
import json
import logging
import os
import requests
import config.settings as settings
import time
import urllib


def download_image(url, file_path):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw_img = urlopen(req).read()
    f = open(file_path, "wb")
    f.write(raw_img)
    f.close()
    # Sleeping to prevent being Rate LimitedF
    time.sleep(5)


def get_images(folder_path, sentence, number_of_images=1):
    images = []
    if settings.download_enabled:
        if number_of_images > 0:
            safe_query = urllib.parse.quote(sentence.strip())
            lexica_url = f"https://lexica.art/api/v1/search?q={safe_query}"
            logging.info(f"Downloading Image From Lexica : {sentence}")
            try:
                r = requests.get(lexica_url)
                j = json.loads(r.text)
            except:
                print("Error Retrieving Lexica Images")
                pass
                return

            for num in range(0, number_of_images):

                image_path = str(Path(folder_path, f"lexica_{num}.png"))

                if not os.path.exists(image_path):
                    image_url = j["images"][num]["src"]
                    download_image(image_url, image_path)
                else:
                    logging.info(
                        f"Image already exists : \
                                 {str(id)} - {sentence}"
                    )
                images.append(image_path)
    else:
        logging.info("Downloading Images Set to False.......")

    return images
