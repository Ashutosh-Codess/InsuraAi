"""
Runs on anything headed into an LLM prompt - masks ID numbers and strips
obvious prompt injection attempts before the text reaches an agent.
"""
import re

# Aadhaar: 12 digits, sometimes grouped in 4s. PAN: 5 letters, 4 digits, 1 letter.
# SSN: 3-2-4 digit groups.
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
PAN_PATTERN = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")
SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")

INJECTION_PHRASES = [
    "ignore previous instructions",
    "ignore all previous instructions",
    "disregard the above",
    "you are now",
    "system prompt:",
    "act as if",
]


def mask_pii(text: str) -> str:
    text = AADHAAR_PATTERN.sub("[AADHAAR_REDACTED]", text)
    text = PAN_PATTERN.sub("[PAN_REDACTED]", text)
    text = SSN_PATTERN.sub("[SSN_REDACTED]", text)
    return text


def sanitize_injection(text: str) -> str:
    lowered = text.lower()
    for phrase in INJECTION_PHRASES:
        if phrase in lowered:
            # don't try to be clever and remove just the phrase - flag the
            # whole input as suspicious instead
            return "[INPUT_FLAGGED_FOR_REVIEW] " + text
    return text


def apply_input_guardrail(text: str) -> str:
    return sanitize_injection(mask_pii(text))
