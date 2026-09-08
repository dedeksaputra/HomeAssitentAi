from core.base_service import BaseService

import time
import numpy as np
import sounddevice as sd
from pathlib import Path

from openwakeword.model import Model

from core.config import ROOT_DIR, load_config


class WakeWordService(BaseService):

    MODEL_FILES = {
        "alexa": "alexa_v0.1.onnx",
        "piupiu": "piupiu.onnx",
    }

    def __init__(self):

        super().__init__("WakeWord")

        self.last_detect_time = 0
        self.cooldown = 2.0

        config = load_config()
        wakeword_name = str(config.get("wakeword_model", "alexa")).strip()
        wakeword_name = Path(wakeword_name).stem
        model_file = self.MODEL_FILES.get(
            wakeword_name,
            f"{wakeword_name}.onnx",
        )
        model_path = ROOT_DIR / "model" / "shared" / model_file

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model wake word tidak ditemukan: {model_path}"
            )

        self.model = Model(
            wakeword_models=[str(model_path)],
            inference_framework="onnx"
        )

        self.sample_rate = 16000
        self.chunk_size = 1280
        self.threshold = float(config.get("wakeword_threshold", 0.85))

        self.detected = False

    def audio_callback(self, indata, frames, time_info, status):

        if status:
            print(status)

        # Sudah terdeteksi, abaikan callback berikutnya
        if self.detected:
            return

        audio = np.frombuffer(indata, dtype=np.int16)

        prediction = self.model.predict(audio)

        for model_name, score in prediction.items():

            if score < self.threshold:
                continue

            now = time.time()

            if now - self.last_detect_time < self.cooldown:
                return

            print(f"{model_name}: {score:.3f}")

            self.last_detect_time = now

            self.on_detected()

            return

    def on_detected(self):

        self.detected = True

    def wait(self):

        self.detected = False

        # Reset state streaming OpenWakeWord
        self.model.reset()

        stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            channels=1,
            dtype="int16",
            callback=self.audio_callback
        )

        stream.start()

        try:

            while not self.detected:
                time.sleep(0.01)

        finally:

            stream.stop()
            stream.close()