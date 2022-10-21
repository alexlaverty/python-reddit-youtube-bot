import subprocess
import logging 
import os 
import settings 
import boto3 
import config 
from gtts import gTTS
import argparse

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])

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
    return text

def create_audio(path, text):
    #logging.info(f"Generating Audio File : {text}")   
    text = process_speech_text(text)
    if not os.path.exists(path):
        
        if settings.voice_engine=="polly":
            polly_client = boto3.Session(
                            aws_access_key_id=config.aws_access_key_id,                     
                            aws_secret_access_key=config.aws_secret_access_key,
                            region_name='us-west-2').client('polly')

            response = polly_client.synthesize_speech(
                    Engine='neural',
                    OutputFormat='mp3', 
                    Text=text,
                    VoiceId='Matthew'
                )

            file = open(path, 'wb')
            file.write(response['AudioStream'].read())
            file.close()

        if settings.voice_engine=="gtts":
            print("GTTS")
            print(text)
            print(path)
            ttmp3 = gTTS(text)
            ttmp3.save(path)
        
        if settings.voice_engine=="balcon":
            result = subprocess.call([
                        'balcon.exe',
                        '-w',path, 
                        '-t',f"{text}"                
                        ])
    else:
        logging.info(f"Audio file already exists : {path}")

    return path
    logging.info("========== Finished Creating Audio File From Text ==========")   


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--speech',default='Hello world this is a test.', help='Enter text for speech')
    parser.add_argument('--path',default='test_audio.mp3', help='Path to save audio file to')
    args = parser.parse_args()
    print(args.path)
    print(args.speech)
    create_audio(args.path, args.speech)