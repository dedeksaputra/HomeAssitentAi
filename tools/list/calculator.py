add_two_numbers_tool = {
    "type": "function",
    "function": {
        "name": "add_two_numbers",
        "description": "Menjumlahkan dua angka.",
        "parameters": {
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {
                    "type": "integer",
                    "description": "Angka pertama."
                },
                "b": {
                    "type": "integer",
                    "description": "Angka kedua."
                }
            }
        }
    }
}


def add_two_numbers(a: int, b: int) -> int:
    return a + b