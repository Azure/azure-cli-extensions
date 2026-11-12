from __future__ import annotations

import sys

from .runner import run

_EXPECTED_FORMAT = (
    "[Component] (BREAKING CHANGE: | Hotfix[:] | Fix #<N>[:])? <description>\n"
    "{Component} (BREAKING CHANGE: | Hotfix[:] | Fix #<N>[:])? <description>"
)


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python -m verify_pr_title "<PR title>"', file=sys.stderr)
        sys.exit(2)

    title = sys.argv[1]
    failures = run(title)

    if not failures:
        print(f"PR title validation passed: '{title}'")
        sys.exit(0)

    print(f"PR title validation failed for: '{title}'\n")
    for name, error in failures:
        print(f"  Rule: {name}")
        for line in error.splitlines():
            print(f"    {line}")
        print()
    print(f"Expected format:\n  {_EXPECTED_FORMAT}")
    sys.exit(1)


if __name__ == "__main__":
    main()
