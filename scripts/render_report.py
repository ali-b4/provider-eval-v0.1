"""Rebuild a side-by-side HTML report from a saved run, without any API calls."""

import argparse
import html
import json
from pathlib import Path

PROVIDERS = ("venice", "chutes", "darkbloom")


def render_report(directory: Path) -> Path:
    columns = []
    for provider in PROVIDERS:
        path = directory / f"{provider}.json"
        if path.exists():
            result = json.loads(path.read_text(encoding="utf-8"))
            success = result["success"]
            state = "Success" if success else "Failed"
            response = result.get("response") or {}
            status = response.get("status_code", "No HTTP response")
            summary = html.escape(f"{state} · {status} · {result['total_latency_seconds']}s")
            model = html.escape(result["provider_model_id"])
            body = f'<p class="{"ok" if success else "failed"}">{summary}</p><p class="model">{model}</p>'
            if result.get("error"):
                body += '<h2>Error</h2><pre>' + html.escape(json.dumps(result["error"], indent=2)) + '</pre>'
            body += '<h2>Response JSON</h2><pre>' + html.escape(json.dumps(result["response"], indent=2, ensure_ascii=False)) + '</pre>'
            body += '<details><summary>Request JSON</summary><pre>' + html.escape(json.dumps(result["request"], indent=2, ensure_ascii=False)) + '</pre></details>'
        else:
            body = '<p class="model">Not selected for this run</p>'
        columns.append(f'<section><h1>{provider.title()}</h1>{body}</section>')
    page = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Provider request comparison</title><style>
*{box-sizing:border-box}body{margin:0;background:#f4f6f8;color:#182434;font:15px system-ui,sans-serif}
header{padding:20px 24px;border-bottom:1px solid #dbe1e8}header strong{font-size:22px}header p{margin-bottom:0;color:#536275}
main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;padding:18px;min-width:900px}
section{background:white;border:1px solid #dbe1e8;border-radius:10px;padding:18px;min-width:0}
h1{font-size:21px;margin:0}h2,summary{font-size:14px;font-weight:600}summary{cursor:pointer;padding:12px 0}
pre{font:12px/1.6 ui-monospace,monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fa;border-radius:6px;padding:12px;max-height:65vh;overflow:auto}
.model{color:#536275;overflow-wrap:anywhere;font-size:12px}.ok{color:#087345}.failed{color:#b42318}
</style></head><body><header><strong>Provider request comparison</strong>
<p>RUN_ID · Non-streaming · Elapsed time includes the full request. Expand Request JSON to inspect the input.</p>
</header><main>COLUMNS</main></body></html>'''
    page = page.replace("RUN_ID", html.escape(directory.name)).replace("COLUMNS", "".join(columns))
    output = directory / "report.html"
    output.write_text(page, encoding="utf-8")
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    if not any((args.run_directory / f"{name}.json").exists() for name in PROVIDERS):
        parser.error("Directory contains no saved provider results")
    print(render_report(args.run_directory))
