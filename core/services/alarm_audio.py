from pathlib import Path

import sounddevice as sd
import soundfile as sf


SOUND_PATH = Path(__file__).resolve().parents[2] / "assets" / "sounds" / "ting.mp3"


def main():
    if not SOUND_PATH.exists():
        return

    try:
        data, sample_rate = sf.read(str(SOUND_PATH), dtype="float32")
        while True:
            sd.play(data, sample_rate)
            sd.wait()
    except Exception:
        return


if __name__ == "__main__":
    main()
