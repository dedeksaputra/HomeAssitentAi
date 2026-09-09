from urllib.parse import quote_plus
import webbrowser
import shutil
import subprocess
import sys


play_music_youtube_tool = {
    "type": "function",
    "function": {
        "name": "play_music_youtube",
        "description": (
            "Memainkan musik YouTube berdasarkan judul yang diberikan user. "
            "Gunakan judul lagu dan artis jika diketahui."
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
    """Memutar musik melalui player lokal atau fallback ke browser."""
    title = str(title or "").strip()
    if not title:
        return {
            "success": False,
            "message": "Judul musik tidak boleh kosong."
        }

    search_url = "https://www.youtube.com/results?search_query=" + quote_plus(title)
    player = shutil.which("mpv") or shutil.which("ffplay")

    if player:
        try:
            yt_dlp = shutil.which("yt-dlp")
            resolver = [yt_dlp] if yt_dlp else [sys.executable, "-m", "yt_dlp"]
            resolved = subprocess.run(
                resolver + ["--get-url", "--format", "bestaudio", "--no-playlist", f"ytsearch1:{title}"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            audio_url = resolved.stdout.strip().splitlines()[0]
            process = subprocess.Popen(
                [player, "--no-video", audio_url]
                if player.endswith("mpv")
                else [player, "-nodisp", "-autoexit", audio_url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return {
                "success": True,
                "message": f"Memutar '{title}' melalui {player}.",
                "player": player,
                "process_id": process.pid,
            }
        except (OSError, subprocess.CalledProcessError, IndexError, subprocess.TimeoutExpired) as error:
            return {
                "success": False,
                "message": f"Player {player} tidak dapat dijalankan: {error}",
                "url": search_url,
            }

    try:
        opened = webbrowser.open_new_tab(search_url)
    except Exception as error:
        return {
            "success": False,
            "message": f"Browser tidak dapat dibuka: {error}",
            "url": search_url,
        }

    return {
        "success": bool(opened),
        "message": (
            "Player lokal mpv/ffplay tidak ditemukan; membuka pencarian "
            f"YouTube untuk '{title}'."
        ),
        "url": search_url,
    }
