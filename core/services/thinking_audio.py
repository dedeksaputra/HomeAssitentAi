from pathlib import Path

import sounddevice as sd
import soundfile as sf


def main():
    root_dir = Path(__file__).resolve().parents[2]
    sound_path = root_dir / "assets" / "sounds" / "thingking.mp3"

    if not sound_path.exists():
        return

    try:
        data, sample_rate = sf.read(str(sound_path), dtype="float32")
    except Exception:
        return

    try:
        while True:
            sd.play(data, sample_rate)
            sd.wait()
    except Exception:
        return


if __name__ == "__main__":
    main()