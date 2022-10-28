import subprocess
import logging
import os
import config.settings as settings
import boto3
import config
from gtts import gTTS
import argparse


from speech.streamlabs_polly import StreamlabsPolly
from speech.tiktok import TikTok

import textwrap
from moviepy.editor import AudioFileClip, concatenate_audioclips

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("debug.log", "w", "utf-8"), logging.StreamHandler()],
)


def process_speech_text(text):
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
    # req_text = text.replace("+", "plus")
    # req_text = req_text.replace(" ", "+")
    # req_text = req_text.replace("&", "and")
    return text


def create_audio(path, text):
    # logging.info(f"Generating Audio File : {text}")
    text = process_speech_text(text)
    if not os.path.exists(path):

        if settings.voice_engine == "polly":
            polly_client = boto3.Session(
                aws_access_key_id=config.aws_access_key_id,
                aws_secret_access_key=config.aws_secret_access_key,
                region_name="us-west-2",
            ).client("polly")

            response = polly_client.synthesize_speech(
                Engine="neural", OutputFormat="mp3", Text=text, VoiceId="Matthew"
            )

            file = open(path, "wb")
            file.write(response["AudioStream"].read())
            file.close()

        if settings.voice_engine == "gtts":
            ttmp3 = gTTS(text)
            ttmp3.save(path)

        if settings.voice_engine == "streamlabspolly":
            slp = StreamlabsPolly()
            speech_text_character_limit = 550

            if len(text) > speech_text_character_limit:
                logging.info(
                    "Text exceeds StreamlabsPolly limit, breaking up into chunks"
                )
                speech_chunks = []
                chunk_list = textwrap.wrap(
                    text,
                    width=speech_text_character_limit,
                    break_long_words=True,
                    break_on_hyphens=False,
                )

                print(chunk_list)

                for count, chunk in enumerate(chunk_list):
                    print(count)
                    if chunk == "&#x200B;":
                        logging.info("Skip zero space character comment : " + chunk)
                        continue

                    if chunk == "":
                        logging.info("Skipping blank comment")
                        continue

                    tmp_path = f"{path}{count}"
                    slp.run(chunk, tmp_path)
                    speech_chunks.append(tmp_path)

                clips = [AudioFileClip(c) for c in speech_chunks]
                final_clip = concatenate_audioclips(clips)
                final_clip.write_audiofile(path)
            else:
                print(text)
                slp.run(text, path)

        if settings.voice_engine == "edge-tts":
            subprocess.run(
                [
                    "edge-tts",
                    "--voice",
                    settings.edge_tts_voice,
                    "--text",
                    f"'{text}'",
                    "--write-media",
                    path,
                ]
            )

        if settings.voice_engine == "balcon":
            result = subprocess.call(["balcon.exe", "-w", path, "-t", f"{text}"])

        if settings.voice_engine == "tiktok":
            speech_text_character_limit = 200
            tt = TikTok()

            if len(text) > speech_text_character_limit:
                logging.info(
                    "Text exceeds tiktok limit, \
                             breaking up into chunks"
                )
                speech_chunks = []
                chunk_list = textwrap.wrap(
                    text,
                    width=speech_text_character_limit,
                    break_long_words=True,
                    break_on_hyphens=False,
                )

                print(chunk_list)

                for count, chunk in enumerate(chunk_list):
                    print(count)
                    if chunk == "&#x200B;":
                        logging.info("Skip zero space character comment : " + chunk)
                        continue

                    if chunk == "":
                        logging.info("Skipping blank comment")
                        continue

                    tmp_path = f"{path}{count}"
                    tt.run(chunk, tmp_path)
                    speech_chunks.append(tmp_path)

                clips = [AudioFileClip(c) for c in speech_chunks]
                final_clip = concatenate_audioclips(clips)
                final_clip.write_audiofile(path)
            else:
                print(text)
                tt.run(text, path)

    else:
        logging.info(f"Audio file already exists : {path}")

    logging.info(f"Created Audio File : {path}")

    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--speech", default="Hello world this is a test.", help="Enter text for speech"
    )
    parser.add_argument(
        "--path", default="test_audio.mp3", help="Path to save audio file to"
    )
    args = parser.parse_args()
    print(args.path)
    print(args.speech)
    create_audio(args.path, args.speech)
