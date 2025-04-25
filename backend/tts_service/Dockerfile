FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# Set non-interactive frontend for apt-get to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Preconfigure timezone (e.g., UTC) to avoid tzdata prompt
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone

# Ensure TTS uses the correct cache directory
ENV TORCH_HOME=/root/.cache
ENV XDG_DATA_HOME=/root/.cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    espeak-ng \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Upgrade pip BEFORE install
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY main.py .
COPY TTS_service.py .

# Copy pre-downloaded TTS model to the correct cache location
RUN mkdir -p /root/.cache/tts
COPY tts-models/tts_models--en--ljspeech--vits /root/.cache/tts/tts_models--en--ljspeech--vits

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]