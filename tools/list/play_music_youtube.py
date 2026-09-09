from urllib.parse import quote_plus
import webbrowser


play_music_youtube_tool = {
    "type": "function",
    "function": {
        "name": "play_music_youtube",
        "description": (
            "Membuka pencarian YouTube untuk memainkan musik berdasarkan judul "
            "yang diberikan user. Gunakan judul lagu dan artis jika diketahui."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Judul musik atau judul musik beserta nama artis."
                }
            },
            "required": ["title"]
        }
    }
}


def play_music_youtube(title: str) -> dict:
    """Membuka hasil pencarian musik di YouTube."""
    title = str(title or "").strip()
    if not title:
        return {
            "success": False,
            "message": "Judul musik tidak boleh kosong."
        }

    url = "https://www.youtube.com/results?search_query=" + quote_plus(title)

    try:
        opened = webbrowser.open_new_tab(url)
    except Exception as error:
        return {
            "success": False,
            "message": f"Browser tidak dapat dibuka: {error}",
            "url": url,
        }

    return {
        "success": bool(opened),
        "message": f"Membuka pencarian YouTube untuk '{title}'.",
        "url": url,
    }
