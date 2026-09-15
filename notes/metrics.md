# Measurement definitions

Each JSON metric contains `value`, `unit`, `source`, and `reason`. Unknown values
are `null` with an explanation. Sources distinguish measured, provider-reported,
configured, and estimated values.

- **TTFT:** seconds from starting the HTTP call to the first nonempty answer or reasoning chunk. Role-only events and usage events do not count. Unavailable without streaming.
- **Total latency:** seconds from starting the HTTP call until completion or failure, including network time. Missing credentials leave this unavailable because no request was sent.
- **Output throughput:** provider-reported completion tokens divided by the first-to-last generated-content chunk interval. This is a per-request estimate: chunks may contain multiple tokens and buffering can inflate speed, particularly for short answers. Unavailable without streaming, final usage, a positive interval, or successful completion.
- **Input tokens:** provider-reported `usage.prompt_tokens`; preserve differences between providers.
- **Output tokens:** provider-reported `usage.completion_tokens`, including reasoning under the compatible API convention. Never add `reasoning_tokens` again. Darkbloom explicitly reports that subset; Venice and Chutes did not provide a separate reasoning count in verification. We have not independently tokenized their hidden reasoning.
- **Prices:** USD per million tokens, tied to the exact configured model ID and dated provider sources in `config/pricing.json`. Output prices need not always exceed input prices.
- **Request cost:** estimated input plus output cost using published rates, including Chutes' reported cached-input discount and Darkbloom's documented standard-consumer minimum of $0.0001. Account-specific rates can differ. This is not a billing receipt. Missing usage/pricing produces null, never a free-call assumption.
- **HTTP/API errors:** explicit success/failure, HTTP status, and error details. Partial streams and raw events survive interruption. A stream must reach `[DONE]`; HTTP 200 alone does not establish success.
- **Metadata:** provider/model IDs, pricing snapshot, rate-limit headers, region, version/fingerprint, context window, and quantization where supplied. Unavailable fields have reasons. A fingerprint identifies a serving configuration, not necessarily a software version.

## Comparison limits

Venice's [documented default system prompt](https://docs.venice.ai/api-reference/api-spec)
is disabled in new requests. On 2026-09-15 this reduced its input count from the
previous 1,650 to 94; Chutes and Darkbloom reported 57. The remaining difference
may involve templates or provider preprocessing; its cause is not established.
Counts are retained rather than artificially equalized.

The fixed model family does not imply identical serving builds: catalogs list
FP8 for Venice and Chutes, while the approved Darkbloom ID specifies 4bit/MTP.
Reasoning defaults can also differ. These runs do not isolate hardware performance.

Pricing sources, retrieved 2026-09-15:

- [Venice model catalog](https://api.venice.ai/api/v1/models): $0.45 input / $3.20 output.
- [Chutes model catalog](https://llm.chutes.ai/v1/models): $0.32 input / $2.50 output; cached input $0.032.
- [Darkbloom pricing](https://api.darkbloom.dev/v1/pricing): $0.15 input / $2.00 output. [Billing units and minimum](https://github.com/Layr-Labs/d-inference/blob/master/docs/reference/pricing-model.md).

Selected source records are retained in `config/provider-catalogs/`. Refresh the
configuration when provider prices change; each new result embeds its price snapshot.


## io.net addition — 2026-09-15

io.net uses the same prompt, temperature, token-limit policy, streaming options,
metric calculations, and error handling as the existing experiment. Its direct
[model catalog](https://api.intelligence.io.solutions/api/v1/models) lists
`Qwen/Qwen3.8-27B` in FP8 with a 65,536-token context window. Prices converted
from the catalog's per-token USD fields are $0.308 input / $2.73 output per
million tokens, with cached input at $0.154. The selected catalog record is saved
in `config/provider-catalogs/ionet.json`. These are published-rate estimates.
