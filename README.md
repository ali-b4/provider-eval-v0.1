# Provider Evaluation Lab v0.1

A small Python lab for comparing **Venice, Chutes, Darkbloom, and io.net** through
their direct APIs, using the fixed model family **`qwen/qwen3.8-27b`**.

The working runner sends the same prompt to all four providers concurrently and
compares response timing, token usage, estimated cost, errors, and endpoint metadata.
Adding io.net preserved the existing experiment settings and measurement formulas.
No requests are routed through OpenRouter or another aggregator.

## Run the experiment

Use Python 3.10 or newer from the project folder. No third-party packages are required.
If `.env` does not exist, copy `.env.example` to `.env` and fill in the API keys.
Keep an existing `.env`; it is excluded from Git.

| Provider | Command-line name | API key variable | Verified model ID |
|---|---|---|---|
| Venice | `venice` | `VENICE_API_KEY` | `qwen-3-8-27b` |
| Chutes | `chutes` | `CHUTES_API_KEY` | `Qwen/Qwen3.8-27B-TEE` |
| Darkbloom | `darkbloom` | `DARKBLOOM_API_KEY` | `EigenLabs/Qwen3.8-27B-4bit-mtp` |
| io.net | `ionet` | `IONET_API_KEY` | `Qwen/Qwen3.8-27B` |

Provider-specific `*_MODEL` environment variables override the defaults in
[scripts/provider_config.py](scripts/provider_config.py). Keep them set to the
verified IDs above for this experiment. Existing process environment variables
take precedence over `.env`. There is no model-selection command-line option or
automatic model fallback.

```bash
# All four providers, concurrently, non-streaming
python3 scripts/manual_request.py --open

# All four providers, concurrently, streaming
python3 scripts/manual_request.py --stream --open

# Only the selected providers, concurrently
python3 scripts/manual_request.py --providers venice ionet --stream --open

# Only io.net, with a custom prompt
python3 scripts/manual_request.py --providers ionet --prompt "Explain inference in one sentence." --open
```

### Experiment settings

- Default prompt: `Reply with exactly: hello`.
- Every selected provider receives the same user message and temperature `0`.
- No artificial `max_tokens` or `max_completion_tokens` limit is sent. Provider defaults still apply.
- Non-streaming is the default; `--stream` enables streaming and requests final usage data.
- All four providers are selected by default, including providers with missing keys.
- Explicit selections run only those providers. Calls overlap; start times may differ slightly.
- Venice's default system prompt is disabled with `include_venice_system_prompt: false`, as in the existing measurement experiment.
- io.net receives a client-identification header for gateway compatibility.
- `--timeout 180` sets the network timeout in seconds (the default); it is not an overall run deadline.

Missing keys and request failures produce records without stopping the other
providers. The command exits with a nonzero status if any selected provider fails.
The terminal prints status lines and the report path. `--open` opens the report
after all calls finish; omit it to save the report without opening a browser.

## Results and reports

Each run creates `results/raw/<run-id>/` containing:

- One JSON record per selected provider: request, response body and headers, HTTP status, timing, metrics, metadata, and error details.
- For streaming requests, timed server-sent events, raw stream lines, and assembled answer/reasoning text. Partial output is retained if the stream fails.
- `report.html`: four equal columns, each with a separate **Metrics** dropdown, response JSON, and expandable request JSON. Unselected providers are labeled “Not selected for this run.” Streaming results also offer assembled answer text.

Authorization keys are redacted from request logs. Prompts and provider responses
are retained locally. Each new record embeds the pricing configuration used for
its calculations.

Rebuild a report from saved records without making API calls:

```bash
python3 scripts/render_report.py results/raw/<run-id>
```

Earlier saved reports retain their original results. Rebuilding an older report
uses the current four-column layout, with io.net marked unselected if absent.

## Measurements

Every new response record, including failures, contains the same metric fields.
Each metric has a value, unit, source, and unavailable reason where applicable.
Sources distinguish measured, provider-reported, configured, and estimated values.
Unknown values are `null`, with an explanation, rather than omitted or assumed zero.

| Dimension | What the runner records |
|---|---|
| Time to first token (TTFT) | Time from starting the HTTP call to the first nonempty answer or reasoning chunk. Unavailable without streaming. |
| Total latency | Time from starting the HTTP call to completion or failure. Unavailable if no request was sent. |
| Output throughput | Completion tokens divided by the first-to-last generated-content chunk interval. Requires a successful stream, reported usage, and a positive interval. |
| Input tokens | Provider-reported `usage.prompt_tokens`. |
| Output tokens | Provider-reported `usage.completion_tokens`; separately reported reasoning tokens are treated as a subset and never added again. |
| Pricing | Input and output USD per million tokens for the exact configured model ID. |
| Estimated cost | Input cost, output cost, and total request cost, using the saved pricing configuration. |
| Errors | Explicit success/failure, HTTP status, error type, and error message. |
| Endpoint metadata | Provider and model IDs, returned model ID, pricing snapshot, rate-limit headers, region, version/fingerprint, context window, and quantization where available. |

### Timing and accounting limits

Streaming throughput is an estimate of observed delivery speed. Providers may send
multiple tokens in one chunk, and buffering can inflate apparent speed for short
answers. Non-streaming responses cannot establish true TTFT or generation throughput.
A stream must reach `[DONE]` to be considered complete.

The runner preserves provider-reported token totals. Darkbloom separately reported
reasoning-token counts in verification; Venice, Chutes, and io.net did not. Their
reasoning accounting has not been independently verified.

Disabling Venice's default system prompt reduced the observed input count from
1,650 to 94 in the measurement verification. The other providers reported 57 in
the four-provider run. The remaining difference is unresolved and is not
artificially corrected.

The model family is fixed, but serving builds and defaults differ. Saved catalogs
list FP8 for Venice, Chutes, and io.net; the approved Darkbloom ID specifies
4bit/MTP. These small runs are not provider rankings or isolated hardware benchmarks.

### Cost calculation

The base estimate is:

```text
input cost  = input tokens  × input price per million / 1,000,000
output cost = output tokens × output price per million / 1,000,000
request cost = input cost + output cost
```

The implementation applies configured cached-input discounts for Chutes and io.net
when cached-token usage is reported. It applies the configured standard-consumer
minimum of $0.0001 to Darkbloom's total. Account-specific rates may differ; these
estimates are not billing receipts. Missing usage or verified pricing leaves cost
unavailable.

[config/pricing.json](config/pricing.json) holds dated prices and source URLs,
verified on 2026-09-15. Selected source records are retained in
[config/provider-catalogs/](config/provider-catalogs/). Prices are not refreshed
automatically. See [notes/metrics.md](notes/metrics.md) for detailed definitions.

## Provider documentation and source of truth

Use each provider's own documentation and model catalog to investigate errors,
model IDs, permissions, and supported request fields.

- [Venice API documentation](https://docs.venice.ai/overview/about-venice)
- [Chutes API reference](https://chutes.ai/docs/api-reference/overview)
- [Darkbloom documentation](https://github.com/Layr-Labs/d-inference/tree/master/docs)
- [io.net documentation](https://io.net/docs/reference/ai-models/get-started-with-io-intelligence-api)

Compare the returned HTTP status, error code, and named request field against those
sources before changing requests. The canonical model name need not be the API
model ID, and Darkbloom keys may permit only an explicitly selected model.

## Codebase map

| Location | Current role |
|---|---|
| `scripts/manual_request.py` | Working concurrent direct-request runner and command-line entry point. |
| `scripts/validate_failures.py` | Separate live failure-validation suite and summary report. |
| `scripts/provider_config.py` | Shared fixed-model endpoints, provider IDs, and report labels. |
| `scripts/streaming.py` | Reads streaming events and assembles output while capturing arrival times. |
| `scripts/measurements.py` | Normalizes metrics, metadata, token usage, and estimated costs. |
| `scripts/render_report.py` | Builds the four-column HTML comparison. |
| `config/pricing.json` | Dated model-specific prices and metadata. |
| `config/provider-catalogs/` | Saved provider catalog/pricing records. |
| `notes/` | Metric definitions and earlier provider investigations. |
| `results/validation/` | Diagnostic observations and PASS/REVIEW summaries, excluded from normal comparisons. |
| `results/raw/` | Saved request-level JSON records and HTML reports. |
| `tests/test_*.py` | Offline checks for requests, concurrency, streaming, errors, metrics, and rendering. |
| `tests/basic_chat.json` | Initial workload definition listing all four providers; not yet consumed by the runner. |
| `providers/base.py` | Common interface for future provider adapters. |
| `providers/venice.py`, `chutes.py`, `darkbloom.py`, `ionet.py` | Adapter placeholders; the working runner does not use these classes. |
| `scripts/run_benchmark.py` | Placeholder for a future multi-workload benchmark runner. |
| `results/summary/` | Reserved for future processed summaries. Current comparisons are in each run's HTML report. |

Older provider-specific raw-request scripts remain available for debugging Venice,
Chutes, and Darkbloom. Use `manual_request.py --providers ionet` for io.net.

## Status and validation

**v0.1 — measurement workflow implemented; broader qualification in development.**

The io.net addition was verified on 2026-09-15 with one request per provider in
each mode: **all eight live requests succeeded**.

- [Four-provider non-streaming report](results/raw/20260915T133047Z-327d32ba/report.html)
- [Four-provider streaming report](results/raw/20260915T133050Z-cc5f32d4/report.html)
- [Earlier three-provider comparison notes](notes/direct-request-comparison.md)

All **12 offline tests** passed after the io.net addition. The failure-validation update expands the passing suite to **15 tests**. They cover provider selection
and concurrency, missing credentials, simulated HTTP/API errors and timeouts,
partial/malformed streams, timing boundaries, token/cost accounting, io.net request
settings, key redaction, and report rendering.

```bash
python3 -m unittest discover -s tests -v
```

Real failure validation is now also saved: [initial suite (39/40 checks)](results/validation/20260915T135818Z-26fc3e42/index.html)
and [targeted repeat (4/4)](results/validation/20260915T135854Z-adff9665/index.html).
The initial exception was a correctly captured Darkbloom 429 on a valid streaming
control; the repeat succeeded. All selected invalid-request cases were rejected
in both modes. See [failure-validation notes and review guide](notes/failure-validation.md).
These tests do not exhaust every possible provider error path.

### Review or repeat failure validation

No ongoing monitoring is needed. Open the saved summary above: PASS means the
expected behavior occurred; REVIEW calls for inspecting the linked details.
An intentionally failed request displays Failed inside its detailed provider report.

```bash
# Repeat all diagnostic cases in both modes (40 attempts)
python3 scripts/validate_failures.py --open

# Repeat only the mixed streaming check
python3 scripts/validate_failures.py --cases mixed --mode streaming --open
```

The diagnostic runner saves separate `results/validation/<run-id>/` folders with
`index.html`, `summary.json`, and per-case records/reports. Expected failures count
as passing checks. It exits nonzero for REVIEW results. Diagnostic settings never
modify `.env` or normal comparison defaults, and the records are marked for exclusion
from benchmark comparisons.

## Next steps

1. **Completed: initial real API failure validation.** Invalid credentials, nonexistent models, malformed temperature values, and local timeouts were tested against all four providers in both modes. Mixed runs confirmed other providers continue after a failure. A real Darkbloom rate-limit response was retained, followed by a successful repeat. Further error cases can be added as needed; see the [review guide](notes/failure-validation.md).
2. **Resolve remaining accounting questions.** Investigate Venice's input-count difference and independently verify reasoning-token accounting where no separate count is supplied.
3. **Complete endpoint qualification.** Document rate/context limits, structured output, tool calling, caching/batching, privacy/retention, documentation quality, and provider limitations. Fill unavailable metadata only when supported by evidence.
4. **Build the multi-workload workflow.** Implement `run_benchmark.py`, connect standardized workload files, and produce processed summaries after validating the measurement foundation.
5. **Refresh pricing before future comparisons.** Preserve dated sources and the configuration used in each run.

The initial failure-record deliverable is complete. The next investigation is
token/reasoning accounting; endpoint qualification and the multi-workload runner
remain unfinished.

## v0.1 scope and completion

The core measurement workflow can now call all four providers directly in both
modes, save consistent metrics and errors, retain endpoint metadata, estimate
costs, and produce a comparison. Unmeasurable values remain explicitly unavailable.
Broader completion includes the remaining validation and qualification work above.

Large-scale benchmarking, high-concurrency load testing, p50/p95 statistics,
automated rankings, routing/failover, self-hosting, interactive dashboards,
production infrastructure, customer-facing APIs, and aggregator comparisons remain
out of scope. The local HTML comparison report is in scope.
