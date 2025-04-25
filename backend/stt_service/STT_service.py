import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
# from datasets import load_dataset
import librosa
# import sounddevice as sd
import io
from pydub import AudioSegment




device = "cuda:0" if torch.cuda.is_available() else "cpu"
# print(f"Using device: {device}")
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3-turbo"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

# dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
# sample = dataset[0]["audio"]


# Play the audio
# audio_data = sample["array"]
# sampling_rate = sample["sampling_rate"]
# print("Playing audio...")
# sd.play(audio_data, sampling_rate)
# sd.wait()  # Wait until the audio is finished playing

# result = pipe(sample,return_timestamps=True)

# # Load audio with librosa
# audio_path = r"C:\Users\raedj\Desktop\ai-assistant-project\backend\Recording.m4a"
# audio_array, sampling_rate = librosa.load(audio_path, sr=16000)  # Whisper uses 16kHz

# print("Playing audio...")
# sd.play(audio_array, sampling_rate)
# sd.wait()  # Wait until the audio is finished playing

# # Process audio
# result = pipe(
#     {"array": audio_array, "sampling_rate": sampling_rate},
#     generate_kwargs={
#         "task": "transcribe",  # transcribe or translate , Use "transcribe" if you want transcription instead of translation
#         "language": "en",      # optional
#         "return_timestamps": True
#     }
# )

# print(result["text"])

def speech_to_text(audio_bytes: bytes) -> str:
    """
    Convert speech to text using Whisper.
    """

    # Convert bytes to file-like object
    audio_stream = io.BytesIO(audio_bytes)

    # Use pydub to read audio in any format (requires ffmpeg)
    audio = AudioSegment.from_file(audio_stream, format="webm")

    # Export to WAV format in-memory
    wav_io = io.BytesIO()
    audio.set_frame_rate(16000).export(wav_io, format="wav")
    wav_io.seek(0)

    # Load the WAV bytes with librosa
    audio_array, sampling_rate = librosa.load(wav_io, sr=16000)

    # Process audio
    result = pipe(
        {"array": audio_array, "sampling_rate": sampling_rate},
        generate_kwargs={
            "task": "transcribe",  # transcribe or translate , Use "transcribe" if you want transcription instead of translation
            "language": "en",      # optional
            "return_timestamps": True
        }
    )
    return result["text"]
