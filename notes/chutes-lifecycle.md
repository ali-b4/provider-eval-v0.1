# Chutes direct request lifecycle

This is a deliberately concrete probe, not a harness or provider abstraction.

1. **Python**: `scripts/chutes_raw_request.py` reads `CHUTES_API_KEY` and `CHUTES_MODEL`, builds one JSON payload, and uses only Python's standard library.
2. **HTTP request**: `POST https://llm.chutes.ai/v1/chat/completions`. The API key is sent as `Authorization: Bearer ...`; the model and messages are JSON fields.
3. **Provider API**: Chutes' shared OpenAI-compatible gateway receives the request and selects the named model.
4. **Inference**: the selected model generates a non-streaming completion from the message.
5. **HTTP response**: Python receives an HTTP status, headers, and JSON body. The script prints all three (with the key redacted).
6. **Parsed result**: response text is at `body.choices[0].message.content`; token accounting is at `body.usage` (`prompt_tokens`, `completion_tokens`, `total_tokens`). The selected model is echoed at `body.model`.

The checked-in `results/raw/chutes.example.json` records the expected successful response shape with provider-generated IDs and token counts redacted. A live capture could not be made in this environment because no `CHUTES_API_KEY` was available.

Source: [Chutes authentication](https://chutes.ai/docs/getting-started/authentication), [Qwen3.8-27B Chutes model page](https://chutes.ai/app/chute/chutes-qwen-qwen3-8-27b-tee).
