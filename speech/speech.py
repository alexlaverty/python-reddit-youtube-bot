"""Transform text to speech."""
import logging
import os
import re
import subprocess  # noqa: S404
import textwrap
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any, List

import boto3
from gtts import gTTS
from moviepy.editor import AudioFileClip, concatenate_audioclips

import config
import config.settings as settings
from speech.streamlabs_polly import StreamlabsPolly
from speech.tiktok import TikTok
from utils.common import sanitize_text

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log", "w", "utf-8"), logging.StreamHandler()],
)


def process_speech_text(text: str) -> str:
    """Sanitize raw text.

    This will process raw text prior to converting it to speech, replacing
    common abbreviations with their full english version to ensure that the
    generated speech is intelligable.

    Args:
        text: Text to be sanitized.

    Returns:
        Updated text that has had common abbreviations converted to their
        full english equivalent.
    """
    text = text.replace(" AFAIK ", " as far as I know ")
    text = text.replace("AITA", " Am I The Asshole? ")
    text = text.replace(" AMA ", " Ask me anything ")
    text = text.replace(" ELI5 ", " Explain Like I'm Five ")
    text = text.replace(" IAMA ", " I am a ")
    text = text.replace("IANAD", " i am not a doctor ")
    text = text.replace("IANAL", " i am not a lawyer ")
    text = text.replace(" IMO ", " in my opinion ")
    text = text.replace(" NSFL ", " Not safe for life ")
    text = text.replace(" NSFW ", " Not safe for Work ")
    text = text.replace("NTA", " Not The Asshole ")
    text = text.replace(" SMH ", " Shaking my head ")
    text = text.replace("TD;LR", " too long didn't read ")
    text = text.replace("TDLR", " too long didn't read ")
    text = text.replace(" TIL ", " Today I Learned ")
    text = text.replace("YTA", " You're the asshole ")
    text = text.replace("SAHM", " stay at home mother ")
    text = text.replace("WIBTA", " would I be the asshole ")
    text = text.replace(" stfu ", " shut the fuck up ")
    text = text.replace(" OP ", " o p ")
    text = text.replace(" CB ", " choosing beggar ")
    text = text.replace("pettyrevenge", "petty revenge")
    text = text.replace("askreddit", "ask reddit")
    text = text.replace("twoxchromosomes", "two x chromosomes")
    text = text.replace("showerthoughts", "shower thoughts")
    text = text.replace("amitheasshole", "am i the asshole")
    text = text.replace("“", '"')
    text = text.replace("“", '"')
    text = text.replace("’", "'")
    text = text.replace("...", ".")
    text = text.replace("*", "")
    text = re.sub(r"(\[|\()[0-9]{1,2}\s*(m|f)?(\)|\])", "", text, flags=re.IGNORECASE)
    text = sanitize_text(text)
    return text


def create_audio(path: Path, text: str) -> Path:
    """Generate an audio file using text to speech.

    Args:
        path: Path to save the generated audio file to.
        text: Text to be converted to speech.

    Returns:
        Path to the generated audio file.
    """
    # logging.info(f"Generating Audio File : {text}")
    output_path = os.path.normpath(path)
    text: str = process_speech_text(text)
    if not os.path.exists(output_path) or not os.path.getsize(output_path) > 0:
        if settings.voice_engine == "polly":
            polly_client: Any = boto3.Session(
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                region_name="us-west-2",
            ).client("polly")

            response: Any = polly_client.synthesize_speech(
                Engine="neural", OutputFormat="mp3", Text=text, VoiceId="Matthew"
            )

            with open(output_path, "wb") as file:  # noqa: SCS109
                file.write(response["AudioStream"].read())

        if settings.voice_engine == "gtts":
            ttmp3: Any = gTTS(text, lang=settings.gtts_language, slow=False)
            ttmp3.save(output_path)

        if settings.voice_engine == "streamlabspolly":
            slp: StreamlabsPolly = StreamlabsPolly()
            speech_text_character_limit: int = 550

            if len(text) > speech_text_character_limit:
                logging.info(
                    "Text exceeds StreamlabsPolly limit, breaking up into chunks"
                )
                speech_chunks: List[Path] = []
                chunk_list: List[str] = textwrap.wrap(
                    text,
                    width=speech_text_character_limit,
                    break_long_words=True,
                    break_on_hyphens=False,
                )
                print(chunk_list)

                for count, chunk in enumerate(chunk_list):
                    print(count)
                    if chunk == "&#x200B;":
                        logging.info("Skip zero space character comment : %s", chunk)
                        continue

                    if chunk == "":
                        logging.info("Skipping blank comment")
                        continue

                    tmp_path: Path = f"{output_path}{count}"
                    slp.run(chunk, tmp_path)
                    speech_chunks.append(tmp_path)

                clips: List[AudioFileClip] = [AudioFileClip(c) for c in speech_chunks]
                final_clip: AudioFileClip = concatenate_audioclips(clips)
                final_clip.write_audiofile(output_path)
            else:
                print(text)
                slp.run(text, output_path)

        if settings.voice_engine == "edge-tts":
            print("+++ edge-tts +++")
            pattern = r'[^a-zA-Z0-9\s.,!?\'"-]'  # You can customize this pattern as needed.
            # Use the re.sub() function to replace any characters that don't match the pattern with an empty string.
            text = re.sub(pattern, '', text)
            text = re.sub(r'\n+', ' ', text)
            text = re.sub(r'\s+', ' ', text)

            print(text)
            subprocess.run(  # noqa: S603, S607
                [
                    "edge-tts",
                    "--voice",
                    settings.edge_tts_voice,
                    "--text",
                    f"'{text.strip()}'",
                    "--write-media",
                    output_path,
                ]
            )

        if settings.voice_engine == "balcon":
            balcon_cmd: List[Any] = ["balcon.exe", "-w", output_path, "-t", f"{text}"]
            subprocess.call(balcon_cmd)  # noqa: S603

        if settings.voice_engine == "tiktok":
            speech_text_character_limit: int = 200
            tt: TikTok = TikTok()

            if len(text) > speech_text_character_limit:
                logging.info(
                    "Text exceeds tiktok limit, \
                             breaking up into chunks"
                )
                speech_chunks: List[Path] = []
                chunk_list: List[str] = textwrap.wrap(
                    text,
                    width=speech_text_character_limit,
                    break_long_words=True,
                    break_on_hyphens=False,
                )
                print(chunk_list)

                for count, chunk in enumerate(chunk_list):
                    print(count)
                    if chunk == "&#x200B;":
                        logging.info("Skip zero space character comment : %s", chunk)
                        continue

                    if chunk == "":
                        logging.info("Skipping blank comment")
                        continue

                    tmp_path: Path = f"{path}{count}"
                    tt.run(chunk, tmp_path)
                    speech_chunks.append(tmp_path)

                clips: List[AudioFileClip] = [AudioFileClip(c) for c in speech_chunks]
                final_clip: AudioFileClip = concatenate_audioclips(clips)
                final_clip.write_audiofile(output_path)
            else:
                print(text)
                tt.run(text, output_path)
    else:
        logging.info("Audio file already exists : %s", output_path)

    logging.info("Created Audio File : %s", output_path)

    return output_path


if __name__ == "__main__":
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument(
        "--speech", default="Hello world this is a test.", help="Enter text for speech"
    )
    parser.add_argument(
        "--path", default="test_audio.mp3", help="Path to save audio file to"
    )
    args: Namespace = parser.parse_args()

    print(args.path)
    print(args.speech)
    create_audio(args.path, args.speech)
