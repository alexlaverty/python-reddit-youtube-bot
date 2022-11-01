import random
import requests
from requests.exceptions import JSONDecodeError

# from utils import settings
# from utils.voice import check_ratelimit
from requests import Response
import config.settings as settings
import time as pytime
from datetime import datetime
import sys
from time import sleep
import re
from utils.common import sanitize_text

if sys.version_info[0] >= 3:
    from datetime import timezone

voices = [
    "Brian",
    "Emma",
    "Russell",
    "Joey",
    "Matthew",
    "Joanna",
    "Kimberly",
    "Amy",
    "Geraint",
    "Nicole",
    "Justin",
    "Ivy",
    "Kendra",
    "Salli",
    "Raveena",
]


# valid voices https://lazypy.ro/tts/


def sleep_until(time):
    """
    Pause your program until a specific end time.
    'time' is either a valid datetime object or unix timestamp in seconds (i.e. seconds since Unix epoch)
    """
    end = time

    # Convert datetime to unix timestamp and adjust for locality
    if isinstance(time, datetime):
        # If we're on Python 3 and the user specified a timezone, convert to UTC and get the timestamp.
        if sys.version_info[0] >= 3 and time.tzinfo:
            end = time.astimezone(timezone.utc).timestamp()
        else:
            zoneDiff = (
                pytime.time() - (datetime.now() - datetime(1970, 1, 1)).total_seconds()
            )
            end = (time - datetime(1970, 1, 1)).total_seconds() + zoneDiff

    # Type check
    if not isinstance(end, (int, float)):
        raise Exception("The time parameter is not a number or datetime object")

    # Now we wait
    while True:
        now = pytime.time()
        diff = end - now

        #
        # Time is up!
        #
        if diff <= 0:
            break
        else:
            # 'logarithmic' sleeping to minimize loop iterations
            sleep(diff / 2)


def check_ratelimit(response: Response):
    """
    Checks if the response is a ratelimit response.
    If it is, it sleeps for the time specified in the response.
    """
    if response.status_code == 429:
        try:
            time = int(response.headers["X-RateLimit-Reset"])
            print(f"Ratelimit hit, sleeping...")
            sleep_until(time)
            return False
        except KeyError:  # if the header is not present, we don't know how long to wait
            return False

    return True


class StreamlabsPolly:
    def __init__(self):
        self.url = "https://streamlabs.com/polly/speak"
        self.max_chars = 550
        self.voices = voices

    def run(self, text, filepath, random_voice: bool = False):
        if random_voice:
            voice = self.randomvoice()
        else:
            if not settings.streamlabs_polly_voice:
                raise ValueError(
                    f"Please set the config variable streamlabs_polly_voice to a valid voice. options are: {voices}"
                )
            voice = str(settings.streamlabs_polly_voice).capitalize()
        text = sanitize_text(text)
        body = {"voice": voice, "text": text, "service": "polly"}
        response = requests.post(self.url, data=body)
        if not check_ratelimit(response):
            self.run(text, filepath, random_voice)

        else:
            try:
                voice_data = requests.get(response.json()["speak_url"])
                with open(filepath, "wb") as f:
                    f.write(voice_data.content)
            except (KeyError, JSONDecodeError):
                try:
                    if response.json()["error"] == "No text specified!":
                        raise ValueError("Please specify a text to convert to speech.")
                except (KeyError, JSONDecodeError):
                    print("Error occurred calling Streamlabs Polly")

    def randomvoice(self):
        return random.choice(self.voices)
