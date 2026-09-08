turn_on_lamp_tool = {
    "type": "function",
    "function": {
        "name": "turn_on_lamp",
        "description": "Menyalakan lampu pada ruangan tertentu.",
        "parameters": {
            "type": "object",
            "required": ["room"],
            "properties": {
                "room": {
                    "type": "string",
                    "description": "Nama ruangan tempat lampu berada."
                }
            }
        }
    }
}


def turn_on_lamp(room: str) -> str:
    """Menyalakan lampu pada ruangan tertentu."""

    print(f"Menyalakan lampu: {room}")

    return f"Lampu {room} berhasil dinyalakan."


turn_off_lamp_tool = {
    "type": "function",
    "function": {
        "name": "turn_off_lamp",
        "description": "Mematikan lampu pada ruangan tertentu.",
        "parameters": {
            "type": "object",
            "required": ["room"],
            "properties": {
                "room": {
                    "type": "string",
                    "description": "Nama ruangan tempat lampu berada."
                }
            }
        }
    }
}


def turn_off_lamp(room: str) -> str:
    """Mematikan lampu pada ruangan tertentu."""

    print(f"Mematikan lampu: {room}")

    return f"Lampu {room} berhasil dimatikan."