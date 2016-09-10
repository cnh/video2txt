import subprocess
import os


    
# [START import_libraries]
import argparse
import base64
import json
import time

from googleapiclient import discovery
import httplib2
from oauth2client.client import GoogleCredentials
# [END import_libraries]


# [START authenticating]

#export GOOGLE_APPLICATION_CREDENTIALS=/home/acgt/ashish_work/anupam_speech/audio2txt-6ed49786eab0.json

# Application default credentials provided by env variable
# GOOGLE_APPLICATION_CREDENTIALS
def get_speech_service():
    credentials = GoogleCredentials.get_application_default().create_scoped(
        ['https://www.googleapis.com/auth/cloud-platform'])
    http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build('speech', 'v1beta1', http=http)
# [END authenticating]

'''
for testing,
video_file_path = '/home/acgt/ashish_work/anupam_speech/Seafret - Oceans.mp4'
'''
def extract_audio(video_file_path):
    ffmpeg_cmd = 'ffmpeg -i '+ video_file_path + ' -vn -acodec copy output-audio.aac'
    subprocess.call(ffmpeg_cmd, shell=True)
    
    dirname, filename = os.path.split(os.path.abspath(__file__))
    audio_path = os.path.join(dirname, 'output-audio.aac')
    main(audio_path)

def main(speech_file):
    """Transcribe the given audio file asynchronously.
    Args:
        speech_file: the name of the audio file.
    """
    # [START construct_request]
    with open(speech_file, 'rb') as speech:
        # Base64 encode the binary audio file for inclusion in the request.
        speech_content = base64.b64encode(speech.read())

    service = get_speech_service()
    service_request = service.speech().asyncrecognize(
        body={
            'config': {
                # There are a bunch of config options you can specify. See
                # https://goo.gl/EPjAup for the full list.
            # https://cloud.google.com/speech/reference/rest/v1beta1/RecognitionConfig 
                'encoding': 'LINEAR16',  # raw 16-bit signed LE samples
                'sampleRate': 16000,  # 16 khz
                # See https://goo.gl/DPeVFW for a list of supported languages.
                'languageCode': 'en-US',  # a BCP-47 language tag
            },
            'audio': {
                'content': speech_content.decode('UTF-8')
                }
            })
    # [END construct_request]
    # [START send_request]
    response = service_request.execute()
    print(json.dumps(response))
    # [END send_request]

    name = response['name']
    # Construct a GetOperation request.
    service_request = service.operations().get(name=name)

    while True:
        # Give the server a few seconds to process.
        print('Waiting for server processing...')
        time.sleep(1)
        # Get the long running operation with response.
        response = service_request.execute()

        if 'done' in response and response['done']:
            break

    print(json.dumps(response['response']['results']))


# [START run_application]
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'video_file', help='Full path of video file to be recognized')
    args = parser.parse_args()
    extract_audio(args.video_file)
    #main(args.speech_file)

    #main(output_audio.aac)
    # [END run_application]

