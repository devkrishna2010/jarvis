"""
J.A.R.V.I.S. — Web Search Skill
Lightweight web information retrieval using requests and BeautifulSoup4.
Operates with strict connectivity detection and authentic fallback dialogue.
"""

import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Tuple

from core.responses import get_response
import config

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def check_internet_connection(timeout: float = 2.5) -> bool:
    """Verifies active internet connectivity via quick DNS/HTTP ping."""
    try:
        requests.get("https://1.1.1.1", timeout=timeout)
        return True
    except Exception:
        try:
            requests.get("https://www.google.com", timeout=timeout)
            return True
        except Exception:
            return False


def search_web(query: str, max_results: int = 3) -> Tuple[bool, List[Dict[str, str]], str]:
    """
    Performs web search via DuckDuckGo HTML Lite (no API keys, zero bloat).
    Returns (success_boolean, results_list, status_message).
    """
    if not config.ENABLE_WEB_SEARCH:
        return False, [], "Web search capability is currently disabled in configuration, sir."

    if not check_internet_connection():
        return False, [], get_response("no_internet")

    encoded = urllib.parse.quote_plus(query.strip())
    url = f"https://html.duckduckgo.com/html/?q={encoded}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=6.0)
        if resp.status_code != 200:
            return False, [], get_response("error")

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        # Parse DuckDuckGo standard html snippet blocks
        snippets = soup.find_all("div", class_="result__body")
        for snip in snippets[:max_results]:
            title_tag = snip.find("a", class_="result__snippet") or snip.find("a", class_="result__url")
            link_tag = snip.find("a", class_="result__a")
            snippet_tag = snip.find("a", class_="result__snippet")

            title = link_tag.get_text(strip=True) if link_tag else "Result"
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            if snippet:
                results.append({"title": title, "snippet": snippet})

        if not results:
            return False, [], get_response("no_results")

        return True, results, get_response("results_found")

    except Exception as e:
        return False, [], f"{get_response('error')} Connection interrupted: {e}"


def handle_search(intent_res) -> str:
    query = intent_res.parameters.get("query", "")
    if not query:
        return "What would you like me to research, sir?"

    success, results, msg = search_web(query, max_results=2)
    if not success or not results:
        return msg

    # Format into concise, elegant J.A.R.V.I.S. response
    top = results[0]
    summary = f"{msg} Regarding '{query}': {top['snippet']}"
    return summary

