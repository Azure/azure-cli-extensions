# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

# from azure.cli.testsdk.scenario_tests import AllowLargeResponse

# """
# Bootstrap Device tests scenarios
# """

# from azure.cli.testsdk import ScenarioTest

# from .config import CONFIG


# def setup_scenario1(test):
#     """Env setup_scenario1"""
#     pass


# def cleanup_scenario1(test):
#     """Env cleanup_scenario1"""
#     pass


# def call_scenario1(test):
#     """Testcase: scenario1"""
#     setup_scenario1(test)
#     step_show(test, checks=[])
#     step_list_resource_group(test, checks=[])
#     step_list_subscription(test, checks=[])
#     cleanup_scenario1(test)


# def step_show(test, checks=None):
#     """Bootstrap Device show operation"""
#     if checks is None:
#         checks = []
#     test.cmd(
#         "az networkfabric bootstrapdevice show --resource-name {name} --resource-group {rg}"
#     )


# def step_list_resource_group(test, checks=None):
#     """Bootstrap Device list by resource group operation"""
#     if checks is None:
#         checks = []
#     test.cmd("az networkfabric bootstrapdevice list --resource-group {rg}")


# def step_list_subscription(test, checks=None):
#     """Bootstrap Device list by subscription operation"""
#     if checks is None:
#         checks = []
#     test.cmd("az networkfabric bootstrapdevice list")


# class GA_BootstrapDeviceScenarioTest1(ScenarioTest):
#     """Bootstrap Device Scenario test"""

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.kwargs.update(
#             {
#                 "name": CONFIG.get("BOOTSTRAP_DEVICE", "name"),
#                 "rg": CONFIG.get("BOOTSTRAP_DEVICE", "resource_group"),
#             }
#         )

#     @AllowLargeResponse()
#     def test_GA_bootstrapdevice_scenario1(self):
#         """test scenario for Bootstrap Device CRUD operations"""
#         call_scenario1(self)
