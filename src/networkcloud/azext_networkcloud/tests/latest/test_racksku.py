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

from .config import CONFIG


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
    if checks is None:
        checks = []
    test.cmd("az networkcloud racksku show --name {rackskuname}")


def step_list_subscription(test, checks=None):
    """RackSku list by subscription operation"""
    if checks is None:
        checks = []
    test.cmd("az networkcloud racksku list")


class RackSkuScenarioTest(ScenarioTest):
    """RackSku scenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update({"rackskuname": CONFIG.get("RACKSKU", "name")})

    def test_racksku_scenario1(self):
        """test scenario for RackSku operations"""
        call_scenario1(self)
