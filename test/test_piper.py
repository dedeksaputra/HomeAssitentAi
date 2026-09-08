from pathlib import Path
from piper.voice import PiperVoice

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "model" / "tts" / "piper" / "id_ID-news_tts-medium.onnx"

voice = PiperVoice.load(MODEL_PATH)

chunk = next(voice.synthesize("Halo"))

print(type(chunk))
print(dir(chunk))