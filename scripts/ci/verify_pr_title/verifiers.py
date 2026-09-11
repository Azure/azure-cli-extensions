from __future__ import annotations

import re
from abc import ABC, abstractmethod


class Verifier(ABC):
    @abstractmethod
    def verify(self, value: str) -> tuple[bool, str]: ...


class RegexVerifier(Verifier):
    def __init__(self, pattern: str, error_message: str, *, fullmatch: bool = False) -> None:
        self._regex = re.compile(pattern)
        self._error_message = error_message
        self._fullmatch = fullmatch

    def verify(self, value: str) -> tuple[bool, str]:
        fn = self._regex.fullmatch if self._fullmatch else self._regex.search
        if fn(value):
            return True, ""
        return False, self._error_message


class NegativeRegexVerifier(Verifier):
    def __init__(self, pattern: str, error_message: str) -> None:
        self._regex = re.compile(pattern)
        self._error_message = error_message

    def verify(self, value: str) -> tuple[bool, str]:
        if not self._regex.search(value):
            return True, ""
        return False, self._error_message


class NonEmptyVerifier(Verifier):
    def __init__(self, error_message: str) -> None:
        self._error_message = error_message

    def verify(self, value: str) -> tuple[bool, str]:
        if value.strip():
            return True, ""
        return False, self._error_message
