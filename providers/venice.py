"""Venice provider adapter placeholder."""

from typing import Any

from .base import BaseProvider


class VeniceProvider(BaseProvider):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Configure the Venice direct API before use")
