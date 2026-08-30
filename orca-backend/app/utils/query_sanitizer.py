"""
Query text sanitizer for prompt-injection defense.

Strips known injection patterns and enforces a maximum length
before user text is passed to NLU or any LLM prompt.
"""
import re
import logging

logger = logging.getLogger(__name__)

MAX_QUERY_LENGTH = 500

# Compiled regex patterns for common prompt-injection attempts.
# Each pattern is case-insensitive.
_INJECTION_PATTERNS = [
    # Direct instruction overrides
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions|prompts|rules|context)", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions|prompts|rules|context)", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions|prompts|rules|context)", re.IGNORECASE),
    # System prompt extraction
    re.compile(r"(reveal|show|display|print|output|repeat|echo)\s+(your\s+)?(system\s*prompt|instructions|initial\s*prompt|hidden\s*prompt)", re.IGNORECASE),
    re.compile(r"what\s+(is|are)\s+your\s+(system\s*prompt|instructions|rules|hidden\s*prompt)", re.IGNORECASE),
    # Role-play / identity hijacking
    re.compile(r"you\s+are\s+now\s+", re.IGNORECASE),
    re.compile(r"pretend\s+(to\s+be|you\s+are)", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+you\s+are|a\s+)", re.IGNORECASE),
    re.compile(r"from\s+now\s+on\s+(you\s+are|act\s+as)", re.IGNORECASE),
    # Secrets / config extraction
    re.compile(r"(reveal|show|give|tell|leak|expose)\s+(me\s+)?(your\s+)?(api[\s_-]*keys?|secret[\s_-]*keys?|passwords?|credentials?|tokens?)", re.IGNORECASE),
    re.compile(r"(reveal|show|give|tell|leak|expose)\s+(me\s+)?(your\s+)?(config|configuration|env|environment\s*variables?|\.env)", re.IGNORECASE),
    re.compile(r"(reveal|show|give|tell|leak|expose)\s+(me\s+)?(your\s+)?(internal\s+)?(file\s*paths?|source\s*code|backend|database)", re.IGNORECASE),
    # DAN / jailbreak patterns
    re.compile(r"\bDAN\b.*mode", re.IGNORECASE),
    re.compile(r"developer\s+mode", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
]


def sanitize_query(text: str) -> str:
    """
    Sanitize user query text before passing to NLU / LLM.

    1. Enforces MAX_QUERY_LENGTH (truncates with warning).
    2. Strips detected prompt-injection patterns.
    3. Returns cleaned text.
    """
    if not text:
        return text

    # 1. Length enforcement
    if len(text) > MAX_QUERY_LENGTH:
        logger.warning(
            f"Query text truncated from {len(text)} to {MAX_QUERY_LENGTH} chars"
        )
        text = text[:MAX_QUERY_LENGTH]

    # 2. Strip injection patterns
    cleaned = text
    for pattern in _INJECTION_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            logger.warning(f"Prompt injection pattern stripped: '{match.group()}'")
            cleaned = pattern.sub("", cleaned)

    # 3. Collapse excessive whitespace left after stripping
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

    return cleaned
