def execute(
    param: str
) -> dict:

    param = str(
        param
    ).strip()

    if not param:

        return {
            "success": False,
            "informasi": "Lokasi lampu tidak diberikan."
        }

    # ==========================================
    # LOGIC MATIKAN LAMPU
    # ==========================================

    # Contoh sementara
    print(
        f"Menghidupkan lampu: {param}"
    )

    return {
        "success": True,
        "informasi": (
            f"Lampu di {param} "
            "berhasil dihidupkan."
        )
    }