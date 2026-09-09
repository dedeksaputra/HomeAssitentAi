import json
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from core.config import ROOT_DIR


ALARM_FILE = ROOT_DIR / "model" / "data" / "memory" / "alarms.json"


class AlarmService:
    """Memantau alarm tersimpan dan menjalankan bunyi saat waktunya tiba."""

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self._stop_event = threading.Event()
        self._thread = None
        self._players: dict[int, subprocess.Popen] = {}

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="alarm-service",
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._stop_players()

        if self._thread is not None and self._thread.is_alive():
            self._thread.join(timeout=2)

        self._thread = None

    def _run(self):
        while not self._stop_event.is_set():
            alarms = self._load_alarms()
            current_time = datetime.now().strftime("%H:%M")
            changed = False

            for alarm in alarms:
                alarm_id = alarm.get("id")
                if not isinstance(alarm_id, int):
                    continue

                process = self._players.get(alarm_id)
                if process is not None and process.poll() is not None:
                    self._players.pop(alarm_id, None)

                if alarm.get("ringing") is True and alarm_id not in self._players:
                    self._players[alarm_id] = self._start_player()

                if (
                    alarm.get("enabled") is True
                    and alarm.get("ringing") is not True
                    and alarm.get("time") == current_time
                ):
                    alarm["ringing"] = True
                    changed = True
                    self._players[alarm_id] = self._start_player()
                    print(
                        f"[ALARM] Berbunyi: {alarm.get('label', 'Alarm')} "
                        f"({alarm.get('time')})"
                    )

                if alarm.get("ringing") is not True:
                    self._stop_player(alarm_id)

            if changed:
                self._save_alarms(alarms)

            self._stop_event.wait(self.interval)

        self._stop_players()

    def _start_player(self):
        try:
            return subprocess.Popen(
                [sys.executable, "-m", "core.services.alarm_audio"],
                cwd=ROOT_DIR,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as error:
            print(f"[ALARM] Audio gagal dijalankan: {error}")
            return None

    def _stop_players(self):
        for alarm_id in list(self._players):
            self._stop_player(alarm_id)

    def _stop_player(self, alarm_id: int):
        process = self._players.pop(alarm_id, None)
        if process is None or process.poll() is not None:
            return

        process.terminate()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill()

    @staticmethod
    def _load_alarms() -> list[dict]:
        if not ALARM_FILE.exists():
            return []

        try:
            with ALARM_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

        return data if isinstance(data, list) else []

    @staticmethod
    def _save_alarms(alarms: list[dict]):
        ALARM_FILE.parent.mkdir(parents=True, exist_ok=True)
        temporary_file = ALARM_FILE.with_suffix(".tmp")
        with temporary_file.open("w", encoding="utf-8") as file:
            json.dump(alarms, file, ensure_ascii=False, indent=4)
        temporary_file.replace(ALARM_FILE)
