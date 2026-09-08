#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-linux"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"

log() {
    printf '\n[HomeAssisten] %s\n' "$1"
}

fail() {
    printf '\n[HomeAssisten] ERROR: %s\n' "$1" >&2
    exit 1
}

printf '\nAlamat server Ollama [127.0.0.1:11434]: '
read -r OLLAMA_HOST_INPUT
OLLAMA_HOST_INPUT="${OLLAMA_HOST_INPUT:-127.0.0.1:11434}"

case "${OLLAMA_HOST_INPUT}" in
    http://*|https://*) OLLAMA_HOST="${OLLAMA_HOST_INPUT%/}" ;;
    *) OLLAMA_HOST="http://${OLLAMA_HOST_INPUT%/}" ;;
esac

printf 'Nama model Ollama [qwen3:1.7b]: '
read -r OLLAMA_MODEL
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:1.7b}"

printf 'Model wake word [alexa] (alexa/piupiu): '
read -r WAKEWORD_MODEL
WAKEWORD_MODEL="${WAKEWORD_MODEL:-alexa}"
WAKEWORD_MODEL="${WAKEWORD_MODEL##*/}"
WAKEWORD_MODEL="${WAKEWORD_MODEL%.onnx}"
case "${WAKEWORD_MODEL}" in
    alexa) WAKEWORD_FILE="alexa_v0.1.onnx" ;;
    piupiu) WAKEWORD_FILE="piupiu.onnx" ;;
    *) WAKEWORD_FILE="${WAKEWORD_MODEL}.onnx" ;;
esac

printf 'File system prompt [config/system_prompt.txt]: '
read -r SYSTEM_PROMPT_SOURCE
SYSTEM_PROMPT_SOURCE="${SYSTEM_PROMPT_SOURCE:-config/system_prompt.txt}"

if [[ "${SYSTEM_PROMPT_SOURCE}" = /* ]]; then
    SYSTEM_PROMPT_PATH="${SYSTEM_PROMPT_SOURCE}"
else
    SYSTEM_PROMPT_PATH="${ROOT_DIR}/${SYSTEM_PROMPT_SOURCE}"
fi
test -f "${SYSTEM_PROMPT_PATH}" || fail "File system prompt tidak ditemukan: ${SYSTEM_PROMPT_SOURCE}"
mkdir -p "${ROOT_DIR}/config"

command -v sudo >/dev/null 2>&1 || fail "sudo tidak ditemukan. Pasang dependency sistem sebagai root atau instal sudo."
command -v apt-get >/dev/null 2>&1 || fail "Installer ini membutuhkan distro Debian/Ubuntu dengan apt-get."

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    log "Memasang Python 3.11 dan dependency sistem audio/build"
    sudo apt-get update
    sudo apt-get install -y \
        python3.11 \
        python3.11-dev \
        python3.11-venv \
        build-essential \
        libsndfile1 \
        libsndfile1-dev \
        portaudio19-dev \
        ffmpeg \
        curl
else
    log "Python ${PYTHON_BIN} ditemukan"
    sudo apt-get update
    sudo apt-get install -y \
        python3.11-dev \
        python3.11-venv \
        build-essential \
        libsndfile1 \
        libsndfile1-dev \
        portaudio19-dev \
        ffmpeg \
        curl
fi

command -v "${PYTHON_BIN}" >/dev/null 2>&1 || fail "Python 3.11 belum tersedia setelah instalasi."

log "Membuat virtual environment di ${VENV_DIR}"
"${PYTHON_BIN}" -m venv "${VENV_DIR}"
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

python -m pip install --upgrade pip setuptools wheel
python -m pip install -r "${ROOT_DIR}/requirements-linux.txt"

log "Memasang openWakeWord dari source lokal"
python -m pip install "${ROOT_DIR}/openWakeWord"

if [[ "${SYSTEM_PROMPT_PATH}" != "${ROOT_DIR}/config/system_prompt.txt" ]]; then
    cp "${SYSTEM_PROMPT_PATH}" "${ROOT_DIR}/config/system_prompt.txt"
fi
OLLAMA_HOST="${OLLAMA_HOST}" OLLAMA_MODEL="${OLLAMA_MODEL}" WAKEWORD_MODEL="${WAKEWORD_MODEL}" ROOT_DIR="${ROOT_DIR}" \
    "${PYTHON_BIN}" - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["ROOT_DIR"])
config = {
    "ollama_host": os.environ["OLLAMA_HOST"],
    "ollama_model": os.environ["OLLAMA_MODEL"],
    "wakeword_model": os.environ["WAKEWORD_MODEL"],
    "wakeword_threshold": 0.85,
    "conversation_timeout": 8,
    "enable_thinking_sound": True,
    "system_prompt_file": "config/system_prompt.txt",
}
(root / "config" / "settings.json").write_text(
    json.dumps(config, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
PY

OLLAMA_HOSTNAME="${OLLAMA_HOST#*://}"
OLLAMA_HOSTNAME="${OLLAMA_HOSTNAME%%/*}"
if [[ "${OLLAMA_HOSTNAME}" == "127.0.0.1:*" || "${OLLAMA_HOSTNAME}" == "localhost:*" || "${OLLAMA_HOSTNAME}" == "[::1]:*" ]]; then
    if ! command -v ollama >/dev/null 2>&1; then
        log "Ollama belum ditemukan, memasang Ollama lokal"
        curl -fsSL https://ollama.com/install.sh | sh
    fi

    command -v ollama >/dev/null 2>&1 || fail "Ollama gagal dipasang."

    if ! ollama list | awk 'NR > 1 {print $1}' | grep -Fxq "${OLLAMA_MODEL}"; then
        log "Mengunduh model Ollama ${OLLAMA_MODEL}"
        ollama pull "${OLLAMA_MODEL}"
    else
        log "Model Ollama qwen3:1.7b sudah tersedia"
    fi
else
    log "Menggunakan Ollama remote: ${OLLAMA_HOST}"
fi

curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1 || fail "Server Ollama tidak dapat dihubungi: ${OLLAMA_HOST}"
if ! curl -fsS "${OLLAMA_HOST}/api/tags" | grep -q "${OLLAMA_MODEL}"; then
    fail "Model ${OLLAMA_MODEL} tidak ditemukan pada server Ollama: ${OLLAMA_HOST}"
fi

for required_file in \
    "model/shared/${WAKEWORD_FILE}" \
    "model/tts/kokoro-v1.0.onnx" \
    "model/tts/voices-v1.0.bin" \
    "model/tts/piper/id_ID-news_tts-medium.onnx"; do
    test -f "${ROOT_DIR}/${required_file}" || fail "File model tidak ditemukan: ${required_file}"
done

chmod +x "${ROOT_DIR}/run_linux.sh"

log "Instalasi selesai"
printf 'Jalankan aplikasi dengan: %s\n' "${ROOT_DIR}/run_linux.sh"
