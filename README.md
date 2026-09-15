# Provider Evaluation Lab v0.1

A small Python-based harness for evaluating and comparing LLM inference providers using a standardized methodology.

The initial benchmark will evaluate the same model:

**`qwen/qwen3.8-27b`**

across three inference providers:

- Venice
- Chutes
- Darkbloom

Each provider will be accessed through its **direct API**. The lab will not route requests through an aggregator such as OpenRouter.

The goal is to understand how different providers deliver the same underlying model and compare them as inference products rather than treating all model endpoints as interchangeable APIs.

---

## v0.1 Goals

v0.1 will send standardized requests to Venice, Chutes, and Darkbloom and measure:

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

The objective is to make the same workload runnable against all three providers and store the resulting measurements in a consistent format.

---

## Benchmark Model

The initial benchmark model is:

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

No requests in the initial benchmark should be routed through OpenRouter or another inference aggregator.

## Provider Documentation and Source of Truth

Use the provider's own documentation as the source of truth whenever a direct request fails or a model name is uncertain. Do not assume that the canonical benchmark name maps directly to the provider's API `model` value; provider-specific aliases, catalog IDs, build IDs, permissions, and error formats may differ.

- [Venice API documentation](https://docs.venice.ai/overview/about-venice) — endpoint, authentication, model IDs, request fields, and response behavior.
- [Chutes API reference](https://chutes.ai/docs/api-reference/overview) — API endpoints, authentication, model-specific guides, and OpenAI-compatible inference requests.
- [Darkbloom documentation](https://github.com/Layr-Labs/d-inference/tree/master/docs) — consumer quickstart, model catalog, API contracts, authentication, error codes, and allowed-model behavior.

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
    │   └── darkbloom.py
    │
    ├── results/
    │   ├── raw/
    │   └── summary/
    │
    ├── scripts/
    │   ├── manual_request.py
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

`manual_request.py` will be used to make simple API calls, inspect raw responses, and debug provider behavior.

`run_benchmark.py` will run standardized tests across all configured providers.

---

### `tests/`

Standardized workloads sent to each provider.

`basic_chat.json` will contain the initial prompts used for provider comparison.

The same test inputs should be used across providers wherever possible.

---

## Standardized Request

The harness should eventually allow a benchmark request to be described using a common set of parameters such as:

    provider
    model
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

The same test should be runnable against Venice, Chutes, and Darkbloom without changing the benchmark logic.

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

Provider/model metadata will be stored separately from individual benchmark observations.

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
- Dashboards
- Production infrastructure
- Customer-facing APIs
- OpenRouter or other aggregator benchmarking

These can be added after the basic provider qualification workflow is working correctly.

---

## v0.1 Completion Criteria

v0.1 is complete when the project can:

1. Send the same standardized workload directly to Venice, Chutes, and Darkbloom
2. Run both streaming and non-streaming requests where supported
3. Record TTFT
4. Record total latency
5. Record output throughput
6. Record input and output token usage
7. Calculate estimated request cost
8. Capture provider errors without stopping the benchmark
9. Store provider/model metadata
10. Save normalized request-level results
11. Produce a simple comparison of the three providers

At that point the lab should provide a functional foundation for more rigorous provider qualification in later versions.

---

## Status

**v0.1 — in development**

Current progress:

- Repository initialized
- Project structure created
- Initial metric definitions created
- Benchmark model selected
- Providers selected

Benchmark model:

`qwen/qwen3.8-27b`

Providers:

- Venice
- Chutes
- Darkbloom

Next step:

Make a successful direct API request to each provider and inspect the raw request and response formats before building the standardized provider interface.
