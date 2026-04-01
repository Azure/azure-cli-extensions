# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

# """
# NF post tests scenarios
# """

# from azure.cli.testsdk import ScenarioTest

# from .config import CONFIG


# def setup_scenario(test):
#     """Env setup_scenario"""
#     pass


# def cleanup_scenario(test):
#     """Env cleanup_scenario"""
#     pass


# def call_scenario1(test):
#     """Testcase: scenario1"""
#     setup_scenario(test)
#     step_resync_scenario1(test)
#     cleanup_scenario(test)


# def call_scenario2(test):
#     """Testcase: scenario2"""
#     setup_scenario(test)
#     step_resync_scenario2(test)
#     cleanup_scenario(test)


# def step_resync_scenario1(test, checks=None):
#     """neighborgroup resync password operation"""
#     if checks is None:
#         checks = []
#     test.cmd(
#         "az networkfabric neighborgroup resync --resource-name {name} --resource-group {rg}"
#     )


# def step_resync_scenario2(test, checks=None):
#     """neighborgroup resync password operation"""
#     if checks is None:
#         checks = []
#     test.cmd(
#         "az networkfabric neighborgroup resync --neighbor-group-name {name} --resource-group {rg}"
#     )


# class GA__NeighborGroupResyncScenarioTest1(ScenarioTest):
#     """Neighbor Group Scenario test"""

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.kwargs.update(
#             {
#                 "name": CONFIG.get("NEIGHBOR_GROUP", "name"),
#                 "rg": CONFIG.get("NEIGHBOR_GROUP", "resource_group"),
#             }
#         )

#     def test_GA_neighborgroup_resync_scenario1(self):
#         """test scenario for NeighborGroup resync operations"""
#         call_scenario1(self)
