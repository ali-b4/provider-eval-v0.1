"""Send the same prompt concurrently to selected providers and save an HTML log."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
import uuid
import webbrowser

from render_report import render_report

ROOT = Path(__file__).resolve().parents[1]
MODEL = "qwen/qwen3.8-27b"
PROVIDERS = {
    "venice": ("https://api.venice.ai/api/v1/chat/completions", "qwen-3-8-27b"),
    "chutes": ("https://llm.chutes.ai/v1/chat/completions", "Qwen/Qwen3.8-27B-TEE"),
    "darkbloom": ("https://api.darkbloom.dev/v1/chat/completions", "EigenLabs/Qwen3.8-27B-4bit-mtp"),
}


def load_dotenv() -> None:
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip()
            if value[:1] in {"'", '"'} and value[-1:] == value[:1]:
                value = value[1:-1]
            os.environ.setdefault(key.strip(), value)


def probe(provider: str, prompt: str, timeout: float) -> dict:
    url, default_model = PROVIDERS[provider]
    model = os.getenv(f"{provider.upper()}_MODEL", default_model)
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}],
               "temperature": 0, "stream": False}
    result = {
        "provider": provider, "model": MODEL, "provider_model_id": model,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request": {"url": url, "headers": {"Authorization": "Bearer <redacted>",
                    "Content-Type": "application/json"}, "json": payload},
        "response": None, "success": False, "error": None,
    }
    start = time.perf_counter()
    try:
        key = os.getenv(f"{provider.upper()}_API_KEY")
        if not key:
            raise ValueError(f"Missing {provider.upper()}_API_KEY")
        request = urllib.request.Request(url, data=json.dumps(payload).encode(),
                    headers={"Authorization": f"Bearer {key}",
                             "Content-Type": "application/json"}, method="POST")
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            body_text = response.read().decode("utf-8", errors="replace")
            result["response"] = {"status_code": response.code,
                                  "headers": dict(response.headers), "body": body_text}
            try:
                result["response"]["body"] = json.loads(body_text)
            except json.JSONDecodeError:
                result["error"] = {"type": "InvalidJSON", "message": "Response was not valid JSON; raw text retained."}
            result["success"] = 200 <= response.code < 300 and result["error"] is None
            if not 200 <= response.code < 300:
                result["error"] = {"type": "HTTPError", "message": f"HTTP {response.code}"}
    except Exception as error:
        result["error"] = {"type": type(error).__name__, "message": str(error)}
    result["total_latency_seconds"] = round(time.perf_counter() - start, 3)
    return result


def run(providers: list[str], prompt: str, timeout: float, output: Path) -> list[dict]:
    output.mkdir(parents=True, exist_ok=False)
    results = []
    with ThreadPoolExecutor(max_workers=len(providers)) as pool:
        futures = [pool.submit(probe, provider, prompt, timeout) for provider in providers]
        for future in as_completed(futures):
            result = future.result()
            (output / f"{result['provider']}.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            results.append(result)
            status = "OK" if result["success"] else "FAILED"
            print(f"{result['provider']}: {status} ({result['total_latency_seconds']}s)")
    render_report(output)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--providers", nargs="+", choices=PROVIDERS, default=list(PROVIDERS))
    parser.add_argument("--prompt", default="Reply with exactly: hello")
    parser.add_argument("--timeout", type=float, default=180, help="Network timeout in seconds (default: 180)")
    parser.add_argument("--open", action="store_true", help="Open the completed HTML report in your browser")
    args = parser.parse_args()
    if not 0 < args.timeout < float("inf"):
        parser.error("--timeout must be a positive finite number")
    load_dotenv()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]
    output = ROOT / "results" / "raw" / run_id
    results = run(list(dict.fromkeys(args.providers)), args.prompt, args.timeout, output)
    report = output / "report.html"
    print(f"Report: {report}")
    if args.open:
        webbrowser.open(report.as_uri())
    raise SystemExit(0 if all(result["success"] for result in results) else 1)


if __name__ == "__main__":
    main()
