"""Common interface for inference providers."""

from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """Minimal provider interface used by the benchmark scripts."""

    @abstractmethod
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> dict[str, Any]:
        """Send chat messages and return a normalized response."""
        raise NotImplementedError

