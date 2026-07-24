from __future__ import annotations

from dataclasses import dataclass

from .extractors import Extractor
from .verifiers import Verifier


@dataclass
class Rule:
    name: str
    extractor: Extractor
    verifier: Verifier

    def check(self, title: str) -> tuple[bool, str]:
        value = self.extractor.extract(title)
        return self.verifier.verify(value)
