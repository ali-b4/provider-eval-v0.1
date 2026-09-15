"""Small, direct, non-streaming Venice probe."""

import json
import os
from pathlib import Path
import urllib.error
import urllib.request


URL = "https://api.venice.ai/api/v1/chat/completions"


def load_dotenv() -> None:
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
MODEL = os.getenv("VENICE_MODEL", "qwen-3-8-27b")
API_KEY = os.environ["VENICE_API_KEY"]
payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": "Reply with exactly: hello from Venice"}],
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

try:
    with urllib.request.urlopen(request) as response:
        raw_response = {
            "status_code": response.status,
            "headers": dict(response.headers),
            "body": json.loads(response.read().decode()),
        }
except urllib.error.HTTPError as error:
    raw_response = {
        "status_code": error.code,
        "headers": dict(error.headers),
        "body": json.loads(error.read().decode()),
    }

print("RAW REQUEST")
print(json.dumps({"url": URL, "headers": {"Authorization": "Bearer <redacted>", "Content-Type": "application/json"}, "json": payload}, indent=2))
print("\nRAW RESPONSE")
print(json.dumps(raw_response, indent=2))
if 200 <= raw_response["status_code"] < 300:
    print("\nPARSED RESULT")
    print(raw_response["body"]["choices"][0]["message"]["content"])
else:
    raise SystemExit(1)
