from datetime import datetime

def execute(
    param: str
) -> dict:

    param = str(
        param
    ).strip()

    if not param:

        return {
            "success": False,
            "informasi": "parameter salah"
        }
    # ==========================================
    # LOGIC MATIKAN LAMPU
    # ==========================================

    # Contoh sementara
    time = get_datetime()


    return {
        "success": True,
        "informasi": (
            f"DATA WAKTU saat ini : {time} "
        )
    }
    
    
def get_datetime():

    """
    Mendapatkan tanggal dan waktu aktual
    dari komputer tempat AI berjalan.
    """

    now = datetime.now()

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
        "tanggal": now.strftime(
            "%Y-%m-%d"
        ),
        "jam": now.strftime(
            "%H:%M:%S"
        ),
        "hari": days[
            now.weekday()
        ],
        "bulan": months[
            now.month - 1
        ],
        "tahun": now.year
    }