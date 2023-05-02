"""TikTok text to speech convertor."""
import base64
from random import SystemRandom
import urllib.parse
from pathlib import Path
from typing import Dict, List

import requests
from requests import Response, Session
from requests.adapters import HTTPAdapter, Retry
from requests.exceptions import SSLError

import config.settings as settings

# from profanity_filter import ProfanityFilter
# pf = ProfanityFilter()
# Code by @JasonLovesDoggo
# https://twitter.com/scanlime/status/1512598559769702406

nonhuman = [  # DISNEY VOICES
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    # ENGLISH VOICES
]

human = [
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",
]
voices = nonhuman + human

noneng = [
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    # AMERICA VOICES
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # ASIA VOICES
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
]


# good_voices = {
#     'good': ['en_us_002', 'en_us_006'],
#     'ok': ['en_au_002', 'en_uk_001']}
# less en_us_stormtrooper more less en_us_rocket en_us_ghostface


class TikTok:  # TikTok Text-to-Speech Wrapper
    """Text to Speech wrapper for TikTok."""

    def __init__(self):
        """Initialise a new TikTok text to speech generator."""
        self.URI_BASE: str = (
            "https://api16-normal-useast5.us.tiktokv.com"
            "/media/api/text/speech/invoke/?text_speaker="
        )
        self.max_chars: int = 300
        self.voices: Dict[str, List[str]] = {
            "human": human,
            "nonhuman": nonhuman,
            "noneng": noneng,
        }

    def run(self, text: str, filepath: Path, random_voice: bool = False) -> None:
        """Convert text to an audio clip using a random tik-tok styled voice.

        Args:
            text: The text to be converted to speech.
            filepath: Path to save the generated audio clip to.
            random_voice: If `true`, selects a random voice, otherwise selects
                the default tiktok voice.
        """
        # if censor:
        #     req_text = pf.censor(req_text)
        #     pass
        rnd: SystemRandom = SystemRandom()
        voice: str = (
            self.randomvoice()
            if random_voice
            else (settings.tiktok_voice or rnd.choice(self.voices["human"]))
        )
        try:
            text: str = urllib.parse.quote(text)
            print(len(text))
            tt_uri: str = f"{self.URI_BASE}{voice}&req_text={text}&speaker_map_type=0"
            print(tt_uri)
            r: Response = requests.post(tt_uri, timeout=120)
        except SSLError:
            # https://stackoverflow.com/a/47475019/18516611
            session: Session = Session()
            retry: Retry = Retry(connect=3, backoff_factor=0.5)
            adapter: HTTPAdapter = HTTPAdapter(max_retries=retry)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            r: Response = session.post(
                f"{self.URI_BASE}{voice}&req_text={text}&speaker_map_type=0"
            )
        # print(r.text)
        vstr: str = [r.json()["data"]["v_str"]][0]
        b64d: bytes = base64.b64decode(vstr)

        with open(filepath, "wb") as out:  # noqa: SCS109
            out.write(b64d)

    def randomvoice(self) -> str:
        """Select a random voice.

        Returns:
            A randomly chosen human voice.
        """
        rnd: SystemRandom = SystemRandom()
        return rnd.choice(self.voices["human"])


if __name__ == "__main__":
    tt: TikTok = TikTok()
    text_to_say: str = "Hello world this is some spoken text"
    print(str(len(text_to_say)))
    tt.run(text_to_say, "tiktok_test.mp3")
