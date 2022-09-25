from pathlib import Path
from urllib.request import Request, urlopen
import json 
import logging 
import os 
import requests
import settings 
import time
import urllib  

def get_image(file_path, sentence, number_of_images=1):

    if settings.download_enabled:
        if not os.path.exists(file_path):
            safe_query = urllib.parse.quote(sentence.strip())
            lexica_url=f"https://lexica.art/api/v1/search?q={safe_query}"
            logging.info(f"Downloading Image : {str(id)} - {sentence}")
            r = requests.get(lexica_url)
            j = json.loads(r.text)
            image_url = j["images"][0]['src']  
            req = Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
            raw_img = urlopen(req).read()
            f = open(file_path, 'wb')
            f.write(raw_img)
            f.close()
            # Sleeping to prevent being Rate Limited
            time.sleep(5)
        else:
            logging.info(f"Image already exists : {str(id)} - {sentence}")
    else:
        logging.info("Downloading Images Set to False.......")

    return file_path