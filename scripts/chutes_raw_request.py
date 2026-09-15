"""Small, direct, non-streaming Chutes probe.

Run with:
    CHUTES_API_KEY=cpk_... python scripts/chutes_raw_request.py

Set CHUTES_MODEL to the model ID enabled for your account. The default is the
Qwen3.8 27B Chutes model.
"""

import json
import os
from pathlib import Path
import urllib.request


URL = "https://llm.chutes.ai/v1/chat/completions"


def load_dotenv() -> None:
    """Load simple KEY=VALUE entries from the repository's local .env file."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if value[:1] in {"'", '"'} and value[-1:] == value[:1]:
            value = value[1:-1]
        os.environ.setdefault(key, value)


load_dotenv()
MODEL = os.getenv("CHUTES_MODEL", "Qwen/Qwen3.8-27B-TEE")
API_KEY = os.environ["CHUTES_API_KEY"]

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Reply with exactly: hello from Chutes"}],
    "temperature": 0,
    "stream": False,
}

request = urllib.request.Request(
    URL,
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    method="POST",
)

with urllib.request.urlopen(request) as response:
    raw_body = response.read().decode()
    raw_response = {
        "status_code": response.status,
        "headers": dict(response.headers),
        "body": json.loads(raw_body),
    }

print("RAW REQUEST")
print(json.dumps({"url": URL, "headers": {"Authorization": "Bearer <redacted>", "Content-Type": "application/json"}, "json": payload}, indent=2))
print("\nRAW RESPONSE")
print(json.dumps(raw_response, indent=2))
print("\nPARSED RESULT")
print(raw_response["body"]["choices"][0]["message"]["content"])
