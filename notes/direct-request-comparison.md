# Direct request comparison — 2026-09-15

Saved run: [HTML comparison](../results/raw/20260915T124502Z-11785503/report.html).
The three calls ran concurrently with the same prompt, `Reply with exactly: hello`,
temperature 0, streaming off, and no `max_tokens` setting. Existing model settings were preserved.

| Provider | HTTP status | Total seconds | Input tokens | Output tokens |
|---|---:|---:|---:|---:|
| Venice | 200 | 0.812 | 1,650 | 29 |
| Chutes | 200 | 1.947 | 57 | 32 |
| Darkbloom | 200 | 2.203 | 57 | 38 |

These are observations from one short request per provider, not performance rankings.
All returned `hello` with two leading newlines in `choices[0].message.content`.

## Response differences observed

- All three use `choices` for the answer and `usage.prompt_tokens`, `usage.completion_tokens`, and `usage.total_tokens` for token counts.
- Venice reported substantially more input tokens for the same submitted message. The cause is not established by this run. Its response includes `venice_parameters` and `cost` fields.
- Venice exposes `reasoning_content` on the message; Chutes exposes `reasoning`; Darkbloom exposes `reasoning`, `reasoning_content`, and `reasoning_details`.
- Darkbloom reports 34 reasoning tokens inside its 38 completion tokens and includes `se_signature` and `response_hash` metadata.
- Chutes includes prompt cache token details, a system fingerprint, and additional serving metadata. Fields are preserved as returned, including null values.
- The configured Darkbloom model ID succeeded with the existing API key.

## Measurement limits and next work

This runner records total request time only. Non-streaming calls do not establish time to first token or generation throughput.
Before normalizing costs and output speed, investigate Venice's input-token difference and how each provider includes reasoning in usage.
Then implement the common provider adapters and streaming benchmark measurements described in the README.

The earlier run `20260915T124452Z-026ed7ed` captured local network-resolution failures
inside the restricted environment. Those are not evidence of provider outages;
the network-enabled run above succeeded for all three providers.

## Measurement implementation — 2026-09-15

Streaming and non-streaming metrics are now implemented. All six verification requests succeeded. See the README for the saved reports and [metric definitions](metrics.md) for pricing, reasoning accounting, and the remaining input-count difference. The earlier measurement limits above describe the original inspection run.
