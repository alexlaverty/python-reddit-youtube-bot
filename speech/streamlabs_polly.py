"""Polly text to speech convertor."""
import sys
import time as pytime
from datetime import datetime
from pathlib import Path
from random import SystemRandom
from time import sleep
from typing import Dict, List, Union

import requests

# from utils import settings
# from utils.voice import check_ratelimit
from requests import Response
from requests.exceptions import JSONDecodeError

import config.settings as settings
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


def sleep_until(time: Union[int, datetime]) -> None:
    """Pause until a specific end time.

    Args:
        time: Either a valid datetime object or unix timestamp in seconds
            (i.e. seconds since Unix epoch).
    """
    end: int = time

    # Convert datetime to unix timestamp and adjust for locality
    if isinstance(time, datetime):
        # If we're on Python 3 and the user specified a timezone, convert to
        # UTC and get the timestamp.
        if sys.version_info[0] >= 3 and time.tzinfo:
            end: datetime = time.astimezone(timezone.utc).timestamp()
        else:
            zone_diff: float = (
                pytime.time() - (datetime.now() - datetime(1970, 1, 1)).total_seconds()
            )
            end: float = (time - datetime(1970, 1, 1)).total_seconds() + zone_diff

    # Type check
    if not isinstance(end, (int, float)):
        raise Exception("The time parameter is not a number or datetime object")

    # Now we wait
    while True:
        now: float = pytime.time()
        diff: float = end - now

        # Time is up!
        if diff <= 0:
            break
        else:
            # 'logarithmic' sleeping to minimize loop iterations
            sleep(diff / 2)


def check_ratelimit(response: Response) -> bool:
    """Check if the rate limit has been hit.

    If it has, sleep for the time specified in the response.

    Args:
        response: The HTTP response to be examined.

    Returns:
        `True` if the rate limit has been reached, otherwise `False`.
    """
    if response.status_code == 429:
        try:
            time: int = int(response.headers["X-RateLimit-Reset"])
            print("Ratelimit hit, sleeping...")
            sleep_until(time)
            return False
        except KeyError:  # if the header is not present, we don't know how long to wait
            return False

    return True


class StreamlabsPolly:
    """Polly text to speech convertor."""

    def __init__(self):
        """Initialise a new Polly text to speech convertor."""
        self.url: str = "https://streamlabs.com/polly/speak"
        self.max_chars: int = 550
        self.voices: List[str] = voices

    def run(self, text: str, filepath: Path, random_voice: bool = False) -> None:
        """Convert text to an audio clip using a random Polly voice.

        Args:
            text: The text to be converted to speech.
            filepath: Path to save the generated audio clip to.
            random_voice: If `true`, selects a random voice, otherwise selects
                the default polly voice.
        """
        if random_voice:
            voice: str = self.randomvoice()
        else:
            if not settings.streamlabs_polly_voice:
                raise ValueError(
                    f"Please set the config variable streamlabs_polly_voice \
                        to a valid voice. options are: {voices}"
                )
            voice: str = str(settings.streamlabs_polly_voice).capitalize()
        text: str = sanitize_text(text)
        body: Dict[str, List[str]] = {"voice": voice, "text": text, "service": "polly"}
        response: Response = requests.post(self.url, data=body, timeout=120)
        if not check_ratelimit(response):
            self.run(text, filepath, random_voice)
        else:
            try:
                voice_data: Response = requests.get(
                    response.json()["speak_url"], timeout=120
                )
                with open(filepath, "wb") as f:  # noqa: SCS109
                    f.write(voice_data.content)
            except (KeyError, JSONDecodeError):
                try:
                    if response.json()["error"] == "No text specified!":
                        raise ValueError("Please specify a text to convert to speech.")
                except (KeyError, JSONDecodeError):
                    print("Error occurred calling Streamlabs Polly")

    def randomvoice(self) -> str:
        """Select a random Polly voice.

        Returns:
            The name of a randomly selected Polly voice.
        """
        rnd: SystemRandom() = SystemRandom()
        return rnd.choice(self.voices)
