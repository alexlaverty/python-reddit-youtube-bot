import boto3 
import config

def create_audio(path, text):
    print("========== Creating Audio File From Text ==========")   
    print("Path : " + path)
    print("Speech : " + path)
    print(text)
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
    print("========== Finished Creating Audio File From Text ==========")   