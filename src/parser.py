"""HTML cleaner and sentence/statement extractor for Greenhouse job descriptions."""

import html
import re

BLOCK_TAG_PATTERN = re.compile(
    r"</?(?:p|li|ul|ol|div|h[1-6]|tr|td|th|section|article|blockquote|hr)\b[^>]*>|<br\s*/?>",
    flags=re.IGNORECASE,
)
INLINE_TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"[ \t\r\f\v]+")
SENTENCE_SPLIT_PATTERN = re.compile(
    r"(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)(?<!\bMr)(?<!\bMs)(?<!\bDr)(?<!\bSr)(?<!\bJr)(?<!\bInc)(?<!\bLtd)"
    r"(?<=[.!?])\s+(?=[A-Z0-9])"
)
LEADING_BULLET_PATTERN = re.compile(r"^[\s•·\-–—*]+")


def unescape_and_strip_html(raw_content: str) -> str:
    """
    Decodes double-escaped HTML entities from Greenhouse and converts HTML block tags into newlines.
    """
    if not raw_content:
        return ""
    # Greenhouse often encodes HTML entities once or twice (e.g. &lt;p&gt; and &amp;amp;)
    decoded = html.unescape(html.unescape(raw_content))
    # Replace non-breaking spaces with regular spaces
    decoded = decoded.replace("\xa0", " ").replace("&nbsp;", " ")
    # Convert block tags into line breaks so list items stay separate
    with_breaks = BLOCK_TAG_PATTERN.sub("\n", decoded)
    # Remove remaining inline HTML tags
    without_tags = INLINE_TAG_PATTERN.sub(" ", with_breaks)
    return without_tags


def extract_candidate_statements(raw_content: str, min_length: int = 20) -> list[str]:
    """
    Extracts clean, deduplicated sentences/bullet statements from raw Greenhouse job HTML.
    """
    cleaned_block_text = unescape_and_strip_html(raw_content)
    statements: list[str] = []
    seen: set[str] = set()

    for raw_line in cleaned_block_text.splitlines():
        normalized_line = WHITESPACE_PATTERN.sub(" ", raw_line).strip()
        normalized_line = LEADING_BULLET_PATTERN.sub("", normalized_line).strip()
        if len(normalized_line) < min_length:
            continue

        # Split long multi-sentence paragraphs while preserving individual bullets
        parts = SENTENCE_SPLIT_PATTERN.split(normalized_line)
        for part in parts:
            clean_part = LEADING_BULLET_PATTERN.sub("", part).strip()
            if len(clean_part) < min_length:
                continue
            key = clean_part.lower()
            if key not in seen:
                seen.add(key)
                statements.append(clean_part)

    return statements
