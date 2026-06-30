# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
NF post tests scenarios
"""

from unittest.mock import patch
from azure.cli.testsdk import ScenarioTest
from azext_managednetworkfabric.operations.error_format import ErrorFormat

from .config import CONFIG


def setup_scenario(test):
    """Env setup_scenario"""
    pass


def cleanup_scenario(test):
    """Env cleanup_scenario"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario(test)
    step_resync_password_scenario1(test)
    cleanup_scenario(test)


def call_scenario2(test):
    """Testcase: scenario2"""
    setup_scenario(test)
    step_resync_password_scenario2(test)
    cleanup_scenario(test)


def call_scenario3(test):
    """Testcase: scenario3 - partial success"""
    setup_scenario(test)
    step_resync_password_partial_success(test)
    cleanup_scenario(test)


def step_resync_password_scenario1(test, checks=None):
    """nf resync password operation"""
    if checks is None:
        checks = []
    output = test.cmd(
        "az networkfabric fabric resync-password --resource-name {name} --resource-group {resourceGroup}"
    ).get_output_in_json()

    assert output["status"] == "Succeeded"
    assert "networkFabrics" in output.get("resourceId", "")


def step_resync_password_scenario2(test, checks=None):
    """nf resync password operation"""
    if checks is None:
        checks = []
    output = test.cmd(
        "az networkfabric fabric resync-password --network-fabric-name {name} --resource-group {resourceGroup}"
    ).get_output_in_json()

    assert output["status"] == "Succeeded"
    assert "networkFabrics" in output.get("resourceId", "")


def step_resync_password_partial_success(test, checks=None):
    """nf resync password operation with partial success"""
    if checks is None:
        checks = []

    error_messages = []
    original = ErrorFormat.handle_lro_error

    def capture_and_raise(http_error):
        error_messages.append(ErrorFormat.format_error_message(http_error))
        original(http_error)

    with patch.object(ErrorFormat, "handle_lro_error", staticmethod(capture_and_raise)):
        test.cmd(
            "az networkfabric fabric resync-password --resource-name {name} --resource-group {resourceGroup}",
            expect_failure=True,
        )

    error_msg = error_messages[0]
    assert "(PartialSuccess)" in error_msg
    assert "Code: PartialSuccess" in error_msg
    assert "Resync succeeded for only some devices" in error_msg
    assert "Exception Details:" in error_msg
    assert "(CouldNotConnect)" in error_msg
    assert "Code: CouldNotConnect" in error_msg
    assert "Message: Could not connect to the device" in error_msg
    assert "Target:" in error_msg
    assert "networkDevices/" in error_msg


class GA_NFResyncPasswordScenarioTest1(ScenarioTest):
    """NFScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("NETWORK_FABRIC", "name"),
                "resourceGroup": CONFIG.get("NETWORK_FABRIC", "resource_group"),
            }
        )

    def test_GA_nf_resync_password_scenario1(self):
        """test scenario for NF resync password operations"""
        call_scenario1(self)

    def test_GA_nf_resync_password_scenario2(self):
        """test scenario for NF resync password with alias"""
        call_scenario2(self)

    def test_GA_nf_resync_password_scenario3(self):
        """test scenario for NF resync password with partial success"""
        call_scenario3(self)
