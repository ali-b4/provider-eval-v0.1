# Provider Evaluation Lab v0.1

A small Python-based harness for evaluating and comparing LLM inference providers using a standardized methodology.

The benchmark uses one fixed model:

**`qwen/qwen3.8-27b`**

across four inference providers:

- Venice
- Chutes
- Darkbloom
- io.net

Each provider will be accessed through its **direct API**. The lab will not route requests through an aggregator such as OpenRouter.

The goal is to understand how different providers deliver the same underlying model and compare them as inference products rather than treating all model endpoints as interchangeable APIs.

---

## Run and inspect requests

The model stays the same, using the existing provider-specific IDs in `.env`.
There is no model-selection command-line option or automatic model fallback.

Run from the project folder with Python 3.10 or newer. No third-party packages are required.
Copy `.env.example` to `.env` if needed and fill in the four API keys.

```bash
# Default: call all four providers concurrently and open the HTML report
python3 scripts/manual_request.py --open

# Stream all four providers and measure first-token time
python3 scripts/manual_request.py --stream --open

# Call only the selected providers, concurrently
python3 scripts/manual_request.py --providers venice chutes --open

# Call just one provider with a custom prompt
python3 scripts/manual_request.py --providers darkbloom --prompt "Explain inference in one sentence." --open
```

Every selected provider receives the same prompt with temperature 0, streaming off by default (`--stream` enables it),
and no artificial `max_tokens` limit. Calls overlap; their exact start times may differ slightly.
Omitting `--providers` selects all four, even if a key is missing. Missing keys and
request failures appear in the report without stopping the other providers.

Each run saves its own folder under `results/raw/<run-id>/`, containing:

- One JSON log per selected provider: request, response body, response headers, HTTP status, elapsed time, and any error.
- `report.html`: four equal columns for Venice, Chutes, Darkbloom, and io.net. Unselected providers are labeled “Not selected.” Each response scrolls independently; expand “Request JSON” to inspect the input.

The report opens after all calls finish. Omit `--open` to save it without opening a browser.
The terminal prints only short status lines and the report path. Authorization keys are
redacted from request logs; prompts and provider responses are retained locally.
`--timeout 180` sets the network timeout in seconds (the default).
A run exits with a nonzero status if any selected provider fails, while still saving its report.

To recreate an HTML report from saved JSON without making new API calls:

```bash
python3 scripts/render_report.py results/raw/<run-id>
```

Both modes save normalized metrics and a separate Metrics dropdown in each column.
Streaming logs include timed SSE events and assembled answer/reasoning output.
`run_benchmark.py` remains a placeholder for a future multi-workload runner.
The older provider-specific probe scripts remain available for individual debugging.

---

## v0.1 Goals

v0.1 will send standardized requests to Venice, Chutes, Darkbloom, and io.net and measure:

- Time to first token (TTFT)
- Total latency
- Output throughput / tokens per second
- Input tokens
- Output tokens
- Input price per 1M tokens
- Output price per 1M tokens
- Estimated request cost
- HTTP / API errors
- Provider and model metadata

Both streaming and non-streaming requests will be tested where supported.

The objective is to make the same workload runnable against all four providers and store the resulting measurements in a consistent format.

---

## Benchmark Model

The fixed benchmark model is:

`qwen/qwen3.8-27b`

This model will be held constant across providers so that the primary variable being compared is the inference provider rather than model quality.

Provider-specific model IDs may differ from the canonical model name and will be recorded in provider metadata where necessary.

---

## Providers

### Venice

Requests will be sent directly to the Venice API.

### Chutes

Requests will be sent directly to the Chutes API.

### Darkbloom

Requests will be sent directly to the Darkbloom API.

### io.net

Requests are sent directly to the io.net IO Intelligence API using `IONET_API_KEY`
and `Qwen/Qwen3.8-27B`. Select it individually with `--providers ionet`.

No requests in the initial benchmark should be routed through OpenRouter or another inference aggregator.

## Provider Documentation and Source of Truth

Use the provider's own documentation as the source of truth whenever a direct request fails or a model name is uncertain. Do not assume that the canonical benchmark name maps directly to the provider's API `model` value; provider-specific aliases, catalog IDs, build IDs, permissions, and error formats may differ.

- [Venice API documentation](https://docs.venice.ai/overview/about-venice) — endpoint, authentication, model IDs, request fields, and response behavior.
- [Chutes API reference](https://chutes.ai/docs/api-reference/overview) — API endpoints, authentication, model-specific guides, and OpenAI-compatible inference requests.
- [Darkbloom documentation](https://github.com/Layr-Labs/d-inference/tree/master/docs) — consumer quickstart, model catalog, API contracts, authentication, error codes, and allowed-model behavior.

- [io.net API documentation](https://io.net/docs/reference/ai-models/create-chat-completion) — direct chat endpoint, streaming, and authentication; [model catalog](https://io.net/docs/reference/ai-models/get-models-list).

For naming checks, use the provider's documented model ID or model-list endpoint. For errors, first compare the HTTP status, error code, and request field named in the provider response against that provider's documentation before changing the request or adapter.

---

## Provider Qualification

In addition to measurements collected automatically by the harness, each provider/model endpoint will be manually evaluated for attributes such as:

- Authentication method
- API compatibility
- Rate limits
- Context limits
- Structured output support
- Tool calling support
- Streaming support
- Caching / batching support where relevant
- Privacy / data retention policies
- Documentation quality
- Provider-specific limitations or behavior

This allows the lab to compare providers on more than raw speed and price.

---

## Project Structure

    provider-eval-v0.1/
    │
    ├── config/
    │   └── pricing.json
    │
    ├── notes/
    │   └── metrics.md
    │
    ├── providers/
    │   ├── base.py
    │   ├── venice.py
    │   ├── chutes.py
    │   ├── darkbloom.py
    │   └── ionet.py
    │
    ├── results/
    │   ├── raw/
    │   └── summary/
    │
    ├── scripts/
    │   ├── manual_request.py
    │   ├── render_report.py
    │   └── run_benchmark.py
    │
    ├── tests/
    │   └── basic_chat.json
    │
    ├── .env.example
    ├── README.md
    └── requirements.txt

---

## Directory Purpose

### `config/`

Configuration that should remain separate from benchmark logic.

`pricing.json` will contain provider/model pricing information used to calculate request costs.

---

### `notes/`

Human-readable project notes and definitions.

`metrics.md` defines the terminology and metrics used throughout the benchmark.

---

### `providers/`

Provider-specific API implementations.

`base.py` will define the common interface expected from every provider.

The provider modules:

- `venice.py`
- `chutes.py`
- `darkbloom.py`
- `ionet.py`

will translate the common request format into each provider's API format and normalize the resulting responses.

The benchmark itself should not need to know the implementation details of each provider.

---

### `results/`

Benchmark outputs.

`raw/` will contain individual request-level observations.

`summary/` will contain processed comparison results.

---

### `scripts/`

Executable project workflows.

`manual_request.py` sends concurrent direct API requests and saves JSON logs and a four-column HTML report. `render_report.py` rebuilds the report from saved logs.

`run_benchmark.py` will run standardized tests across all configured providers.

---

### `tests/`

Standardized workloads sent to each provider.

`basic_chat.json` will contain the initial prompts used for provider comparison.

The same test inputs should be used across providers wherever possible.

---

## Standardized Request

The harness should eventually allow a benchmark request to be described using a common set of parameters such as:

    providers (all four by default; explicit selections restrict the run)
    messages
    max_tokens
    temperature
    streaming

The provider adapter will then convert this standardized request into the format expected by the selected provider.

Conceptually:

    standardized request
            ↓
      provider adapter
            ↓
       provider API

---

## Request Flow

    test prompt
        ↓
    standardized request
        ↓
    provider adapter
        ↓
    direct provider API
        ↓
    response / token stream
        ↓
    measurement
        ↓
    normalized result
        ↓
    results/raw

The same test should be runnable against Venice, Chutes, Darkbloom, and io.net without changing the benchmark logic.

---

## Measurement Model

A benchmark result should eventually contain fields similar to:

    provider
    model
    provider_model_id
    timestamp
    streaming

    input_tokens
    output_tokens

    ttft
    total_latency
    output_tokens_per_second

    input_price_per_1m
    output_price_per_1m

    input_cost
    output_cost
    request_cost

    success
    http_status
    error_type
    error_message

Provider/model metadata may be maintained separately, but every response record must include or reference the endpoint metadata used for that request.

---

## Performance Metrics

### Time to First Token — TTFT

Time between sending the request and receiving the first generated token or streaming chunk.

    TTFT = first_token_time - request_start_time

This measures how quickly the provider begins responding.

---

### Total Latency

Time between sending the request and receiving the complete response.

    total_latency = response_complete_time - request_start_time

---

### Output Throughput

The rate at which output tokens are generated after generation begins.

Approximately:

    output_throughput =
        output_tokens / generation_time

where:

    generation_time =
        final_token_time - first_token_time

Output throughput is measured in tokens per second.

TTFT and output throughput are tracked separately because a provider can begin generating quickly but generate slowly, or begin slowly but generate the remaining output quickly.

---

## Token Accounting

For each request, the harness should record:

### Input Tokens

Tokens sent to the model, including relevant prompt text, instructions, and conversation history.

### Output Tokens

Tokens generated by the model in response to the request.

Where possible, provider-reported usage data will be used.

Differences in token reporting between providers should be recorded rather than silently ignored.

---

## Cost Calculation

For providers that price inference by token usage:

    input_cost =
        input_tokens
        × input_price_per_1m
        / 1,000,000

    output_cost =
        output_tokens
        × output_price_per_1m
        / 1,000,000

    request_cost =
        input_cost + output_cost

Pricing data should live in configuration or provider metadata rather than inside benchmark measurement logic.

---

## Error Capture

Failed requests are part of provider evaluation and should be recorded rather than discarded.

The harness should eventually capture fields such as:

    provider
    model
    timestamp
    http_status
    error_type
    error_message
    request_parameters

Potential failures include:

- Authentication failures
- Invalid model IDs
- Invalid parameters
- Rate limits
- Context-limit violations
- Provider overload
- Server errors
- Timeouts
- Malformed requests

A failed request should produce a result record rather than crashing the entire benchmark run.

---

## Raw Results

Each benchmark request should produce a structured result.

Raw observations will be written to:

`results/raw/`

The initial implementation may use JSONL or another simple structured format.

Raw results should remain available so later analysis can be reproduced without rerunning the provider calls.

---

## Summary Results

Processed comparisons will be written to:

`results/summary/`

An initial comparison should eventually make it possible to view results approximately like:

| Provider | Model | Mode | Input Tokens | Output Tokens | TTFT | Total Latency | Tok/s | Cost | Success |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| Venice | qwen/qwen3.8-27b | Streaming | | | | | | | |
| Chutes | qwen/qwen3.8-27b | Streaming | | | | | | | |
| Darkbloom | qwen/qwen3.8-27b | Streaming | | | | | | | |
| io.net | qwen/qwen3.8-27b | Streaming | | | | | | | |

v0.1 should not attempt to draw strong statistical conclusions from a small number of requests.

The immediate purpose is to build the measurement system and understand how the providers behave.

---

## Current Scope

v0.1 is focused on learning how to:

1. Call multiple inference providers directly
2. Understand their API request and response formats
3. Normalize requests across providers
4. Normalize provider responses
5. Measure inference performance
6. Understand streaming behavior
7. Track token usage
8. Calculate inference costs
9. Capture API failures
10. Compare provider capabilities and limitations

The benchmark intentionally holds the model constant so that differences in provider behavior are easier to observe.

---

## Out of Scope for v0.1

The following are intentionally deferred:

- Large-scale benchmarking
- High-concurrency load testing
- p50 / p95 statistics
- Sophisticated statistical analysis
- Automated provider ranking
- Multi-provider routing
- Failover
- Self-hosted inference
- Interactive dashboards (the local HTML request log is in scope)
- Production infrastructure
- Customer-facing APIs
- OpenRouter or other aggregator benchmarking

These can be added after the basic provider qualification workflow is working correctly.

---

## v0.1 Completion Criteria

v0.1 is complete when the project can:

1. Send the same standardized workload directly to Venice, Chutes, Darkbloom, and io.net
2. Run both streaming and non-streaming requests where supported
3. Record TTFT
4. Record total latency
5. Record output throughput
6. Record input and output token usage
7. Calculate estimated request cost
8. Capture provider errors without stopping the benchmark
9. Store provider/model metadata
10. Save normalized request-level results
11. Produce a simple comparison of the four providers

At that point the lab should provide a functional foundation for more rigorous provider qualification in later versions.

---

## Status

**v0.1 — in development**

Current progress:

- All three providers returned HTTP 200 in the concurrent verification run; see [comparison notes](notes/direct-request-comparison.md) and the [saved HTML report](results/raw/20260915T124502Z-11785503/report.html)
- Concurrent direct request runner added; all four providers now run by default, with optional subsets
- Per-provider JSON logs and a three-column HTML report added
- Offline tests cover concurrent selection, failures, missing keys, timeouts, and HTML escaping
- Repository initialized
- Project structure created
- Initial metric definitions created
- Benchmark model selected: `qwen/qwen3.8-27b`
- Direct non-streaming probe scripts created for Venice, Chutes, and Darkbloom
- `.env` loading added to the probe scripts; `.env` is excluded from Git
- No artificial `max_tokens` limit is included in the direct probe requests
- Provider documentation links added as the source of truth for model names and errors
- Provider-specific Qwen3.8 model IDs configured:
  - Venice: `qwen-3-8-27b`
  - Chutes: `Qwen/Qwen3.8-27B-TEE`
  - Darkbloom: `EigenLabs/Qwen3.8-27B-4bit-mtp`
- Venice direct request successfully returned HTTP 200 and parsed response text
- Darkbloom model-permission behavior identified: the API key only permits its explicitly selected model ID
- Raw response shape and lifecycle notes documented for the initial Chutes investigation

Benchmark model:

`qwen/qwen3.8-27b`

Providers:

- Venice
- Chutes
- Darkbloom

### Completed: direct request inspection

- Confirmed successful direct responses from all three providers using the existing model IDs, including Darkbloom's approved model.
- Ran all three providers concurrently and retained their raw JSON responses and HTML comparison report.
- Compared request and response shapes, usage fields, reasoning fields, status codes, and provider metadata.
- Recorded provider-specific findings and remaining measurement questions in [comparison notes](notes/direct-request-comparison.md).

### Completed: measurements and streaming

Implemented and verified on 2026-09-15 with six successful live requests and 10 offline tests.
Reports: [non-streaming](results/raw/20260915T125720Z-8cf4bdc4/report.html) ·
[streaming](results/raw/20260915T125723Z-b21f2938/report.html).

The following checklist describes the implemented workflow. Keep the model fixed and continue
calling all four providers concurrently by default; an explicit provider selection
runs only those providers concurrently.

1. **Implement non-streaming measurements.** Extend the existing request logs into consistent metric records for every provider response, including failures.
2. **Implement streamed responses.** Capture the response stream and final assembled output, measure time to first token and generation throughput, and retain usage and error information.
3. **Record every metric defined in [notes/metrics.md](notes/metrics.md) for every test response**, in both streaming and non-streaming modes:
   - Time to first token (TTFT).
   - Total latency.
   - Output throughput / tokens per second, measured per request.
   - Input tokens.
   - Output tokens, including reasoning tokens as well as the final answer.
   - Input price per 1M tokens.
   - Output price per 1M tokens.
   - Total request cost.
   - HTTP/API errors, including status and error details, with an explicit success/failure outcome.
   - Provider/model metadata, including provider name, model ID, pricing, rate limits, region, version, and context window where available.
4. **Add a separate, clean “Metrics” dropdown to each provider column in every run's `report.html`.** Display the metrics above with readable labels and units, separate from the raw request and response JSON. Keep all four columns aligned for comparison and save the same metrics in the underlying JSON records.
5. **Verify measurement consistency across providers.** Resolve differences in input-token reporting and reasoning-token accounting, and use documented provider pricing for cost calculations.

Every response record must contain the full metric set. When a metric cannot be
measured or supplied, record it as unavailable (`null`) with a reason rather than
omitting it or reporting zero. For example, non-streaming responses do not expose
true TTFT or the generation interval needed for output throughput; failures may
also leave usage and costs unknown. Clearly distinguish measured, provider-reported,
and estimated values.


### Remaining qualification work

- Explain the remaining input-count difference (Venice 94 versus 57) and independently verify Venice/Chutes reasoning accounting; preserve reported totals meanwhile.
- Refresh dated prices before future comparisons; estimates use standard published rates, not account billing receipts.
- Investigate unavailable endpoint metadata such as serving region and Darkbloom context window.
- Build the multi-workload `run_benchmark.py` workflow after this measurement foundation.

New Venice requests disable its default system prompt to reduce hidden input differences.
See [measurement definitions and limits](notes/metrics.md) for timing, pricing, and accounting rules.


### Added: io.net — 2026-09-15

- All four providers now run concurrently by default, with four equal report columns and the same metric fields.
- io.net uses `IONET_API_KEY` and the verified `Qwen/Qwen3.8-27B` model ID. Optional `IONET_MODEL` follows the same configuration convention as the other providers.
- Prompt, temperature, token-limit policy, streaming options, and measurement formulas are unchanged.
- io.net pricing and endpoint metadata are recorded in `config/pricing.json` and its saved catalog snapshot.
- All eight live requests succeeded: [non-streaming report](results/raw/20260915T133047Z-327d32ba/report.html) and [streaming report](results/raw/20260915T133050Z-cc5f32d4/report.html).
- All 12 offline tests pass, including four-provider concurrency, io.net request settings, usage/cost accounting, key redaction, and report columns.

```bash
# Same experiment, now all four providers
python3 scripts/manual_request.py --open
python3 scripts/manual_request.py --stream --open

# Select only io.net
python3 scripts/manual_request.py --providers ionet --stream --open
```

Earlier saved reports and dated three-provider observations retain their original results.
The `providers/` adapter classes and `run_benchmark.py` remain future-work placeholders;
the working workflow for all four providers is `manual_request.py`.
