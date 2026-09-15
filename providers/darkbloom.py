"""Darkbloom provider adapter placeholder."""

from typing import Any

from .base import BaseProvider


class DarkbloomProvider(BaseProvider):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Configure the Darkbloom direct API before use")

