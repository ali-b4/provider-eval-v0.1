"""Provider A adapter."""

from typing import Any

from .base import BaseProvider


class ProviderA(BaseProvider):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Configure Provider A before use")

