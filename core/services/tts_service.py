from core.base_service import BaseService

import sounddevice as sd
import soundfile as sf
from kokoro_onnx import Kokoro

from pathlib import Path
from piper.voice import PiperVoice
import numpy as np
import subprocess
import sys

class TTSService(BaseService):

    def __init__(self):

        super().__init__("TTS")

        self.kokoro = Kokoro(
            "model/tts/kokoro-v1.0.onnx",
            "model/tts/voices-v1.0.bin"
        )

        self.voice = "af_sarah"
        self.speed = 0.8
        self.lang = "en-us"
        
        
        # piper
        root_dir = Path(__file__).resolve().parents[2]
        model_path = (
            root_dir
            / "model"
            / "tts"
            / "piper"
            / "id_ID-news_tts-medium.onnx"
        )
        
        self.voice = PiperVoice.load(model_path)

        self._thinking_process = None

    def thinking(self, enabled: bool):
        if enabled:
            if (
                self._thinking_process is not None
                and self._thinking_process.poll() is None
            ):
                return

            self._thinking_process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "core.services.thinking_audio",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return

        if self._thinking_process is None:
            return

        if self._thinking_process.poll() is None:
            self._thinking_process.terminate()
            try:
                self._thinking_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._thinking_process.kill()

        self._thinking_process = None

    def speak(self, text):


        samples, sample_rate = self.kokoro.create(
            text=text,
            voice=self.voice,
            speed=self.speed,
            lang=self.lang
        )

        sd.play(samples, sample_rate)
        sd.wait()
        
        
    def speak_piper(self, text : str):
        
        if not text:
            return

        audio_chunks = []
        sample_rate = None

        for chunk in self.voice.synthesize(text):

            if sample_rate is None:
                sample_rate = chunk.sample_rate

            audio_chunks.append(chunk.audio_float_array)

        if len(audio_chunks) == 0:
            return

        audio = np.concatenate(audio_chunks)

        sd.play(audio, sample_rate)
        sd.wait()
        
    def beep(self):

        data, sr = sf.read("assets/sounds/ting.mp3", dtype='float32')

        sd.play(data, sr)

        sd.wait()