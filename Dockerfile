FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends espeak alsa-utils curl wget ca-certificates

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY voices/ voices/
COPY bbc_news.py .

EXPOSE 8000

CMD ["python", "bbc_news.py"]
