import re
import os

from utils.aws_services import AWSTranscribe

import moviepy.editor as mp
import speech_recognition as sr
from langchain.llms import OpenAI

class SpeechToText:

    def __init__(self, model, bucket='newsp4-transcribe-docs-bucket'):
        self.model = model
        self.bucket = bucket

    # Function to extract audio from video file
    def extract_audio(self, video_file):
        video = mp.VideoFileClip(video_file)
        audio = video.audio
        audio_file = "extracted_audio.wav"
        audio.write_audiofile(audio_file)
        return audio_file

    # Function to perform speech to text conversion
    def speech_to_text(self, audio_file):
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return text

    # Function to clean text
    def clean_text(self, text):
        # Remove stammering words (words repeated more than twice)
        cleaned_text = re.sub(r'\b(\w+)( \1\b)+', r'\1', text, flags=re.IGNORECASE)
        # Remove punctuation and special characters
        cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_text)
        return cleaned_text


    def openai_api(self, text):
        prompt = "Be precise and rewrite the context and topic in thie video in simple words"
        content = prompt + " " + text

        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

        client = OpenAI(
            api_key=OPENAI_API_KEY,
        )
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            model=self.model,
            )
        clean_text =  response.choices[0].message.content
        # print(message_content)
        return clean_text
    
    def transcribe(self, file_path):
        '''
        Takes a file path in ingress and returns a text in output
        '''

        # if self.model == 'whisper-base':
        #     model = whisper.load_model("base")
        #     text = model.transcribe(file_path)
        #     return text['text']
        
        if self.model == 'transcribe':
            transcribe = AWSTranscribe(self.bucket, 'us-east-1')
            job_name=transcribe.generate_job_name()
            text = transcribe.amazon_transcribe(self.bucket, job_name, file_path, 'it-IT')
            return text
            
        elif self.model.startswith("gpt"):
            # Step 1: Extract audio from video
            audio_file = self.extract_audio(file_path)
            # Step 2: Convert speech to text
            text = self.speech_to_text(audio_file)
            # Step 3: Clean the text
            cleaned_text = self.clean_text(text)
            # Step 4: Input text to OpenAI API
            improvised_text =self.openai_api(cleaned_text)
            return improvised_text
        
        else:
            pass
            #TODO implement new models!!