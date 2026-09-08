import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "settings.json"


def load_config() -> dict[str, Any]:
    if not DEFAULT_CONFIG_PATH.exists():
        return {}

    try:
        with DEFAULT_CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"Konfigurasi tidak dapat dibaca: {DEFAULT_CONFIG_PATH}"
        ) from error

    if not isinstance(config, dict):
        raise RuntimeError("Isi konfigurasi harus berupa object JSON.")

    return config


def get_ollama_host(config: dict[str, Any]) -> str:
    host = str(config.get("ollama_host", "127.0.0.1:11434")).strip()
    if "://" not in host:
        host = f"http://{host}"
    return host.rstrip("/")


def get_system_prompt(config: dict[str, Any]) -> str:
    prompt_file = str(
        config.get("system_prompt_file", "config/system_prompt.txt")
    ).strip()
    prompt_path = ROOT_DIR / prompt_file

    try:
        prompt = prompt_path.read_text(encoding="utf-8").strip()
    except OSError as error:
        raise RuntimeError(
            f"File system prompt tidak dapat dibaca: {prompt_path}"
        ) from error

    if not prompt:
        raise RuntimeError(f"File system prompt kosong: {prompt_path}")

    return prompt
