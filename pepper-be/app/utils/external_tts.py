import os
# Get credentials path from environment variable for security
# Do not hardcode credentials path
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

from google.cloud import texttospeech
import uuid
import os

def text_to_speech(text: str, language_code: str, voice_name: str) -> bytes:
    try:
        client = texttospeech.TextToSpeechClient()

        input_text = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16  # Format WAV
        )

        response = client.synthesize_speech(
            input=input_text, voice=voice, audio_config=audio_config
        )

        return response.audio_content  # langsung bytes WAV

    except Exception as e:
        print(f"[TTS ERROR]: {e}")
        return None
