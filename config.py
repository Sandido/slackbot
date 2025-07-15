import os

# ── Numeric “magic” values ──────────────────────────
REQUEST_TTL_SECONDS = int(os.getenv("REQUEST_TTL_SECONDS", 60 * 5))   # 5 min
HISTORY_LOOKBACK     = int(os.getenv("HISTORY_LOOKBACK", 5))          # Slack API limit
HTTP_PORT            = int(os.getenv("HTTP_PORT", 5000))              # Flask port

# ── Paths / strings that shouldn’t be sprinkled around ──────────────
SLACK_EVENTS_PATH    = os.getenv("SLACK_EVENTS_PATH", "/slack/events")

# ── Domain constants you may reuse elsewhere ────────────────────────
RECOGNIZED_LANGS = {
    "english", "japanese", "spanish", "french", "german",
    "italian", "korean", "dutch", "portuguese", "russian", "hebrew",
}
