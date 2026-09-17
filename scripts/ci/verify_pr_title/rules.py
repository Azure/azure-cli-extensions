from __future__ import annotations

from .extractors import AfterPrefixExtractor, FullTitleExtractor
from .rule import Rule
from .verifiers import RegexVerifier

RULES: list[Rule] = [
    Rule(
        name="Component prefix present",
        extractor=FullTitleExtractor(),
        verifier=RegexVerifier(
            pattern=r"^(\[.+?\]|\{.+?\})",
            error_message=(
                "Title must start with a non-empty [Component] or {Component} bracket.\n"
                "  [Component]  – customer-facing change (included in HISTORY.rst)\n"
                "  {Component}  – non-customer-facing change (excluded from HISTORY.rst)\n"
                "  Examples: [Storage], {Misc.}, [API Management]"
            ),
        ),
    ),
    Rule(
        name="Non-empty description after prefix",
        extractor=AfterPrefixExtractor(),
        verifier=RegexVerifier(
            pattern=(
                r"^\s*(?:(?:BREAKING CHANGE:|Hotfix:?|Fix\s+#\d+:?)\s+)\S"
                r"|"
                r"^\s*(?!BREAKING CHANGE:|Hotfix:?|Fix\s+#\d+:?)\S"
            ),
            error_message=(
                "Title must contain a description after the component prefix.\n"
                "  Optionally preceded by a recognised keyword:\n"
                "    BREAKING CHANGE: <description>\n"
                "    Hotfix[:]        <description>\n"
                "    Fix #<N>[:]      <description>\n"
                "  Examples:\n"
                "    [Storage] az storage blob upload: Add --overwrite flag\n"
                "    [Compute] BREAKING CHANGE: Remove deprecated --sku parameter\n"
                "    [Core] Fix #12345: az account show fails on managed identity\n"
                "    {Misc.} Fix typo in help text"
            ),
        ),
    ),
]
