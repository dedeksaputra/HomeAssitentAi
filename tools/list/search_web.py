from html.parser import HTMLParser
import base64
import re
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse
from urllib.request import Request, urlopen


search_web_tool = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": (
            "Mencari informasi terkini di web berdasarkan pertanyaan user. "
            "Gunakan untuk data yang tidak tersedia di history atau tools lain."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Pertanyaan atau kata kunci yang dicari di web."
                },
                "max_results": {
                    "type": "integer",
                    "description": "Jumlah hasil, antara 1 dan 5."
                }
            },
            "required": ["query"]
        }
    }
}


class _DuckDuckGoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._current = None
        self._capture_title = False
        self._capture_snippet = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()

        if tag == "a" and "result__a" in classes:
            self._current = {
                "title": "",
                "url": urljoin("https://html.duckduckgo.com", attributes.get("href", "")),
                "snippet": "",
            }
            self._capture_title = True
        elif self._current and "result__snippet" in classes:
            self._capture_snippet = True

    def handle_data(self, data):
        if not self._current:
            return
        if self._capture_title:
            self._current["title"] += data
        elif self._capture_snippet:
            self._current["snippet"] += data

    def handle_endtag(self, tag):
        if tag == "a" and self._capture_title:
            self._capture_title = False
        if self._capture_snippet and tag in {"a", "div"}:
            self._capture_snippet = False
            if self._current["title"] and self._current["url"]:
                self.results.append(self._current)
                self._current = None


class _BingParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._current = None
        self._capture_title = False
        self._capture_snippet = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = attributes.get("class", "").split()

        if tag == "li" and "b_algo" in classes:
            self._current = {"title": "", "url": "", "snippet": ""}
        elif self._current and tag == "a" and not self._current["url"]:
            self._current["url"] = attributes.get("href", "")
            self._capture_title = True
        elif self._current and tag == "p":
            self._capture_snippet = True

    def handle_data(self, data):
        if not self._current:
            return
        if self._capture_title:
            self._current["title"] += data
        elif self._capture_snippet:
            self._current["snippet"] += data

    def handle_endtag(self, tag):
        if tag == "a":
            self._capture_title = False
        elif tag == "p":
            self._capture_snippet = False
        elif tag == "li" and self._current:
            if self._current["title"] and self._current["url"]:
                self.results.append(self._current)
            self._current = None


def _clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value.split("https://", 1)[0].strip() or value


def _normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if "bing.com" not in parsed.netloc:
        return url

    encoded_url = parse_qs(parsed.query).get("u", [""])[0]
    if not encoded_url.startswith("a1"):
        return url

    try:
        decoded = base64.urlsafe_b64decode(encoded_url[2:] + "===")
        return decoded.decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return url


def search_web(query: str, max_results: int = 5) -> dict:
    """Mencari hasil web ringkas dari DuckDuckGo HTML."""
    query = str(query or "").strip()
    if not query:
        return {"success": False, "message": "Query pencarian tidak boleh kosong."}

    try:
        max_results = max(1, min(int(max_results), 5))
    except (TypeError, ValueError):
        max_results = 5

    request = Request(
        "https://html.duckduckgo.com/html/?q=" + quote_plus(query),
        headers={"User-Agent": "HomeAssisten/1.0"},
    )

    try:
        with urlopen(request, timeout=10) as response:
            html = response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError, TimeoutError) as error:
        return {"success": False, "message": f"Pencarian web gagal: {error}"}

    parser = _DuckDuckGoParser()
    parser.feed(html)
    if not parser.results:
        bing_request = Request(
            "https://www.bing.com/search?q=" + quote_plus(query),
            headers={"User-Agent": "Mozilla/5.0 HomeAssisten/1.0"},
        )
        try:
            with urlopen(bing_request, timeout=10) as response:
                bing_html = response.read().decode("utf-8", errors="replace")
            parser = _BingParser()
            parser.feed(bing_html)
        except (HTTPError, URLError, TimeoutError):
            pass
    results = []
    for result in parser.results:
        result = {key: _clean_text(value) for key, value in result.items()}
        result["url"] = _normalize_url(result["url"])
        if urlparse(result["url"]).scheme in {"http", "https"}:
            results.append(result)
        if len(results) >= max_results:
            break

    return {
        "success": bool(results),
        "query": query,
        "results": results,
        "message": "Hasil pencarian siap diringkas oleh AI." if results else "Tidak ada hasil ditemukan.",
    }
