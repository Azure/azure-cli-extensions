from __future__ import annotations

from .rule import Rule
from .rules import RULES


def run(title: str, rules: list[Rule] = RULES) -> list[tuple[str, str]]:
    failures: list[tuple[str, str]] = []
    for rule in rules:
        passed, error = rule.check(title)
        if not passed:
            failures.append((rule.name, error))
    return failures
