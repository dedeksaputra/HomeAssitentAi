# Panduan Tools

Tool HomeAssisten disimpan di folder:

```text
tools/list/
```

Saat runtime dimulai, `tools/list/loader.py` membaca semua file Python di folder tersebut secara otomatis. File `loader.py` dan `___init__.py` tidak dipindai sebagai tool.

## Aturan Penamaan

Setiap tool terdiri dari dua bagian:

1. Schema Ollama dalam dictionary dengan nama berakhiran `_tool`.
2. Function Python dengan nama yang sama seperti `function.name` di schema, tetapi tanpa suffix `_tool`.

Contoh yang benar:

```python
get_weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Mengambil cuaca suatu kota.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nama kota."
                }
            },
            "required": ["city"]
        }
    }
}


def get_weather(city: str) -> str:
    return f"Cuaca untuk {city} belum tersedia."
```

Hubungan namanya adalah:

```text
get_weather_tool  -> nama schema yang dicari loader
get_weather       -> function yang dipanggil runtime
function.name     -> get_weather
```

## Struktur File

Buat satu file Python baru di `tools/list/`, misalnya:

```text
tools/list/get_weather.py
```

Contoh lengkap:

```python
get_weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Mengambil informasi cuaca berdasarkan kota.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Nama kota yang ingin diperiksa."
                }
            },
            "required": ["city"]
        }
    }
}


def get_weather(city: str) -> str:
    """Mengambil cuaca berdasarkan kota."""
    return f"Cuaca di {city} belum tersedia."
```

## Syarat Agar Tool Terdeteksi

- File berada langsung di `tools/list/`, bukan subfolder.
- File memiliki ekstensi `.py`.
- Nama dictionary schema berakhiran `_tool`.
- Nilai schema berupa dictionary.
- Schema memiliki key `function` berupa dictionary.
- `function.name` tidak kosong.
- Function Python dengan nama persis `function.name` tersedia di file yang sama.
- Function tersebut harus berupa function Python yang dapat dipanggil.
- Parameter schema harus sesuai dengan parameter function.

Jika salah satu syarat tidak terpenuhi, tool tidak dapat digunakan dengan benar. Loader akan mencetak pesan error untuk file yang gagal di-import atau function yang tidak ditemukan.

## Schema Parameter

Schema menggunakan format function tools Ollama:

```python
"parameters": {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Nama user."
        },
        "age": {
            "type": "integer",
            "description": "Umur user."
        },
        "enabled": {
            "type": "boolean",
            "description": "Status aktif atau tidak."
        }
    },
    "required": ["name"]
}
```

Tipe umum:

- `string`: teks.
- `integer`: bilangan bulat.
- `number`: bilangan desimal.
- `boolean`: `true` atau `false`.
- `array`: daftar nilai.
- `object`: object JSON.

Nama parameter pada `properties` harus sama dengan nama parameter function Python karena runtime menjalankan:

```python
function_to_call(**arguments)
```

## Nilai Return

Tool boleh mengembalikan string, dictionary, list, angka, atau nilai JSON lain. Runtime akan mengubah nilai non-string menjadi JSON string sebelum dikirim kembali ke Ollama.

Contoh:

```python
def get_status() -> dict:
    return {
        "status": "ok",
        "message": "Sistem berjalan"
    }
```

Untuk hasil yang mudah dipahami AI, gunakan return yang jelas dan jangan mencetak hasil sebagai satu-satunya output. `print()` hanya untuk log terminal; nilai yang dikembalikan adalah data yang diterima Ollama.

## Beberapa Tool Dalam Satu File

Satu file dapat berisi lebih dari satu tool. Contoh `tools/list/lamp.py` berisi tool untuk menyalakan dan mematikan lampu. Setiap schema harus memiliki nama variable dan `function.name` yang berbeda.

```python
turn_on_lamp_tool = {
    "type": "function",
    "function": {
        "name": "turn_on_lamp",
        "description": "Menyalakan lampu.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}


def turn_on_lamp() -> str:
    return "Lampu menyala."
```

## Aturan Praktis

- Gunakan nama file `snake_case`, misalnya `get_weather.py`.
- Gunakan nama tool `snake_case`, misalnya `get_weather`.
- Jangan memakai suffix `_tool` pada function Python.
- Jangan menggunakan nama function yang sama untuk dua tool berbeda.
- Hindari nama tool yang terlalu umum seperti `run` atau `execute`.
- Validasi input function sebelum menjalankan operasi eksternal.
- Tangani error dan kembalikan pesan yang dapat dipahami AI.
- Jangan menyimpan password, token, atau API key langsung di file tool.

## Pengujian

Pastikan environment aktif, lalu cek jumlah tool yang dimuat:

```bash
.venv/bin/python -c "from tools.list.loader import load_tools; tools, functions = load_tools(); print(len(tools), sorted(functions))"
```

Di Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -c "from tools.list.loader import load_tools; tools, functions = load_tools(); print(len(tools), sorted(functions))"
```

Jika tool baru berhasil dimuat, nama function akan muncul dalam daftar `functions`. Jalankan aplikasi dan berikan perintah yang sesuai dengan deskripsi tool agar Ollama dapat memilihnya.
