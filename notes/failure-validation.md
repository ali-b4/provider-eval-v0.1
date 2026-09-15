# Real API failure validation — 2026-09-15

## Outcome

The first README next step is complete for the selected failure cases. All four
providers rejected invalid credentials, invalid model IDs, and a malformed
`temperature` value in both request modes. Deliberate 1 ms local timeouts were
also recorded in both modes.

The initial suite passed **39 of 40 checks**. One valid Darkbloom streaming
control returned a real **429 rate-limit error**, which was correctly saved while
Chutes and io.net continued successfully. After the stated retry interval, the
mixed streaming check passed **4 of 4 checks**. The original 429 remains saved.

- [Initial suite: 39/40](../results/validation/20260915T135818Z-26fc3e42/index.html)
- [Mixed streaming repeat: 4/4](../results/validation/20260915T135854Z-adff9665/index.html)

These are 44 diagnostic observations, not speed or reliability rankings. A failed
request is an expected result for the deliberately invalid cases.

## What happened

The HTTP statuses below were the same for streaming and non-streaming requests.

| Test | Venice | Chutes | Darkbloom | io.net |
|---|---|---|---|---|
| Invalid API key | 401 | 401 | 401 | 401 |
| Nonexistent model | 404 | 404 | 403, model not allowed by key | 400 |
| Text supplied instead of numeric temperature | 400 | 400 | 400 | 422 |
| Deliberate 1 ms local timeout | Timeout recorded | Timeout recorded | Timeout recorded | Timeout recorded |

Darkbloom checks model permissions for the key; its 403 is a permission rejection,
not proof that its nonexistent-model lookup returns 404. io.net's 422 identifies
`temperature` as invalid. Provider response bodies are retained in full.

The mixed tests deliberately give Venice an invalid key and make normal short
requests to the other three providers. All three controls completed in the
non-streaming test. In streaming, Darkbloom first returned an output-token rate
limit with a 1-second retry instruction, then succeeded on the targeted repeat.
This confirms a request failure does not stop the other providers in that group.
Earlier four-provider reports already contain successful Venice requests in both modes.

Provider references used to interpret the responses:

- [Venice API reference](https://docs.venice.ai/api-reference/api-spec)
- [Chutes API reference](https://chutes.ai/docs/api-reference/overview)
- [Darkbloom API contracts](https://github.com/Layr-Labs/d-inference/blob/master/docs/reference/api-contracts.md)
- [io.net chat reference](https://io.net/docs/reference/ai-models/create-chat-completion)

## How to review it

1. Open the initial suite report above. **PASS** means the observed behavior matched the test expectation; **REVIEW** means it needs investigation.
2. Click **Details** beside a row to see the four provider columns, raw error, HTTP status, and Metrics dropdown. Deliberately invalid requests should display **Failed** here; that is expected.
3. The sole initial REVIEW is the Darkbloom streaming control's 429. Open the repeat report to see its subsequent success.

No ongoing monitoring is required. These are completed, one-off tests. Nothing
runs in the background or retries automatically.

To repeat the full suite after changing error handling or provider configuration:

```bash
python3 scripts/validate_failures.py --open
```

This makes 40 diagnostic attempts using the configured keys, with short valid
control requests. It may incur small usage charges or encounter provider limits.
For a targeted check:

```bash
python3 scripts/validate_failures.py --cases mixed --mode streaming --open
python3 scripts/validate_failures.py --providers ionet --cases invalid_auth invalid_model invalid_parameter --open
```

Results go to a new `results/validation/<run-id>/` folder. `index.html` is the
summary, `summary.json` contains the check results, and each case folder contains
provider JSON records and a four-column `report.html`. The command returns a
nonzero exit status if any check needs REVIEW. Expected failures alone do not
make the command fail.

## Boundaries

- The ordinary comparison commands and fixed-model request settings are unchanged.
- Diagnostic overrides are per request; `.env` and configured defaults are not modified.
- Every saved diagnostic/control record is marked `exclude_from_benchmark` in its validation section and stored outside `results/raw/`.
- Automated checks verify expected status categories and the full metric/metadata structure; inspect details to establish the precise provider reason. The response bodies in this run were also reviewed.
- A 1 ms timeout usually interrupts connection setup. It tests local timeout capture, not a provider outage or a mid-generation stream interruption.
- These tests do not exhaust every real error path. Malformed streams and partial output remain covered by offline tests, not deliberately induced live failures.
- Fifteen offline tests pass, including diagnostic isolation, incorrect failure classification, and summary generation.

Next work remains token/reasoning accounting, endpoint qualification, and the
multi-workload runner described in the README.
