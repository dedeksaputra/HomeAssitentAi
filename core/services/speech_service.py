
from core.base_service import BaseService

import queue
import time
import numpy as np
import sounddevice as sd
import torch

from silero_vad import load_silero_vad, VADIterator
from faster_whisper import WhisperModel


class SpeechService(BaseService):

    def __init__(self):

        super().__init__("Speech")

        self.sample_rate = 16000
        self.block_size = 512

        # =========================
        # Silero VAD
        # =========================

        self.model = load_silero_vad()

        self.vad = VADIterator(
            self.model,
            threshold=0.5,
            sampling_rate=self.sample_rate,
            min_silence_duration_ms=500,
            speech_pad_ms=100
        )

        # =========================
        # Whisper
        # =========================

        self.whisper = WhisperModel(
            model_size_or_path="small",
            device="cpu",
            compute_type="int8"
        )

        # =========================
        # Audio Queue
        # =========================

        self.queue = queue.Queue()

    # =========================================================
    # AUDIO CALLBACK
    # =========================================================

    def audio_callback(self, indata, frames, time_info, status):

        if status:
            print(status)

        audio = np.frombuffer(
            indata,
            dtype=np.float32
        )

        self.queue.put(audio.copy())

    # =========================================================
    # LISTEN
    # =========================================================

    def listen(self, timeout=None):

        print("Listening...")

        # Bersihkan audio lama
        self.clear_queue()

        # Reset VAD
        self.vad.reset_states()

        audio_buffer = []

        recording = False

        # Waktu mulai menunggu suara
        start_time = time.monotonic()

        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.block_size,
            channels=1,
            dtype="float32",
            callback=self.audio_callback
        ):

            while True:

                # =================================================
                # TIMEOUT
                # =================================================

                if timeout is not None:

                    elapsed = time.monotonic() - start_time

                    if elapsed >= timeout and not recording:

                        print(
                            f"No speech detected within "
                            f"{timeout} seconds"
                        )

                        return None

                # =================================================
                # AMBIL AUDIO
                # =================================================

                try:

                    # Timeout kecil supaya loop tetap bisa
                    # mengecek batas timeout di atas.
                    chunk = self.queue.get(
                        timeout=0.1
                    )

                except queue.Empty:

                    continue

                # =================================================
                # VAD
                # =================================================

                chunk_tensor = torch.from_numpy(chunk)

                event = self.vad(chunk_tensor)

                # =================================================
                # EVENT VAD
                # =================================================

                if event:

                    # -----------------------------
                    # USER MULAI BICARA
                    # -----------------------------

                    if "start" in event:

                        print("Voice Start")

                        recording = True

                    # -----------------------------
                    # USER SELESAI BICARA
                    # -----------------------------

                    elif "end" in event:

                        print("Voice End")

                        audio_buffer.append(
                            chunk.copy()
                        )

                        break

                # =================================================
                # SIMPAN AUDIO SAAT RECORDING
                # =================================================

                if recording:

                    audio_buffer.append(
                        chunk.copy()
                    )

        # =========================================================
        # TIDAK ADA AUDIO
        # =========================================================

        if len(audio_buffer) == 0:

            return None

        # =========================================================
        # GABUNG AUDIO
        # =========================================================

        audio = np.concatenate(
            audio_buffer
        )

        print(
            f"Recorded "
            f"{len(audio) / self.sample_rate:.2f} sec"
        )

        # =========================================================
        # WHISPER
        # =========================================================

        print("Whisper Processing...")

        text = self.transcribe(audio)

        return text

    # =========================================================
    # CLEAR QUEUE
    # =========================================================

    def clear_queue(self):

        while not self.queue.empty():

            try:
                self.queue.get_nowait()

            except queue.Empty:

                break

    # =========================================================
    # TRANSCRIBE
    # =========================================================

    def transcribe(self, audio):

        segments, info = self.whisper.transcribe(
            audio,
            language="id",
            beam_size=5,
            vad_filter=False
        )

        text = ""

        for segment in segments:

            text += segment.text

        return text.strip()

