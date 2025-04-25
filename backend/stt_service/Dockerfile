# Use PyTorch image with CUDA support
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

# Set non-interactive frontend for apt-get to avoid prompts
ENV DEBIAN_FRONTEND=noninteractive

# Preconfigure timezone (e.g., UTC) to avoid tzdata prompt
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime && \
    echo "UTC" > /etc/timezone

COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Ensure all Python dependencies install correctly
RUN pip install --no-cache-dir -r requirements.txt

# Install huggingface_hub (without hf_xet for reliability)
RUN pip install huggingface_hub==0.26.0

# Copy pre-downloaded Hugging Face cache (optional)
COPY ./huggingface_cache /root/.cache/huggingface

COPY main.py .
COPY STT_service.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]