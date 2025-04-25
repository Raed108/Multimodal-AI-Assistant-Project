import torch
from TTS.api import TTS
# from playsound import playsound
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import XttsAudioConfig  # Import XttsAudioConfig
# from TTS.config.shared_configs import BaseDatasetConfig  # Import BaseDatasetConfig
# from TTS.tts.models.xtts import XttsArgs  # Import XttsArgs
from io import BytesIO
# from gtts import gTTS
# import os
# import pyttsx3
# import tempfile
# import os
# from pydub import AudioSegment


# Using gTTS (Online)

# # Manually entered text
# text = "Hello, this is a test of text-to-speech functionality."

# # Convert text to speech
# tts = gTTS(text=text, lang='en', slow=False)  # 'en' for English, slow=False for normal speed

# # Save the audio to a file
# audio_file = "output.mp3"
# tts.save(audio_file)

# # Play the audio file (Windows example)
# os.system("start " + audio_file)  # Use "open" for macOS, or "xdg-open" for Linux

#############################

# Using pyttsx3 (Offline)

# Initialize the TTS engine
# engine = pyttsx3.init()

# # Manually entered text
# text = "Hello, this is a test of text-to-speech functionality."

# # Optional: Adjust voice properties
# engine.setProperty('rate', 150)  # Speed (words per minute)
# engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

# # Speak the text
# engine.say(text)
# engine.runAndWait()  # Wait until speaking is done



###############################

# TTS (Text-to-Speech) using TTS library
# This example uses the TTS library to convert text to speech and save it as a WAV file.


# Add the necessary global classes to the safe globals
# torch.serialization.add_safe_globals([XttsConfig, XttsAudioConfig, BaseDatasetConfig, XttsArgs])

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# List available 🐸TTS models
# print(TTS().list_models())

# Initialize TTS
# tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
tts = TTS("tts_models/en/ljspeech/vits").to(device)

# # TTS to a file, use a preset speaker
# file_path = r"C:\Users\raedj\Desktop\ai-assistant-project\output.wav"

# # Create a temporary WAV file
# with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
#     temp_path = tmp_file.name

# tts.tts_to_file(
#   text="مرحبا كيف حالك؟",
#   speaker="Craig Gutsy",
# # speaker_wav=r"C:\Users\raedj\Desktop\ai-assistant-project\backend\Recording.mp3",
#   language="ar",
# #   file_path=file_path
#   file_path=temp_path,  # Save to the temporary file
# )

# # Play the generated audio
# playsound(temp_path)

# # Delete the temporary file after playback
# os.remove(temp_path)
# speaker_wav_data = None
# def load_speaker_wav():
#     global speaker_wav_data
#     with open(r"C:\Users\raedj\Desktop\ai-assistant-project\output.mp3", "rb") as f:
#         speaker_wav_data = f.read()

def text_to_speech(text: str, maleSpeaker: bool) -> bytes:
    """
    Convert text to speech and save it as a WAV file.
    """
    if maleSpeaker:
        # Lower pitch slightly to simulate a male voice (VITS doesn't have "Craig Gutsy")
        wav = tts.tts(
            text=text,
            split_sentences=True,
            # Pitch adjustment (not directly supported in high-level API, see below)
        )
    else:
        # Default LJSpeech voice (female)
        wav = tts.tts(
            text=text,
            split_sentences=True,
        )

    # Convert WAV data to bytes in memory
    with BytesIO() as audio_buffer:
        tts.synthesizer.save_wav(wav, audio_buffer)
        audio_bytes = audio_buffer.getvalue()

    return audio_bytes

    # wav = tts.tts(
    #     text=text,
    #     split_sentences=True
    # )

    # # Convert WAV data to AudioSegment for pitch manipulation
    # with BytesIO() as temp_buffer:
    #     tts.synthesizer.save_wav(wav, temp_buffer)
    #     temp_buffer.seek(0)
    #     audio = AudioSegment.from_wav(temp_buffer)

    # if maleSpeaker:
    #     # Lower pitch to simulate male voice (e.g., -4 semitones approximation)
    #     audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 0.8)})
    # # else: No change needed for female voice (default LJSpeech)

    # # Export to bytes
    # with BytesIO() as audio_buffer:
    #     audio.export(audio_buffer, format="wav")
    #     audio_bytes = audio_buffer.getvalue()

    # return audio_bytes





    # Create a temporary WAV file
    # with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
    #     temp_path = tmp_file.name

    # if maleSpeaker:
    #     tts.tts_to_file(
    #         text=text,
    #         speaker="Craig Gutsy", 
    #         language="en",
    #         file_path=temp_path,
    #         )
    # else:
    #     tts.tts_to_file(
    #         text=text,
    #         speaker_wav=r"C:\Users\raedj\Desktop\ai-assistant-project\output.mp3",  
    #         language="en",
    #         file_path=temp_path,
    #     )

    # # Read the audio bytes
    # with open(temp_path, "rb") as f:
    #     audio_bytes = f.read()

    # # Clean up
    # os.remove(temp_path)
    # return audio_bytes