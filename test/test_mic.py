import pyaudio
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024
SECONDS = 5

audio = pyaudio.PyAudio()

stream = audio.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    input_device_index=1
)

print("Recording...")

frames = []

for _ in range(int(RATE / CHUNK * SECONDS)):
    frames.append(stream.read(CHUNK, exception_on_overflow=False))

print("Done.")

stream.stop_stream()
stream.close()
audio.terminate()

wf = wave.open("test.wav", "wb")
wf.setnchannels(CHANNELS)
wf.setsampwidth(audio.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b"".join(frames))
wf.close()

print("Saved: test.wav")