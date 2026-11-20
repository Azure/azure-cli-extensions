# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.

# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

"""
Bootstrap Interface tests scenarios
"""

from azure.cli.testsdk import ScenarioTest

from .config import CONFIG
from .utils.output_checks import attr


def setup_scenario1(test):
    """Env setup_scenario1"""
    pass


def cleanup_scenario1(test):
    """Env cleanup_scenario1"""
    pass


def call_scenario1(test):
    """Testcase: scenario1"""
    setup_scenario1(test)
    step_show(
        test,
        checks=[
            test.check("name", attr(test, "name")),
            test.check("provisioningState", attr(test, "expectedProvisioningState")),
            test.check("connectedTo", attr(test, "expectedConnectedTo")),
            test.check("interfaceType", attr(test, "expectedInterfaceType")),
            test.check("ipv4Address", attr(test, "expectedIpv4Address")),
            test.check("ipv6Address", attr(test, "expectedIpv6Address")),
            test.check("physicalIdentifier", attr(test, "expectedPhysicalIdentifier")),
            test.check("operationalState", attr(test, "expectedOperationalState")),
            test.check(
                "administrativeState", attr(test, "expectedAdministrativeState")
            ),
            test.check("configurationState", attr(test, "expectedConfigurationState")),
        ],
    )
    step_list_resource_group(test, checks=[])
    cleanup_scenario1(test)


def step_show(test, checks=None):
    """Bootstrap Interface show operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapinterface show --resource-name {name} --resource-group {rg} "
        "--bootstrap-device {bootstrapDeviceName}",
        checks=checks,
    )


def step_list_resource_group(test, checks=None):
    """Interface list by resource group operation"""
    if checks is None:
        checks = []
    test.cmd(
        "az networkfabric bootstrapinterface list --resource-group {rg} --bootstrap-device {bootstrapDeviceName}"
    )


class GA_BootstrapInterfaceScenarioTest1(ScenarioTest):
    """Bootstrap InterfaceScenario test"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.kwargs.update(
            {
                "name": CONFIG.get("BOOTSTRAP_INTERFACE", "name"),
                "rg": CONFIG.get("BOOTSTRAP_INTERFACE", "resource_group"),
                "bootstrapDeviceName": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "bootstrap_device_name"
                ),
                "expectedAdministrativeState": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_administrative_state"
                ),
                "expectedConfigurationState": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_configuration_state"
                ),
                "expectedConnectedTo": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_connected_to"
                ),
                "expectedInterfaceType": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_interface_type"
                ),
                "expectedIpv4Address": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_ipv4_address"
                ),
                "expectedIpv6Address": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_ipv6_address"
                ),
                "expectedOperationalState": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_operational_state"
                ),
                "expectedPhysicalIdentifier": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_physical_identifier"
                ),
                "expectedProvisioningState": CONFIG.get(
                    "BOOTSTRAP_INTERFACE", "expected_provisioning_state"
                ),
            }
        )

    def test_GA_bootstrapinterface_scenario1(self):
        """test scenario for Bootstrap Interface CRUD operations"""
        call_scenario1(self)
