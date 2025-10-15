# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

# from azure.cli.testsdk.scenario_tests import AllowLargeResponse

# """
# NNI tests scenarios
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
#     step_update_npb_static_bfd_admin_state_secnario1(test, checks=[])
#     cleanup_scenario(test)


# def call_scenario2(test):
#     """Testcase: scenario1"""
#     setup_scenario(test)
#     step_update_npb_static_bfd_admin_state_secnario2(test, checks=[])
#     cleanup_scenario(test)


# def call_scenario3(test):
#     """Testcase: scenario1"""
#     setup_scenario(test)
#     step_update_npb_static_bfd_admin_state_secnario3(test, checks=[])
#     cleanup_scenario(test)


# def step_update_npb_static_bfd_admin_state_secnario1(test, checks=None):
#     """nni run Update BFD Admin State operation"""
#     if checks is None:
#         checks = []
#     test.cmd(
#         "az networkfabric nni update-npb-static-route-bfd-administrative-state --fabric {fabric} --resource-name {name}"
#         " --resource-group {rg} --state {state} --resource-ids {resourceIds}"
#     )


# def step_update_npb_static_bfd_admin_state_secnario2(test, checks=None):
#     """nni run Update BFD Admin State operation"""
#     if checks is None:
#         checks = []
#     test.cmd(
#         "az networkfabric nni update-npb-static-route-bfd-administrative-state --fabric-name {fabric} --nni-name {name}"
#         " --resource-group {rg} --state {state} --resource-ids {resourceIds}"
#     )


# def step_update_npb_static_bfd_admin_state_secnario3(test, checks=None):
#     """nni run Update BFD Admin State operation"""
#     if checks is None:
#         checks = []
#     test.cmd(
#         "az networkfabric nni update-npb-static-route-bfd-administrative-state --network-to-network-interconnect-name {name}"
#         " --resource-group {rg} --state {state} --resource-ids {resourceIds}"
#     )


# class GA_NNIUpdateNPBStaticRouteBFDAdminStateTest1(ScenarioTest):
#     """NNIScenario test"""

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.kwargs.update(
#             {
#                 "name": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "name"),
#                 "rg": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "resource_group"),
#                 "fabric": CONFIG.get("NETWORK_TO_NETWORK_INTERCONNECT", "fabric"),
#                 "resourceIds": CONFIG.get(
#                     "NETWORK_TO_NETWORK_INTERCONNECT", "resource_ids"
#                 ),
#                 "state": CONFIG.get(
#                     "NETWORK_TO_NETWORK_INTERCONNECT", "npb_route_bfd_state"
#                 ),
#             }
#         )

#     @AllowLargeResponse()
#     def test_GA_nni_update_npb_static_bfd_admin_state_scenario1(self):
#         """test scenario for NNI CRUD operations"""
#         call_scenario1(self)
