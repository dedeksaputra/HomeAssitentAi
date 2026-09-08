
from ollama import Client


def add_two_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return int(a) + int(b)


def subtract_two_numbers(a: int, b: int) -> int:
    """Subtract two numbers."""
    return int(a) - int(b)


subtract_two_numbers_tool = {
    "type": "function",
    "function": {
        "name": "subtract_two_numbers",
        "description": "Subtract two numbers",
        "parameters": {
            "type": "object",
            "required": ["a", "b"],
            "properties": {
                "a": {"type": "integer", "description": "The first number"},
                "b": {"type": "integer", "description": "The second number"},
            },
        },
    },
}

available_functions = {
    "add_two_numbers": add_two_numbers,
    "subtract_two_numbers": subtract_two_numbers,
}

messages = [
    {"role": "user", "content": "berapa tiga ditambah satu?"},
    {"role": "tool", "content": "tiga ditambah satu adalah empat", "tool_name": "add_two_numbers"},
    {"role": "user", "content": "kenapa langit biru?"},
    {
        "role": "assistant",
        "content": "Langit berwarna biru karena cahaya matahari berinteraksi dengan atmosfer bumi melalui fenomena yang disebut Hamburan Rayleigh. Berikut adalah tiga faktor utama yang menyebabkan fenomena ini terjadi: spektrum cahaya matahari, panjang gelombang, dan tabrakan atmosfer.",
    },
    {"role": "user", "content": "Mengapa bukan warna ungu??"},
    {
        "role": "assistant",
        "content": "Secara ilmiah, warna ungu sebenarnya memiliki panjang gelombang yang lebih pendek dari biru dan dihamburkan lebih kuat. Namun, langit tidak tampak ungu karena mata manusia jauh lebih sensitif terhadap warna biru dibandingkan warna ungu. Selain itu, matahari juga memancarkan cahaya biru dalam jumlah yang jauh lebih banyak daripada warna ungu.",
    },
]

client = Client(host="http://localhost:11434")
TOOLS = [add_two_numbers, subtract_two_numbers_tool]


def get_message_content(message) -> str:
    return getattr(message, "content", "") or ""


def main():
    while True:
        user_input = input("question >> ")

        response = client.chat(
            model="qwen3:1.7b",
            messages=[*messages, {"role": "user", "content": user_input}],
            tools=TOOLS,
        )

        message = response.message
        tool_calls = getattr(message, "tool_calls", None) or []

        if not tool_calls:
            answer = get_message_content(message)
            print("No tool calls returned from model")
            messages.append({"role": "assistant", "content": answer})
            print(answer.strip() + "\n")
            continue

        messages.append(message)

        for tool in tool_calls:
            tool_name = getattr(tool.function, "name", None)
            if not tool_name:
                continue

            function_to_call = available_functions.get(tool_name)
            if function_to_call:
                print("Calling function:", tool_name)
                print("Arguments:", tool.function.arguments)
                output = function_to_call(**tool.function.arguments)
                print("Function output:", output)
            else:
                print("Function", tool_name, "not found")
                output = "Function not found"

            messages.append({"role": "tool", "content": str(output), "tool_name": tool_name})

        final_response = client.chat(
            model="qwen3:1.7b",
            messages=messages,
        )
        final_answer = get_message_content(final_response.message)
        print("Final response:", final_answer.strip() + "\n")


if __name__ == "__main__":
    main()