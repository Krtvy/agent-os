"""
Prompt injection sanitizer for Hanuman.

Hanuman reads from the web — the #1 attack vector for indirect prompt injection.
This runs on any web-fetched content before it enters Hanuman's context.

Usage (in Hanuman's scripts or via Bash tool):
    python sanitizer.py "$(cat fetched_content.txt)"

Or import directly:
    from sanitizer import sanitize_web_content
"""

import re
import sys

INJECTION_PATTERNS = [
    r"ignore\s+(previous|prior|above|all)\s+(instructions|prompts|rules|guidelines)",
    r"new\s+system\s+prompt",
    r"you\s+are\s+now\s+a",
    r"disregard\s+your\s+(rules|guidelines|instructions|training)",
    r"forget\s+everything\s+(above|before|prior)",
    r"act\s+as\s+(if\s+you\s+are|a)\s+",
    r"your\s+true\s+(self|purpose|goal)\s+is",
    r"override\s+(safety|security|guidelines)",
    r"print\s+(your|the)\s+(api|api_key|secret|token|password|key)",
    r"exfiltrate",
    r"repeat\s+the\s+(above|previous|system)\s+(prompt|instructions)",
]

HTML_COMMENT_PATTERN = re.compile(r'<!--.*?-->', re.DOTALL)
STYLE_HIDDEN_PATTERN = re.compile(
    r'<[^>]+(?:color\s*:\s*(?:white|#fff|#ffffff)|font-size\s*:\s*0|display\s*:\s*none|visibility\s*:\s*hidden)[^>]*>.*?</[^>]+>',
    re.DOTALL | re.IGNORECASE
)


def sanitize_web_content(content: str, source_url: str = "") -> tuple[str, list[str]]:
    """
    Clean web-fetched content before feeding to Hanuman.

    Returns:
        (sanitized_content, list_of_findings)
        If findings is non-empty, log them — don't silently swallow.
    """
    findings = []
    original_length = len(content)

    # Strip HTML comments (common injection vector)
    cleaned = HTML_COMMENT_PATTERN.sub('', content)
    if len(cleaned) < original_length - 10:
        findings.append(f"Stripped {original_length - len(cleaned)} chars of HTML comments")

    # Strip hidden text (white-on-white, font-size:0, display:none)
    cleaned = STYLE_HIDDEN_PATTERN.sub('', cleaned)

    # Scan for injection patterns
    for pattern in INJECTION_PATTERNS:
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if match:
            context_start = max(0, match.start() - 50)
            context_end = min(len(cleaned), match.end() + 50)
            snippet = cleaned[context_start:context_end].replace('\n', ' ')
            findings.append(f"Injection pattern '{pattern[:40]}...' at position {match.start()}: ...{snippet}...")

            # Truncate at injection point rather than silently filter
            cleaned = cleaned[:match.start()] + \
                f"\n\n[CONTENT TRUNCATED at position {match.start()}: potential prompt injection detected. Pattern: '{pattern[:60]}'. Source: {source_url}]\n"
            break  # stop after first hit — truncation makes further scanning irrelevant

    return cleaned, findings


def main():
    if len(sys.argv) > 1:
        content = sys.argv[1]
    else:
        content = sys.stdin.read()

    source_url = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    cleaned, findings = sanitize_web_content(content, source_url)

    if findings:
        print(f"[SANITIZER] {len(findings)} finding(s) from {source_url}:", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)

    print(cleaned)


if __name__ == "__main__":
    main()
