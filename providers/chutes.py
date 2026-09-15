"""Chutes provider adapter placeholder."""

from typing import Any

from .base import BaseProvider


class ChutesProvider(BaseProvider):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Configure the Chutes direct API before use")
