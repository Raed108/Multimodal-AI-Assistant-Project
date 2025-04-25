FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libfuse2 \
    && rm -rf /var/lib/apt/lists/*

# Install huggingface_hub with hf_xet
RUN pip install huggingface_hub==0.23.0 hf_xet

# Install other dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy pre-downloaded Hugging Face cache (optional)
COPY ./huggingface_cache /root/.cache/huggingface

COPY main.py .
COPY image_service.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]