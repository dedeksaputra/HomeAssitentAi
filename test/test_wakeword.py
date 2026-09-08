import numpy as np
import sounddevice as sd
from openwakeword.model import Model

# Lokasi model ONNX
MODEL_PATH = r"D:\project ai\HomeAssisten\model\shared\piou__piou.onnx"

# Konfigurasi audio
SAMPLE_RATE = 16000
CHUNK_SIZE = 1280  # 80 ms

print("Loading OpenWakeWord...")

model = Model(
    wakeword_models=[MODEL_PATH],
    inference_framework="onnx"
)

print("Model loaded.")
print("Listening... Say 'Alexa'")

def audio_callback(indata, frames, time, status):

    if status:
        print(status)

    audio = np.frombuffer(indata, dtype=np.int16)

    prediction = model.predict(audio)

    for name, score in prediction.items():

        print(f"{name}: {score:.3f}", end="\r")

        if score > 0.5:
            print(f"\nWake Detected! ({name}) Score={score:.3f}")

with sd.RawInputStream(
    samplerate=SAMPLE_RATE,
    blocksize=CHUNK_SIZE,
    channels=1,
    dtype="int16",
    callback=audio_callback
):
    while True:
        pass