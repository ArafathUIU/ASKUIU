from celery import Celery
import whisper
import os

app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@app.task
def process_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    os.remove(audio_path)  # Clean up
    return result["text"]