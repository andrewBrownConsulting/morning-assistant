import argparse
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

PIPER_BINARY = shutil.which("piper")

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    from fastapi import FastAPI
except ImportError:
    FastAPI = None

try:
    import uvicorn
except ImportError:
    uvicorn = None

BBC_NEWS_RSS = "https://feeds.bbci.co.uk/news/uk/rss.xml"

def get_top_headlines(feed_url=BBC_NEWS_RSS, count=5):
    try:
        with urllib.request.urlopen(feed_url) as response:
            xml_data = response.read()
    except Exception as exc:
        print(f"Unable to connect to BBC News: {exc}")
        return []

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as exc:
        print(f"Unable to parse BBC News feed: {exc}")
        return []

    headlines = [item.findtext("title") for item in root.findall("./channel/item")]
    return headlines[:count]


def speak_text(text):
    if not text:
        return

    if pyttsx3 is not None:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return

    if PIPER_BINARY:
        subprocess.run([PIPER_BINARY, "--model", "/usr/share/piper/models/en_US-lessac-medium.onnx", "--output_file", "/tmp/piper_out.wav"], input=text.encode("utf-8"), check=False)
        return

    system = platform.system()

    if system == "Darwin" and shutil.which("say"):
        subprocess.run(["say", text], check=False)
        return

    if system == "Windows" and shutil.which("powershell"):
        safe_text = text.replace("'", "''")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"$voice = New-Object -ComObject SAPI.SpVoice; $voice.Speak('{safe_text}')",
            ],
            check=False,
        )
        return

    if system == "Linux":
        for command in ("espeak", "spd-say"):
            if shutil.which(command):
                subprocess.run([command, text], check=False)
                return

    print(f"No supported TTS engine found for {system}.")


def read_headlines_aloud(headlines):
    if not headlines:
        speak_text("Unable to connect to BBC News. It is unavailable right now.")
        return []

    message = "Here are today's top headlines from BBC News.\n"
    for i, headline in enumerate(headlines, start=1):
        message += f"{i}. {headline}\n"
    speak_text(message)
    return headlines


def run_news_script_once():
    return read_headlines_aloud(get_top_headlines())


def start_background_run():
    try:
        news_text = "Here are today's top headlines from BBC News. "
        headlines = get_top_headlines()
        if not headlines:
            news_text += "Unable to connect to BBC News. It is unavailable right now."
        else:
            for i, headline in enumerate(headlines, start=1):
                news_text += f"{i}. {headline}. "
        subprocess.run(["espeak", news_text], check=False)
        return {"status": "started"}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}

app = FastAPI(title="BBC News Service") if FastAPI is not None else None


if app is not None:
    @app.get("/")
    def root():
        return {"service": "bbc-news", "status": "ok"}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/headlines")
    def headlines_route():
        return {"headlines": get_top_headlines()}

    @app.post("/run")
    def run_route():
        return start_background_run()

    @app.post("/test-audio")
    def test_audio_route():
        try:
            if PIPER_BINARY:
                subprocess.run(
                    [PIPER_BINARY, "--model", "/usr/share/piper/models/en_US-lessac-medium.onnx", "--output_file", "/tmp/piper_test.wav"],
                    input="this is a test".encode("utf-8"),
                    check=False,
                )
            else:
                subprocess.run(["espeak", "this is a test"], check=False)
            return {"status": "ok", "message": "Played test audio"}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}

def parse_args():
    parser = argparse.ArgumentParser(description="BBC News reader")
    parser.add_argument("--play-only", action="store_true", help="Speak the current headlines once")
    parser.add_argument("--headlines-only", action="store_true", help="Print the top headlines as JSON")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
