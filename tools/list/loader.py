import importlib
import inspect
from pathlib import Path


def load_tools():
    tools = []
    available_functions = {}

    tools_dir = Path(__file__).parent

    for file in tools_dir.glob("*.py"):

        if file.name in ("__init__.py", "loader.py"):
            continue

        module_name = f"{__package__}.{file.stem}"

        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            print(f"[TOOLS] Failed to load {file.name}: {e}")
            continue

        for name, value in vars(module).items():

            # Cari variable yang berakhiran _tool
            if not name.endswith("_tool"):
                continue

            if not isinstance(value, dict):
                continue

            function_data = value.get("function")

            if not isinstance(function_data, dict):
                continue

            tool_name = function_data.get("name")

            if not tool_name:
                continue

            # Tambahkan schema untuk Ollama
            tools.append(value)

            # Cari function Python berdasarkan nama schema
            function = getattr(module, tool_name, None)

            if function is None or not inspect.isfunction(function):
                print(
                    f"[TOOLS] Function '{tool_name}' "
                    f"tidak ditemukan."
                )
                continue

            # Tambahkan function untuk executor
            available_functions[tool_name] = function

    return tools, available_functions