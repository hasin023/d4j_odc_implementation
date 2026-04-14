"""Robust web content retrieval for bug report URLs.

Architecture inspired by claw-code's WebFetchTool (rust/crates/tools/src/lib.rs).
Supports GitHub Issues, Apache JIRA, and generic HTML pages with structured
content extraction optimised for LLM consumption.

Design decisions (from claw-code):
  - Structured output: every fetch returns a WebFetchResult, never raises.
  - URL normalisation: auto-upgrade HTTP→HTTPS (except localhost).
  - Source-specific extractors route first; on *any* failure they fall through
    instantly to the generic HTML extractor — the generic path is the backbone.
  - HTML-to-text mirrors claw-code's tag-stripping + entity-decoding pipeline.
"""

from __future__ import annotations

import html
import re
import time
from dataclasses import dataclass, field
from urllib.parse import urlparse

import requests


# ---------------------------------------------------------------------------
# Structured result (mirrors claw-code WebFetchOutput)
# ---------------------------------------------------------------------------

@dataclass
class WebFetchResult:
    """Result of a bug report fetch operation.

    Always populated — ``error`` is set on failure instead of raising.
    """

    content: str = ""
    url: str = ""
    status_code: int = 0
    source_type: str = "unknown"       # "github", "jira", "generic"
    duration_ms: int = 0
    content_length: int = 0
    error: str | None = None


# ---------------------------------------------------------------------------
# HTTP client factory (mirrors claw-code build_http_client)
# ---------------------------------------------------------------------------

_DEFAULT_TIMEOUT = 20        # seconds — matches claw-code
_MAX_REDIRECTS = 10          # matches claw-code redirect policy
_USER_AGENT = "D4J-ODC-Pipeline/0.2 (research tool)"


def _build_http_session() -> requests.Session:
    """Create a reusable HTTP session with sane defaults.

    Mirrors claw-code ``build_http_client`` (L2835-2842):
      - 20s timeout
      - 10-redirect limit
      - Custom user-agent
    """
    session = requests.Session()
    session.headers.update({"User-Agent": _USER_AGENT})
    session.max_redirects = _MAX_REDIRECTS
    return session


# ---------------------------------------------------------------------------
# URL normalisation (mirrors claw-code normalize_fetch_url)
# ---------------------------------------------------------------------------

def _normalize_url(url: str) -> str:
    """Normalise a URL: upgrade plain HTTP to HTTPS unless localhost.

    Mirrors claw-code ``normalize_fetch_url`` (L2844-2857).
    """
    parsed = urlparse(url)
    if parsed.scheme == "http" and parsed.hostname not in ("localhost", "127.0.0.1", "::1"):
        return parsed._replace(scheme="https").geturl()
    return url


# ---------------------------------------------------------------------------
# HTML → text pipeline (mirrors claw-code html_to_text + helpers)
# ---------------------------------------------------------------------------

# Tags whose *entire content* should be removed before text extraction.
_STRIP_BLOCK_TAGS = re.compile(
    r"<\s*(script|style|nav|header|footer|noscript|svg|iframe)"
    r"[^>]*>.*?</\s*\1\s*>",
    re.DOTALL | re.IGNORECASE,
)

# Any remaining HTML tags.
_STRIP_TAGS = re.compile(r"<[^>]+>")


def decode_html_entities(text: str) -> str:
    """Decode common HTML entities to their character equivalents.

    Mirrors claw-code ``decode_html_entities`` (L2959-2967), then falls
    through to Python's ``html.unescape`` for full coverage.
    """
    # Fast-path the most common entities (matches claw-code exactly).
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = text.replace("&nbsp;", " ")
    # Catch any remaining entities Python knows about.
    return html.unescape(text)


def collapse_whitespace(text: str) -> str:
    """Collapse runs of whitespace to single spaces.

    Mirrors claw-code ``collapse_whitespace`` (L2969-2970).
    """
    return " ".join(text.split())


def html_to_text(raw_html: str) -> str:
    """Convert raw HTML to clean plain text.

    Mirrors claw-code ``html_to_text`` (L2929-2957):
      1. Remove script/style/nav/header/footer blocks entirely.
      2. Strip remaining tags.
      3. Decode HTML entities.
      4. Collapse whitespace.
    """
    # 1. Remove entire blocks that never contain useful content.
    text = _STRIP_BLOCK_TAGS.sub(" ", raw_html)
    # 2. Strip remaining tags character-by-character (mirrors claw-code loop).
    text = _STRIP_TAGS.sub(" ", text)
    # 3. Decode entities.
    text = decode_html_entities(text)
    # 4. Collapse whitespace.
    return collapse_whitespace(text)


def preview_text(text: str, max_chars: int) -> str:
    """Truncate text to *max_chars* with an ellipsis marker.

    Mirrors claw-code ``preview_text`` (L2973-2978).
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "… [truncated]"


# ---------------------------------------------------------------------------
# Source detection
# ---------------------------------------------------------------------------

_GITHUB_ISSUE_RE = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/issues/(?P<number>\d+)",
    re.IGNORECASE,
)

_JIRA_BROWSE_RE = re.compile(
    r"(?P<host>[^/]+)/(?:jira/)?browse/(?P<key>[A-Z][\w]+-\d+)",
    re.IGNORECASE,
)


def _detect_source(url: str) -> str:
    """Classify a URL as 'github', 'jira', or 'generic'."""
    if _GITHUB_ISSUE_RE.search(url):
        return "github"
    if _JIRA_BROWSE_RE.search(url):
        return "jira"
    return "generic"


# ---------------------------------------------------------------------------
# Source-specific extractors (each falls back to generic on ANY failure)
# ---------------------------------------------------------------------------

def _fetch_github_issue(url: str, session: requests.Session) -> str | None:
    """Try to fetch a GitHub issue via the REST API.

    Returns extracted text on success, or ``None`` to signal fallback to
    the generic extractor.
    """
    match = _GITHUB_ISSUE_RE.search(url)
    if not match:
        return None

    owner, repo, number = match.group("owner"), match.group("repo"), match.group("number")
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"

    try:
        resp = session.get(
            api_url,
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=_DEFAULT_TIMEOUT,
        )
        if resp.status_code != 200:
            return None

        data = resp.json()
        parts: list[str] = []

        title = data.get("title", "")
        if title:
            parts.append(f"Title: {title}")

        state = data.get("state", "")
        labels = [label.get("name", "") for label in data.get("labels", []) if label.get("name")]
        if state or labels:
            meta_parts = []
            if state:
                meta_parts.append(f"State: {state}")
            if labels:
                meta_parts.append(f"Labels: {', '.join(labels)}")
            parts.append(" | ".join(meta_parts))

        body = data.get("body", "") or ""
        if body:
            parts.append(f"\nDescription:\n{body.strip()}")

        # Fetch first few comments for additional context
        comments_url = data.get("comments_url", "")
        comments_count = data.get("comments", 0)
        if comments_url and comments_count > 0:
            try:
                comments_resp = session.get(
                    comments_url,
                    params={"per_page": min(comments_count, 5)},
                    timeout=_DEFAULT_TIMEOUT,
                )
                if comments_resp.status_code == 200:
                    comments = comments_resp.json()
                    if comments:
                        parts.append("\nComments:")
                        for comment in comments[:5]:
                            author = comment.get("user", {}).get("login", "unknown")
                            comment_body = comment.get("body", "").strip()
                            if comment_body:
                                parts.append(f"\n[{author}]: {comment_body}")
            except Exception:
                pass  # comments are best-effort

        return "\n".join(parts) if parts else None

    except Exception:
        return None  # fall through to generic


def _fetch_jira_issue(url: str, session: requests.Session) -> str | None:
    """Try to fetch a JIRA issue via the REST API.

    Returns extracted text on success, or ``None`` to signal fallback to
    the generic extractor.
    """
    match = _JIRA_BROWSE_RE.search(url)
    if not match:
        return None

    host = match.group("host")
    issue_key = match.group("key")

    # Build the REST API URL — works for both Atlassian Server and Cloud.
    # Try with /jira/ prefix first (common for Apache), then without.
    parsed = urlparse(url)
    base_scheme = parsed.scheme or "https"
    api_urls = [
        f"{base_scheme}://{host}/jira/rest/api/2/issue/{issue_key}",
        f"{base_scheme}://{host}/rest/api/2/issue/{issue_key}",
    ]

    for api_url in api_urls:
        try:
            resp = session.get(
                api_url,
                params={"fields": "summary,description,comment,priority,issuetype,status,resolution"},
                timeout=_DEFAULT_TIMEOUT,
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            fields = data.get("fields", {})
            parts: list[str] = []

            summary = fields.get("summary", "")
            if summary:
                parts.append(f"Title: {summary}")

            # Metadata line
            meta_parts = []
            issue_type = fields.get("issuetype", {})
            if isinstance(issue_type, dict) and issue_type.get("name"):
                meta_parts.append(f"Type: {issue_type['name']}")
            priority = fields.get("priority", {})
            if isinstance(priority, dict) and priority.get("name"):
                meta_parts.append(f"Priority: {priority['name']}")
            status = fields.get("status", {})
            if isinstance(status, dict) and status.get("name"):
                meta_parts.append(f"Status: {status['name']}")
            resolution = fields.get("resolution", {})
            if isinstance(resolution, dict) and resolution.get("name"):
                meta_parts.append(f"Resolution: {resolution['name']}")
            if meta_parts:
                parts.append(" | ".join(meta_parts))

            description = fields.get("description", "") or ""
            if description:
                parts.append(f"\nDescription:\n{description.strip()}")

            # Comments (first few)
            comment_data = fields.get("comment", {})
            comments = comment_data.get("comments", []) if isinstance(comment_data, dict) else []
            if comments:
                parts.append("\nComments:")
                for comment in comments[:5]:
                    author_data = comment.get("author", {})
                    author = author_data.get("displayName") or author_data.get("name", "unknown")
                    comment_body = comment.get("body", "").strip()
                    if comment_body:
                        parts.append(f"\n[{author}]: {comment_body}")

            result = "\n".join(parts) if parts else None
            if result:
                return result

        except Exception:
            continue  # try next API URL, then fall through to generic

    return None  # all API attempts failed → fall through to generic


def _fetch_generic_page(response: requests.Response) -> str:
    """Extract meaningful text from a generic HTML page.

    This is the backbone extractor — the most important path.
    Mirrors claw-code's ``normalize_fetched_content`` + ``html_to_text``
    pipeline (L2872-2957).
    """
    content_type = response.headers.get("Content-Type", "")

    if "html" in content_type.lower():
        raw = response.text
        text = html_to_text(raw)
    elif "json" in content_type.lower():
        # Some APIs return JSON directly
        try:
            data = response.json()
            text = _flatten_json_for_display(data)
        except Exception:
            text = response.text.strip()
    else:
        # Plain text, XML, or others — just use the text as-is
        text = response.text.strip()

    return text


def _flatten_json_for_display(data: object, max_depth: int = 3) -> str:
    """Flatten a JSON structure into readable key-value text."""
    lines: list[str] = []

    def _walk(obj: object, prefix: str = "", depth: int = 0) -> None:
        if depth > max_depth:
            return
        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                if isinstance(value, (dict, list)):
                    _walk(value, full_key, depth + 1)
                else:
                    str_val = str(value).strip()
                    if str_val and str_val != "None":
                        lines.append(f"{full_key}: {str_val}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj[:10]):  # limit array items
                _walk(item, f"{prefix}[{i}]", depth + 1)

    _walk(data)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def fetch_bug_report(url: str, *, max_chars: int = 12_000) -> WebFetchResult:
    """Fetch and extract meaningful content from a bug report URL.

    This is the main entry point — mirrors claw-code's ``execute_web_fetch``
    (L2747-2779).

    Routing logic:
      1. Detect source type (github / jira / generic).
      2. Try the source-specific API extractor.
      3. On *any* failure, instantly fall back to the generic HTML extractor.
      4. Truncate to ``max_chars`` with ``preview_text()``.
      5. Return a ``WebFetchResult`` — never raises.
    """
    if not url or not url.strip():
        return WebFetchResult(error="empty URL")

    start_time = time.monotonic()
    source_type = _detect_source(url)
    normalized_url = _normalize_url(url.strip())
    session = _build_http_session()

    try:
        # ── Phase 1: Try source-specific API extraction ───────────
        api_content: str | None = None

        if source_type == "github":
            api_content = _fetch_github_issue(normalized_url, session)
        elif source_type == "jira":
            api_content = _fetch_jira_issue(normalized_url, session)

        # ── Phase 2: If API succeeded, use its result ─────────────
        if api_content:
            content = preview_text(api_content.strip(), max_chars)
            elapsed = int((time.monotonic() - start_time) * 1000)
            return WebFetchResult(
                content=content,
                url=normalized_url,
                status_code=200,
                source_type=source_type,
                duration_ms=elapsed,
                content_length=len(content),
            )

        # ── Phase 3: Fall through to generic page extraction ──────
        #    This is the backbone — the most important path.
        response = session.get(normalized_url, timeout=_DEFAULT_TIMEOUT)
        final_url = response.url
        status = response.status_code

        if status >= 400:
            elapsed = int((time.monotonic() - start_time) * 1000)
            return WebFetchResult(
                url=str(final_url),
                status_code=status,
                source_type="generic",
                duration_ms=elapsed,
                error=f"HTTP {status} — {response.reason}",
            )

        text = _fetch_generic_page(response)
        content = preview_text(text, max_chars)
        elapsed = int((time.monotonic() - start_time) * 1000)

        return WebFetchResult(
            content=content,
            url=str(final_url),
            status_code=status,
            source_type=source_type if api_content is None else "generic",
            duration_ms=elapsed,
            content_length=len(content),
        )

    except requests.exceptions.Timeout:
        elapsed = int((time.monotonic() - start_time) * 1000)
        return WebFetchResult(
            url=normalized_url,
            source_type=source_type,
            duration_ms=elapsed,
            error=f"request timed out after {_DEFAULT_TIMEOUT}s",
        )

    except requests.exceptions.ConnectionError as exc:
        elapsed = int((time.monotonic() - start_time) * 1000)
        return WebFetchResult(
            url=normalized_url,
            source_type=source_type,
            duration_ms=elapsed,
            error=f"connection error: {exc}",
        )

    except Exception as exc:
        elapsed = int((time.monotonic() - start_time) * 1000)
        return WebFetchResult(
            url=normalized_url,
            source_type=source_type,
            duration_ms=elapsed,
            error=f"unexpected error: {exc}",
        )

    finally:
        session.close()
