# Provider Evaluation Lab v0.1

A small Python-based harness for evaluating and comparing LLM inference providers using a standardized methodology.

The goal is to understand inference providers as products rather than treating them as interchangeable APIs. The lab will compare the performance, economics, reliability, and capabilities of the same or similar models across multiple providers.

## v0.1 Goals

v0.1 will support at least two real inference providers and measure:

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

Both streaming and non-streaming requests will be tested.

The harness should make it possible to send comparable requests to different providers and save the resulting measurements in a consistent format.

## Provider Qualification

In addition to measurements collected automatically by the harness, provider/model endpoints will be manually evaluated for attributes such as:

- Authentication
- Rate limits
- Context limits
- Structured output support
- Tool calling support
- Caching / batching support where relevant
- Privacy / data retention policies
- Documentation quality

## Project Structure

```text
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
│   ├── provider_a.py
│   └── provider_b.py
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