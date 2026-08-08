from __future__ import annotations

import re
from abc import ABC, abstractmethod


class Extractor(ABC):
    @abstractmethod
    def extract(self, title: str) -> str: ...


class FullTitleExtractor(Extractor):
    def extract(self, title: str) -> str:
        return title


class ComponentPrefixExtractor(Extractor):
    _PATTERN = re.compile(r"^(\[.+?\]|\{.+?\})")

    def extract(self, title: str) -> str:
        m = self._PATTERN.match(title)
        return m.group(1) if m else ""


class AfterPrefixExtractor(Extractor):
    _PATTERN = re.compile(r"^(?:\[.+?\]|\{.+?\})\s*(.*)", re.DOTALL)

    def extract(self, title: str) -> str:
        m = self._PATTERN.match(title)
        return m.group(1) if m else title
