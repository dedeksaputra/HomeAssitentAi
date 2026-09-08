import json
from datetime import datetime
from pathlib import Path

ALARM_FILE = Path(__file__).resolve().parents[2] / "model" / "data" / "memory" / "alarms.json"


# ============================================================
# SET ALARM
# ============================================================

set_alarm_tool = {
    "type": "function",
    "function": {
        "name": "set_alarm",
        "description": (
            "Membuat alarm pada waktu tertentu. "
            "Gunakan format waktu 24 jam HH:MM. "
            "Contoh: 07:30 untuk alarm pukul tujuh lewat tiga puluh."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": (
                        "Waktu alarm dalam format 24 jam HH:MM. "
                        "Contoh: 07:30 atau 21:45."
                    )
                },
                "label": {
                    "type": "string",
                    "description": (
                        "Keterangan alarm, misalnya "
                        "'Bangun pagi' atau 'Berangkat kerja'."
                    )
                }
            },
            "required": ["time"]
        }
    }
}


# ============================================================
# CANCEL ALARM
# ============================================================

cancel_alarm_tool = {
    "type": "function",
    "function": {
        "name": "cancel_alarm",
        "description": (
            "Mematikan atau menonaktifkan alarm yang sudah dibuat "
            "berdasarkan ID alarm."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "alarm_id": {
                    "type": "integer",
                    "description": "ID alarm yang ingin dimatikan."
                }
            },
            "required": ["alarm_id"]
        }
    }
}


# ============================================================
# STOP RINGING ALARM
# ============================================================

stop_alarm_tool = {
    "type": "function",
    "function": {
        "name": "stop_alarm",
        "description": (
            "Menghentikan alarm yang sedang berbunyi."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


# ============================================================
# HELPER
# ============================================================

def _load_alarms() -> list[dict]:
    """Membaca semua alarm dari file JSON."""

    if not ALARM_FILE.exists():
        return []

    try:
        with ALARM_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, OSError):
        return []


def _save_alarms(alarms: list[dict]) -> None:
    """Menyimpan semua alarm ke file JSON."""

    with ALARM_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            alarms,
            file,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# CREATE ALARM
# ============================================================

def set_alarm(
    time: str,
    label: str = "Alarm"
) -> dict:
    """Membuat alarm baru.

    Args:
        time: Waktu alarm dalam format HH:MM.
        label: Keterangan alarm.

    Returns:
        Informasi alarm.
    """

    # Validasi waktu
    try:
        alarm_time = datetime.strptime(
            time,
            "%H:%M"
        ).strftime("%H:%M")

    except ValueError:
        return {
            "success": False,
            "message": (
                "Format waktu tidak valid. "
                "Gunakan format HH:MM."
            )
        }

    alarms = _load_alarms()

    # Generate ID
    alarm_id = 1

    if alarms:
        alarm_id = max(
            alarm.get("id", 0)
            for alarm in alarms
        ) + 1

    alarm = {
        "id": alarm_id,
        "time": alarm_time,
        "label": label,
        "enabled": True,
        "ringing": False,
        "created_at": datetime.now().isoformat()
    }

    alarms.append(alarm)

    _save_alarms(alarms)

    print(
        f"[ALARM] Dibuat: "
        f"{alarm_time} - {label}"
    )

    return {
        "success": True,
        "message": (
            f"Alarm berhasil dibuat untuk "
            f"pukul {alarm_time}."
        ),
        "alarm": alarm
    }


# ============================================================
# CANCEL ALARM
# ============================================================

def cancel_alarm(alarm_id: int) -> dict:
    """Menonaktifkan alarm berdasarkan ID.

    Args:
        alarm_id: ID alarm yang ingin dinonaktifkan.

    Returns:
        Status hasil operasi.
    """

    alarms = _load_alarms()

    for alarm in alarms:

        if alarm.get("id") == alarm_id:

            alarm["enabled"] = False
            alarm["ringing"] = False

            _save_alarms(alarms)

            print(
                f"[ALARM] Dinonaktifkan: "
                f"{alarm_id}"
            )

            return {
                "success": True,
                "message": (
                    f"Alarm {alarm_id} berhasil "
                    "dinonaktifkan."
                ),
                "alarm": alarm
            }

    return {
        "success": False,
        "message": (
            f"Alarm dengan ID {alarm_id} "
            "tidak ditemukan."
        )
    }


# ============================================================
# STOP RINGING ALARM
# ============================================================

def stop_alarm() -> dict:
    """Menghentikan semua alarm yang sedang berbunyi.

    Returns:
        Status hasil operasi.
    """

    alarms = _load_alarms()

    stopped = []

    for alarm in alarms:

        if alarm.get("ringing") is True:

            alarm["ringing"] = False
            alarm["enabled"] = False

            stopped.append(alarm["id"])

    if not stopped:

        return {
            "success": False,
            "message": "Tidak ada alarm yang sedang berbunyi."
        }

    _save_alarms(alarms)

    print(
        f"[ALARM] Alarm dihentikan: "
        f"{stopped}"
    )

    return {
        "success": True,
        "message": "Alarm berhasil dihentikan.",
        "alarm_ids": stopped
    }
