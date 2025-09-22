# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
#
# --------------------------------------------------------------------------------------------
# pylint: disable=too-few-public-methods,unnecessary-pass,unused-argument

# from azure.cli.testsdk.scenario_tests import AllowLargeResponse

# """
# External Network tests scenarios
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
#     """# Testcase: scenario1"""
#     setup_scenario1(test)
#     step_update_bfd_admin_state(test, checks=[])
#     cleanup_scenario1(test)


# def step_update_bfd_admin_state(test, checks=None):
#     """external network run Update BFD Admin State operation"""
#     if checks is None:
#         checks = []
#     test.cmd(
#         "az networkfabric externalnetwork update-bfd-administrative-state --l3domain {l3Domain} --resource-name {name}"
#         " --resource-group {rg} --administrative-state {administrativeState} --route-type {routeType}"
#     )


# class GA_ExternalNetworkUpdateBFDAdminStateTest1(ScenarioTest):
#     """External Network test"""

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.kwargs.update(
#             {
#                 "name": CONFIG.get("EXTERNAL_NETWORK", "optionb_name"),
#                 "rg": CONFIG.get("EXTERNAL_NETWORK", "optionb_resource_group"),
#                 "l3Domain": CONFIG.get("EXTERNAL_NETWORK", "optionb_l3_domain"),
#                 "administrativeState": CONFIG.get(
#                     "EXTERNAL_NETWORK", "administrative_state"
#                 ),
#                 "routeType": CONFIG.get("EXTERNAL_NETWORK", "route_type"),
#             }
#         )

#     @AllowLargeResponse()
#     def test_GA_externalnetwork_UpdateBFDAdminState_scenario1(self):
#         """test scenario for externalnetwork CRUD operations"""
#         call_scenario1(self)
