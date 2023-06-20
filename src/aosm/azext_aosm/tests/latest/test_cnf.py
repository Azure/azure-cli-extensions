# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
from unittest.mock import Mock, patch

from azext_aosm.generate_nfd.cnf_nfd_generator import CnfNfdGenerator

# from azure_devtools.scenario_tests import AllowLargeResponse
# from azure.cli.testsdk import ResourceGroupPreparer, ScenarioTest
from azure.cli.core.azclierror import (
    BadRequestError,
    InvalidArgumentValueError,
    ResourceNotFoundError,
    InvalidTemplateError
)

class TestErrorMessages(unittest.TestCase):
    def test_invalid_chart(self):
        with self.assertRaises(InvalidTemplateError):
            CnfNfdGenerator._extract_chart(self, "test/helmChart")    
    # def test_invalid_values(self):
    #     with self.assertRaises(InvalidTemplateError):
    #         CnfNfdGenerator.get_chart_mapping_schema(self, "test")
            
# class AosmScenarioTest(ScenarioTest):
#     @ResourceGroupPreparer(name_prefix="cli_test_aosm")
#     def test__aosm(self, resource_group):
#         self.kwargs.update({"name": "test1"})

#         self.cmd(
#             "aosm create -g {rg} -n {name} --tags foo=doo",
#             checks=[self.check("tags.foo", "doo"), self.check("name", "{name}")],
#         )
#         self.cmd(
#             "aosm update -g {rg} -n {name} --tags foo=boo",
#             checks=[self.check("tags.foo", "boo")],
#         )
#         count = len(self.cmd("aosm list").get_output_in_json())
#         self.cmd(
#             "aosm show - {rg} -n {name}",
#             checks=[
#                 self.check("name", "{name}"),
#                 self.check("resourceGroup", "{rg}"),
#                 self.check("tags.foo", "boo"),
#             ],
#         )
#         self.cmd("aosm delete -g {rg} -n {name}")
#         final_count = len(self.cmd("aosm list").get_output_in_json())
#         self.assertTrue(final_count, count - 1)