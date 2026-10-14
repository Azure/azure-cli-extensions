# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""Tests for the --add-proxy-bypass / --clear-proxy-bypass keyword handling.

Covers:
  * ``parse_proxy_bypass_keywords`` -- the single split every consumer shares, so
    validation and the code acting on the keywords cannot disagree about what the
    user asked for.
  * ``has_proxy_bypass_keyword`` -- case-insensitive whole-keyword matching.
  * ``validate_proxy_bypass`` -- rejects unknown keywords with a message naming the
    flag, since get_enum_type cannot check a comma-separated list; rejects the same
    keyword on both flags; and rejects clearing the Arc bypass alongside a new
    --proxy-skip-range, which would already drop those endpoints on its own.
"""

import os
import sys
from argparse import Namespace

import pytest
from azure.cli.core.azclierror import ArgumentUsageError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
import azext_connectedk8s._constants as consts
from azext_connectedk8s._validators import (
    has_proxy_bypass_keyword,
    parse_proxy_bypass_keywords,
    validate_proxy_bypass,
)

ARC = consts.Proxy_Bypass_Arc_Keyword
CONTAINER_INSIGHTS = consts.Proxy_Bypass_ContainerInsights_Extension_Type


# ---------------- Tests for parse_proxy_bypass_keywords ----------------
@pytest.mark.parametrize(
    "value,expected",
    [
        (None, []),
        ("", []),
        ("   ", []),
        (",", []),
        ("Arc", ["Arc"]),
        (" aRc ", ["aRc"]),
        ("Arc,Arc", ["Arc", "Arc"]),
        ("Arc, ,", ["Arc"]),
        (
            "Arc, Microsoft.AzureMonitor.Containers",
            ["Arc", "Microsoft.AzureMonitor.Containers"],
        ),
    ],
    ids=[
        "none",
        "empty",
        "blank",
        "separator-only",
        "single",
        "trims-spaces",
        "keeps-repeats",
        "drops-empty-entries",
        "both-keywords",
    ],
)
def test_parse_keywords(value, expected):
    assert parse_proxy_bypass_keywords(value) == expected


# ---------------- Tests for has_proxy_bypass_keyword ----------------
@pytest.mark.parametrize(
    "value,keyword,expected",
    [
        (None, ARC, False),
        ("", ARC, False),
        ("Arc", ARC, True),
        (" aRc ", ARC, True),
        ("ARC", ARC, True),
        ("Arc", CONTAINER_INSIGHTS, False),
        (f"{ARC},{CONTAINER_INSIGHTS}", CONTAINER_INSIGHTS, True),
        ("microsoft.azuremonitor.containers", CONTAINER_INSIGHTS, True),
        ("Arcadia", ARC, False),
        ("NotArc", ARC, False),
    ],
    ids=[
        "none",
        "empty",
        "exact",
        "any-case-and-spaces",
        "upper",
        "other-keyword-absent",
        "second-of-two",
        "extension-type-lowercased",
        "no-prefix-match",
        "no-suffix-match",
    ],
)
def test_has_keyword(value, keyword, expected):
    assert has_proxy_bypass_keyword(value, keyword) is expected


# ---------------- Tests for validate_proxy_bypass ----------------
def _namespace(added=None, cleared=None, no_proxy=""):
    return Namespace(
        add_proxy_bypass=added, clear_proxy_bypass=cleared, no_proxy=no_proxy
    )


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        ARC,
        CONTAINER_INSIGHTS,
        f"{ARC},{CONTAINER_INSIGHTS}",
        f" aRc , {CONTAINER_INSIGHTS.upper()} ",
    ],
    ids=["none", "empty", "arc", "extension-type", "both", "any-case-and-spaces"],
)
def test_validate_accepts_supported_keywords_on_add(value):
    validate_proxy_bypass(_namespace(added=value))


@pytest.mark.parametrize(
    "value",
    [None, "", ARC, CONTAINER_INSIGHTS, f"{ARC},{CONTAINER_INSIGHTS}"],
    ids=["none", "empty", "arc", "extension-type", "both"],
)
def test_validate_accepts_supported_keywords_on_clear(value):
    validate_proxy_bypass(_namespace(cleared=value))


def test_validate_accepts_a_namespace_without_the_flags():
    # connect has no --clear-proxy-bypass, so both are read defensively.
    validate_proxy_bypass(Namespace())


@pytest.mark.parametrize(
    "added,cleared",
    [(ARC, CONTAINER_INSIGHTS), (CONTAINER_INSIGHTS, ARC)],
    ids=["add-arc", "add-extension-type"],
)
def test_validate_accepts_different_keywords_on_each_flag(added, cleared):
    validate_proxy_bypass(_namespace(added=added, cleared=cleared))


@pytest.mark.parametrize(
    "kwarg,flag",
    [("added", "--add-proxy-bypass"), ("cleared", "--clear-proxy-bypass")],
    ids=["add", "clear"],
)
def test_validate_rejects_an_unknown_keyword_on_either_flag(kwarg, flag):
    with pytest.raises(ArgumentUsageError) as err:
        validate_proxy_bypass(_namespace(**{kwarg: "Bogus"}))
    message = str(err.value)
    assert flag in message
    assert "Bogus" in message
    assert ARC in message
    assert CONTAINER_INSIGHTS in message


def test_validate_reports_only_the_unknown_keywords():
    with pytest.raises(ArgumentUsageError) as err:
        validate_proxy_bypass(_namespace(added=f"{ARC},Bogus,Nope"))
    assert "Bogus, Nope" in str(err.value)


@pytest.mark.parametrize(
    "keyword", [ARC, CONTAINER_INSIGHTS], ids=["arc", "extension-type"]
)
def test_validate_rejects_the_same_keyword_on_both_flags(keyword):
    # Adding and clearing the same bypass in one command has no defined outcome.
    with pytest.raises(ArgumentUsageError) as err:
        validate_proxy_bypass(_namespace(added=keyword, cleared=keyword.lower()))
    message = str(err.value)
    assert "--add-proxy-bypass" in message
    assert "--clear-proxy-bypass" in message


def test_validate_allows_clearing_arc_together_with_a_new_skip_range():
    # The new skip range becomes the base the endpoints are removed from, so the two
    # flags do not contradict each other.
    validate_proxy_bypass(_namespace(cleared=ARC, no_proxy="10.0.0.0/8"))


def test_validate_allows_adding_arc_together_with_a_new_skip_range():
    validate_proxy_bypass(_namespace(added=ARC, no_proxy="10.0.0.0/8"))


def test_validate_allows_clearing_the_extension_bypass_with_a_new_skip_range():
    # The Container Insights bypass lives in a ConfigMap, not the skip range.
    validate_proxy_bypass(_namespace(cleared=CONTAINER_INSIGHTS, no_proxy="10.0.0.0/8"))
