# Menjalankan HomeAssisten di Linux

Installer disiapkan untuk Debian/Ubuntu x86_64 dengan Python 3.11.

## Instalasi

```bash
chmod +x install_linux.sh run_linux.sh
./install_linux.sh
```

Installer akan:

- meminta alamat server Ollama, nama model, mode thinking Ollama, model wake word, dan file system prompt;
- menyimpan pengaturan di `config/settings.json`;
- menyimpan role system aktif di `config/system_prompt.txt`;
- memasang Python 3.11, compiler, PortAudio, libsndfile, FFmpeg, dan curl;
- membuat `.venv-linux`;
- memasang dependency Python yang dipakai runtime;
- memasang `openWakeWord` dari folder lokal;
- memasang Ollama dan mengunduh model pilihan jika alamatnya lokal;
- memeriksa koneksi ke server Ollama remote jika alamatnya bukan lokal;
- memeriksa file model wakeword dan TTS.

Model `.onnx`, `.tflite`, dan `.bin` tidak disimpan di repository GitHub karena ukurannya besar. Salin model ke folder `model/` sesuai struktur proyek sebelum menjalankan installer.

## Menjalankan

```bash
./run_linux.sh
```

Script membaca host dan model dari `config/settings.json`. Ollama lokal akan dijalankan bila alamatnya lokal dan servicenya belum aktif; untuk alamat remote, script langsung memeriksa server tersebut lalu menjalankan `main.py`.

Pengaturan dapat diubah tanpa instalasi ulang:

- `config/settings.json`: alamat Ollama, model, mode thinking Ollama, wake word, threshold, timeout, dan opsi suara thinking;
- `config/system_prompt.txt`: role system yang digabungkan dengan history sebelum dikirim ke Ollama.

## Input Aplikasi

Aplikasi mendukung dua cara input:

- Ketik langsung pada `Prompt (Enter untuk voice):` untuk mengirim teks tanpa wake word.
- Tekan `Enter` pada prompt, lalu ucapkan wake word dan perintah suara.
- Saat menunggu wake word, tekan `q` untuk kembali ke mode input teks.

Model wake word default adalah `alexa` dan menggunakan file `model/shared/alexa_v0.1.onnx`. Model custom `piupiu` dapat dipilih di `config/settings.json` dengan memastikan `model/shared/piupiu.onnx` tersedia.

OpenWakeWord menggunakan threshold `0.85` secara default. Naikkan nilainya jika terlalu sering aktif sendiri; turunkan jika wake word sulit terdeteksi.

## Catatan

- Python 3.11 dipilih agar kompatibel dengan wheel audio/ML yang digunakan proyek.
- Installer tidak mengunduh model wakeword/TTS karena file tersebut sudah menjadi bagian dari folder `model/` proyek.
- Model runtime besar tidak disimpan di GitHub; distribusikan melalui paket atau release terpisah.
- Untuk GPU NVIDIA, dependency Torch perlu disesuaikan dengan CUDA host; konfigurasi default memakai CPU agar dapat berjalan di Linux tanpa GPU khusus.
