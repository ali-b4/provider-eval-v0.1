# Codebase cleanup — 2026-09-15

## Completed

- Consolidated the three legacy debugging commands behind `scripts/raw_request.py`, reusing the working runner's request, credential, and error handling. Their filenames, prompts, and console sections remain available. Importing them no longer sends requests.
- Debug requests now share the runner's provider settings and 180-second network timeout. In particular, the Venice debug command now disables its default system prompt, matching the comparison runner.
- Removed the empty `requirements.txt`; the project uses Python's standard library.
- Removed tracked Finder metadata and ignored `.DS_Store` and local `.venv/` directories.

The README, environment configuration, active runner, failure validation, measurement code, streaming code, and report renderer were left untouched for the other agent. Saved results and catalogs were preserved.

## Handoff: issues in files owned by the other agent

These findings were reproduced offline with synthetic responses. Recheck them after the other agent's changes before implementing fixes.

| Priority | Location | Finding and suggested fix |
|---|---|---|
| High | `scripts/measurements.py` → `normalize` | Non-object usage/details or string cached-token counts raise exceptions. Normalization runs outside the request error handler, so one malformed response can stop the comparison. Validate field types, retain the raw response, and mark unusable counts unavailable. Reject boolean and negative token counts too. |
| High | `scripts/manual_request.py` → `probe` | HTTP 200 bodies such as `null`, `[]`, or `{}` count as successful completions. Validate the response structure before counting success. |
| Medium | `scripts/validate_failures.py` → `assess` | An HTTP 503 error containing “upstream timed out” passes the local-timeout check. Distinguish local timeout exceptions from provider HTTP/API errors. |
| Medium | `scripts/manual_request.py` → `probe` | A model environment override changes `provider_model_id` but retains the fixed Qwen family label. Validate overrides or ensure future comparisons group by the actual requested model. |

For dashboard history, also preserve saved pricing when normalizing an existing record: `normalize` currently rereads the current price file. The report already keeps existing metrics; this matters when future code recalculates them.

## Development direction

Use the saved normalized records as the boundary between collecting results and displaying them. Keep one shared request implementation for the debug commands, validation, and eventual workload runner.

The unused `providers/` classes, `scripts/run_benchmark.py`, and `tests/basic_chat.json` remain because the concurrent README roadmap references them. Replace or remove those placeholders together with the roadmap update; they are not used by today's request workflow.
