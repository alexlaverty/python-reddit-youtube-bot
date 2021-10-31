import boto3 
import config
import logging 

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
    text = text.replace(" AITA ", " Am I The Asshole? ")
    text = text.replace(" AMA ", " Ask me anything ")
    text = text.replace(" ELI5 ", " Explain Like I'm Five ")
    text = text.replace(" IAMA ", " I am a ")
    text = text.replace(" IANAD ", " i am not a doctor ")
    text = text.replace(" IANAL ", " i am not a lawyer ")
    text = text.replace(" IMO ", " in my opinion ")
    text = text.replace(" NSFL ", " Not safe for life ")
    text = text.replace(" NSFW ", " Not safe for Work ")
    text = text.replace(" NTA ", " Not The Asshole ")
    text = text.replace(" SMH ", " Shaking my head ")
    text = text.replace(" TD;LR ", " too long didn't read ")
    text = text.replace(" TDLR ", " too long didn't read ")
    text = text.replace(" TIL ", " Today I Learned ")
    text = text.replace(" YTA ", " You're the asshole ")
    text = text.replace(" SAHM ", " stay at home mother ")
    return text

def create_audio(path, text):
    logging.info("========== Creating Audio File From Text ==========")   
    logging.info("Path : " + path)
    
    text = process_speech_text(text)
    logging.info("Speech : " + text)

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
    logging.info("========== Finished Creating Audio File From Text ==========")   


