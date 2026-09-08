#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-linux"

test -x "${VENV_DIR}/bin/python" || {
    printf 'Virtual environment belum ada. Jalankan ./install_linux.sh terlebih dahulu.\n' >&2
    exit 1
}

cd "${ROOT_DIR}"

OLLAMA_HOST="${OLLAMA_HOST:-}"
OLLAMA_MODEL="${OLLAMA_MODEL:-}"
if [[ -z "${OLLAMA_HOST}" || -z "${OLLAMA_MODEL}" ]]; then
    CONFIG_VALUES="$(${VENV_DIR}/bin/python -c 'import json; from pathlib import Path; c=json.loads(Path("config/settings.json").read_text(encoding="utf-8")); print(c.get("ollama_host", "")); print(c.get("ollama_model", "qwen3:1.7b"))')"
    if [[ -z "${OLLAMA_HOST}" ]]; then
        OLLAMA_HOST="$(printf '%s\n' "${CONFIG_VALUES}" | sed -n '1p')"
    fi
    if [[ -z "${OLLAMA_MODEL}" ]]; then
        OLLAMA_MODEL="$(printf '%s\n' "${CONFIG_VALUES}" | sed -n '2p')"
    fi
fi
OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-qwen3:1.7b}"

OLLAMA_HOSTNAME="${OLLAMA_HOST#*://}"
OLLAMA_HOSTNAME="${OLLAMA_HOSTNAME%%/*}"
if [[ "${OLLAMA_HOSTNAME}" == "127.0.0.1:*" || "${OLLAMA_HOSTNAME}" == "localhost:*" || "${OLLAMA_HOSTNAME}" == "[::1]:*" ]]; then
    command -v ollama >/dev/null 2>&1 || {
        printf 'Ollama lokal belum terpasang. Jalankan ./install_linux.sh terlebih dahulu.\n' >&2
        exit 1
    }

    if ! curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1; then
        ollama serve >/tmp/homeassisten-ollama.log 2>&1 &
        OLLAMA_PID=$!
        trap 'kill "${OLLAMA_PID}" 2>/dev/null || true' EXIT

        for _ in $(seq 1 30); do
            curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1 && break
            sleep 1
        done
    fi

    if ! ollama list | awk 'NR > 1 {print $1}' | grep -Fxq "${OLLAMA_MODEL}"; then
        ollama pull "${OLLAMA_MODEL}"
    fi
else
    printf 'Menggunakan Ollama remote: %s\n' "${OLLAMA_HOST}"
fi

curl -fsS "${OLLAMA_HOST}/api/tags" >/dev/null 2>&1 || {
    printf 'Server Ollama tidak dapat dihubungi: %s\n' "${OLLAMA_HOST}" >&2
    exit 1
}

curl -fsS "${OLLAMA_HOST}/api/tags" | grep -q "${OLLAMA_MODEL}" || {
    printf 'Model %s tidak ditemukan pada server Ollama: %s\n' "${OLLAMA_MODEL}" "${OLLAMA_HOST}" >&2
    exit 1
}

exec "${VENV_DIR}/bin/python" main.py
