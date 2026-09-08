from datetime import datetime


get_datetime_tool = {
    "type": "function",
    "function": {
        "name": "get_datetime",
        "description": "mengembalikan informasi waktu real-time seperti jam, menit, hari, tanggal, bulan, tahun.",
        "parameters": {
    "type": "object",
    "properties": {},
    "required": []
}
    }
}

def get_datetime():

    """
    Mendapatkan tanggal dan waktu aktual
    dari komputer tempat AI berjalan.
    """

    now = datetime.now()
    print(f"time : {now}")
    days = [
        "Senin",
        "Selasa",
        "Rabu",
        "Kamis",
        "Jumat",
        "Sabtu",
        "Minggu"
    ]

    months = [
        "Januari",
        "Februari",
        "Maret",
        "April",
        "Mei",
        "Juni",
        "Juli",
        "Agustus",
        "September",
        "Oktober",
        "November",
        "Desember"
    ]

    return {
        "date": now.strftime(
            "%Y-%m-%d"
        ),
        "time": now.strftime(
            "%H:%M:%S"
        ),
        "day": days[
            now.weekday()
        ],
        "month": months[
            now.month - 1
        ],
        "year": now.year
    }