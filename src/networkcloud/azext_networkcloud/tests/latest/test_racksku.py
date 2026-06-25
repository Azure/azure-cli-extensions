# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
RackSku tests scenarios
"""

from azure.cli.testsdk import ScenarioTest
from azure.cli.testsdk.scenario_tests import AllowLargeResponse

from .config import CONFIG
from .utils.assert_messages import (
    missing_field_message,
    properties_key_mismatch_message,
)
from .utils.output_checks import (
    get_value,
    show_properties,
)


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """# Testcase: scenario1"""
    setup_scenario1(test)
    step_show(test, checks=None)
    step_list_subscription(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """RackSku show operation"""
    if checks is not None:
        test.cmd("az networkcloud racksku show --name {rackskuname}", checks=checks)
        return

    result = test.cmd(
        "az networkcloud racksku show --name {rackskuname}"
    ).get_output_in_json()
    context = "Racksku show"
    show_properties(result)
    assert result.get("name") is not None, missing_field_message(
        context, "name", result
    )
    assert result.get("properties") is not None, missing_field_message(
        context, "properties", result
    )

    assert result.get("deploymentType") == get_value(
        test, "deployType"
    ), properties_key_mismatch_message("deployType")

    assert result.get("rackType") == get_value(
        test, "rackType"
    ), properties_key_mismatch_message("rackType")


def step_list_subscription(test, checks=None):
    """RackSku list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud racksku list")


class RackSkuScenarioTest(ScenarioTest):
    """RackSku scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "rackskuname": CONFIG.get("RACKSKU", "name"),
                "deployType": CONFIG.get("RACKSKU", "deployment_type"),
                "rackType": CONFIG.get("RACKSKU", "rack_type"),
            }
        )

    @AllowLargeResponse()
    def test_racksku_scenario1(self):
        """test scenario for RackSku operations"""
        call_scenario1(self)
