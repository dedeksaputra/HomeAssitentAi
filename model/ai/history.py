
import json
from pathlib import Path
from typing import Any


# Lokasi file history
HISTORY_FILE = Path(__file__).resolve().parents[1] / "data" / "memory" / "history.json"


def _load_history() -> list[dict[str, Any]]:
    """Membaca seluruh history dari file JSON."""

    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, OSError):
        return []


def _save_history(history: list[dict[str, Any]]) -> None:
    """Menyimpan history ke file JSON."""

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    with HISTORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            history,
            file,
            ensure_ascii=False,
            indent=4,
        )


def get_history() -> list[dict[str, Any]]:
    """Mengambil seluruh history percakapan.

    Returns:
        List seluruh history.
    """
    return _load_history()


def get_history_last(count: int = 1) -> list[dict[str, Any]]:
    """Mengambil history terakhir.

    Args:
        count: Jumlah history terakhir yang ingin diambil.

    Returns:
        List history terakhir.
    """
    history = _load_history()

    if count <= 0:
        return []

    return history[-count:]


MAX_HISTORY_ITEMS = 50
DEFAULT_HISTORY_KEEP = 20


def _trim_history(history: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Jaga 20 riwayat awal dan hapus riwayat lama secara aman.

    Saat jumlah riwayat melebihi 100, proses trim dimulai dari index 20.
    Jika item paling lama berjenis user, maka hapus pasangan user+assistant berikutnya
    agar riwayat tidak terpotong di tengah pasangan.
    """

    if len(history) <= MAX_HISTORY_ITEMS:
        return history

    protected = history[:DEFAULT_HISTORY_KEEP]
    removable = history[DEFAULT_HISTORY_KEEP:]

    while len(protected) + len(removable) > MAX_HISTORY_ITEMS:
        if not removable:
            break

        first_role = removable[0].get("role")

        if first_role == "user" and len(removable) > 1 and removable[1].get("role") == "assistant":
            del removable[:2]
        else:
            del removable[0]

    return protected + removable


def add_history(data: dict[str, Any]) -> None:
    """Menambahkan satu data ke history.

    Args:
        data: Data history yang ingin ditambahkan.
    """

    if not isinstance(data, dict):
        raise TypeError("History harus berupa dictionary.")

    history = _load_history()
    history.append(data)
    history = _trim_history(history)

    _save_history(history)


def clear_history() -> None:
    """Menghapus seluruh history."""

    _save_history([])


def get_history_count() -> int:
    """Mengambil jumlah history."""

    return len(_load_history())

