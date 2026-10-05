FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=10000

# Install system dependencies including ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install CPU PyTorch build
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download Whisper Small model during image build so startup is instant
RUN python -c "import whisper; whisper.load_model('small')"

# Copy application files
COPY . .

# Expose standard web ports
EXPOSE 10000 7860 8765

# Run FastAPI app
CMD ["python", "app/main.py"]
