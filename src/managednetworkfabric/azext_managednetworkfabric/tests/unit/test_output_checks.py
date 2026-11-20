# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace

import pytest
from azure.cli.core.aaz.exceptions import AAZInvalidShorthandSyntaxError

from azext_managednetworkfabric.tests.latest.utils.output_checks import attr


@pytest.mark.parametrize(
    "value, expected",
    [
        ('"example-resource"', "example-resource"),
        ("'example-resource'", "example-resource"),
        ('  "example-resource"  ', "example-resource"),
        ('"  description  "', "  description  "),
        ("", ""),
        ('"True"', "True"),
        ('"123"', "123"),
        ('\'{"mtu":1500,"enabled":true}\'', {"mtu": 1500, "enabled": True}),
        ('"{environment:mock}"', {"environment": "mock"}),
        ('"[{name:first},{name:second}]"', [{"name": "first"}, {"name": "second"}]),
        ('"[1,true,null]"', [1, True, None]),
        (0, 0),
        (False, False),
        ({"name": "resource"}, {"name": "resource"}),
    ],
)
def test_attr_normalizes_configured_values(value, expected):
    test = SimpleNamespace(kwargs={"value": value})
    assert attr(test, "value") == expected


@pytest.mark.parametrize("kwargs", [{}, {"missing": None}])
def test_attr_reports_missing_values(kwargs):
    with pytest.raises(AssertionError, match="Test variable 'missing' was not set"):
        attr(SimpleNamespace(kwargs=kwargs), "missing")


def test_attr_reports_invalid_shorthand():
    with pytest.raises(AAZInvalidShorthandSyntaxError):
        attr(SimpleNamespace(kwargs={"value": "{invalid"}), "value")
