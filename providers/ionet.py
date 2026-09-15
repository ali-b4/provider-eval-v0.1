"""io.net adapter placeholder, matching the future benchmark adapter interface.

The working request workflow is scripts/manual_request.py --providers ionet.
"""
from typing import Any
from .base import BaseProvider


class IonetProvider(BaseProvider):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError("Use scripts/manual_request.py --providers ionet")
