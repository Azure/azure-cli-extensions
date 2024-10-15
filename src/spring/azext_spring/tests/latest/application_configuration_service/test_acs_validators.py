# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import unittest
from argparse import Namespace
from azure.cli.core.azclierror import InvalidArgumentValueError
from ...._validators_enterprise import (validate_pattern_for_show_acs_configs)

valid_pattern_dict = {
    "ASfefsdeDfWeb/azdit": "ASfefsdeDfWeb/azdit",
    "ASfefsdeDfWeb/*": "ASfefsdeDfWeb/default",
    "ASfefsdeDfWeb/default": "ASfefsdeDfWeb/default",
    "admin-application": "admin-application/default",
    "admin-application/*": "admin-application/default",
    "admin-application/default": "admin-application/default",
    "application/default": "application/default",
    "application/*": "application/default",
    "application": "application/default",
    "a": "a/default",
    "application/b": "application/b",
    "a/b": "a/b",
    "a/*": "a/default"
}

invalid_pattern_list = [
    "admin-application/",
    "admin-application/default/default",
    "admin-application//my-profile",
    "admin-application///my-profile",
    "admin-application/**",
    "/*",
    "/*//",
    "/default",
    "//default",
    "  /default",
    " /default",
    "application/default ",
    "application/ default",
    "application /default",
    " application/default",
    "application/ ",
    "application/  "
]


class TestAcsValidators(unittest.TestCase):
    def test_valid_pattern_for_show_acs_configs(self):
        for pattern in valid_pattern_dict.keys():
            ns = Namespace(resource_group="group",
                           service="service",
                           config_file_pattern=pattern)
            validate_pattern_for_show_acs_configs(ns)
            self.assertEquals(valid_pattern_dict[pattern], ns.config_file_pattern)

    def test_invalid_pattern_for_show_acs_configs(self):
        expectedErr = "Pattern should be in the format of 'application' or 'application/profile'"
        for pattern in invalid_pattern_list:
            with self.assertRaises(InvalidArgumentValueError) as context:
                ns = Namespace(resource_group="group",
                               service="service",
                               config_file_pattern=pattern)
                validate_pattern_for_show_acs_configs(ns)
            self.assertTrue(expectedErr in str(context.exception))
