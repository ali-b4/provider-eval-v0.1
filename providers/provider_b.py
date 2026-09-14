"""Provider B adapter."""

from typing import Any

from .base import BaseProvider


class ProviderB(BaseProvider):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Configure Provider B before use")

