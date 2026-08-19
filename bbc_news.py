import platform
import shutil
import subprocess
import urllib.request
import xml.etree.ElementTree as ET

try:
    import pyttsx3
except ImportError:  # pragma: no cover - optional dependency
    pyttsx3 = None

BBC_NEWS_RSS = "http://feeds.bbci.co.uk/news/rss.xml"


def get_top_headlines(feed_url=BBC_NEWS_RSS, count=5):
    with urllib.request.urlopen(feed_url) as response:
        xml_data = response.read()
    root = ET.fromstring(xml_data)
    titles = [item.findtext("title") for item in root.findall("./channel/item")]
    return titles[:count]


def speak_text(text):
    if not text:
        return

    if pyttsx3 is not None:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        return

    system = platform.system()

    if system == "Darwin" and shutil.which("say"):
        subprocess.run(["say", text], check=False)
        return

    if system == "Windows":
        if shutil.which("powershell"):
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

    print(f"No supported TTS engine found for {system}. Install pyttsx3 or espeak/spd-say.")


def read_headlines_aloud(headlines):
    message = "Here are today's top headlines from BBC News.\n"
    for i, headline in enumerate(headlines, start=1):
        message += f"{i}. {headline}\n"
    speak_text(message)


if __name__ == "__main__":
    headlines = get_top_headlines()
    read_headlines_aloud(headlines)
