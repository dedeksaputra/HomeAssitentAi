# HomeAssisten

HomeAssisten adalah voice assistant berbahasa Indonesia dengan wake word, speech-to-text, Ollama, tools, dan text-to-speech.

## Kebutuhan

- Linux Debian/Ubuntu x86_64 untuk installer resmi.
- Python 3.11.
- Mikrofon dan speaker yang dapat diakses sistem.
- Server Ollama yang dapat dijangkau melalui jaringan.
- Model Ollama yang dipilih di konfigurasi, default `qwen3:1.7b`.
- File model wake word dan TTS runtime, yang didistribusikan terpisah karena ukurannya besar.

## Model Runtime

Model `.onnx`, `.tflite`, dan `.bin` tidak disimpan di repository GitHub agar repository tidak bergantung pada kuota Git LFS. Setelah clone, letakkan file model pada struktur berikut:

```text
model/shared/piupiu.onnx
model/tts/kokoro-v1.0.onnx
model/tts/voices-v1.0.bin
model/tts/piper/id_ID-news_tts-medium.onnx
```

File model dapat disalin dari paket/model release HomeAssisten yang Anda simpan secara terpisah. Installer akan memeriksa file tersebut dan berhenti dengan pesan file yang belum tersedia.

## Instalasi Linux

```bash
chmod +x install_linux.sh run_linux.sh
./install_linux.sh
```

Installer akan meminta:

1. Alamat server Ollama, misalnya `192.168.1.20:11434`.
2. Nama model Ollama, default `qwen3:1.7b`.
3. File system prompt, default `config/system_prompt.txt`.

Installer membuat virtual environment, memasang dependency, memeriksa model lokal atau remote, dan memvalidasi file model audio.

Jalankan aplikasi dengan:

```bash
./run_linux.sh
```

## Konfigurasi

Pengaturan utama berada di [config/settings.json](config/settings.json):

```json
{
  "ollama_host": "http://127.0.0.1:11434",
  "ollama_model": "qwen3:1.7b",
  "conversation_timeout": 8,
  "enable_thinking_sound": true,
  "system_prompt_file": "config/system_prompt.txt"
}
```

Role system berada di [config/system_prompt.txt](config/system_prompt.txt). File tersebut dibaca runtime dan digabungkan dengan history sebelum pesan dikirim ke Ollama.

`OLLAMA_HOST` dapat digunakan sebagai override sementara:

```bash
OLLAMA_HOST=http://192.168.1.20:11434 ./run_linux.sh
```

## Ollama Remote

Pada PC yang menjalankan Ollama, pastikan Ollama mendengarkan koneksi jaringan, bukan hanya `127.0.0.1`. Konfigurasi service Ollama sesuai sistem operasi Anda agar bind ke alamat yang dapat dijangkau, lalu buka TCP port `11434` di firewall.

Pastikan model tersedia di server Ollama:

```bash
ollama pull qwen3:1.7b
curl http://127.0.0.1:11434/api/tags
```

Dari PC HomeAssisten, ganti `ollama_host` di `config/settings.json` dengan alamat server Ollama. `run_linux.sh` akan memeriksa koneksi dan model sebelum menjalankan aplikasi.

## Struktur Konfigurasi

- `config/settings.json`: host, model, timeout, dan opsi runtime.
- `config/system_prompt.txt`: role system AI.
- `core/config.py`: loader konfigurasi.
- `install_linux.sh`: installer Debian/Ubuntu.
- `run_linux.sh`: pemeriksaan Ollama dan runner aplikasi.

## GitHub

Model besar sengaja tidak di-commit ke repository. Dengan begitu clone source tidak memerlukan Git LFS atau kuota LFS GitHub.

File lokal seperti virtual environment, history, log, dan folder `non_runtime` diabaikan oleh Git.

### Commit Pertama

```bash
git init
git add .
git status
git commit -m "Initial HomeAssisten project"
git branch -M main
git remote add origin https://github.com/USERNAME/REPOSITORY.git
git push -u origin main
```

Ganti URL remote dengan URL repository GitHub Anda sendiri. Jangan commit token, password, atau konfigurasi rahasia.

## Troubleshooting

- Ollama tidak terhubung: periksa `ollama_host`, firewall, port `11434`, dan `curl http://HOST:11434/api/tags`.
- Model tidak ditemukan: jalankan `ollama pull NAMA_MODEL` di server Ollama.
- Tidak ada audio: periksa permission mikrofon, speaker, PortAudio, dan perangkat audio default.
- Crash native audio: uji dengan `enable_thinking_sound: false` untuk menonaktifkan suara indikator thinking.

Dokumentasi Linux tambahan tersedia di [LINUX.md](LINUX.md).
