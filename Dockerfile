FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends espeak alsa-utils curl wget ca-certificates && \
    mkdir -p /tmp/piper && \
    wget -O /tmp/piper/piper_linux_x86_64.tar.gz https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux-x86_64.tar.gz && \
    tar -xzf /tmp/piper/piper_linux_x86_64.tar.gz -C /tmp/piper && \
    cp /tmp/piper/piper /usr/local/bin/piper && \
    mkdir -p /usr/share/piper/models && \
    wget -O /usr/share/piper/models/en_US-lessac-medium.onnx https://huggingface.co/rhasspy/piper-voices/resolve/v1.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx && \
    wget -O /usr/share/piper/models/en_US-lessac-medium.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/v1.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json && \
    rm -rf /tmp/piper && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bbc_news.py .

EXPOSE 8000

CMD ["python", "bbc_news.py"]
