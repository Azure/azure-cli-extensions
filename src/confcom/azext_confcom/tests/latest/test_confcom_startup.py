# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import unittest
import pytest

from azext_confcom.custom import acipolicygen_confcom

import pytest

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


# @unittest.skip("not in use")
@pytest.mark.run(order=1)
class InitialErrors(unittest.TestCase):
    def test_invalid_output_flags(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            acipolicygen_confcom(
                "fakepath/input.json",
                None,
                None,
                None,
                None,
                None,
                outraw=True,
                outraw_pretty_print=True,
            )
        self.assertEqual(wrapped_exit.exception.code, 1)

        with self.assertRaises(SystemExit) as wrapped_exit:
            acipolicygen_confcom(
                "fakepath/input.json", None, None, None, None, None, outraw=True, print_policy_to_terminal=True
            )
        self.assertEqual(wrapped_exit.exception.code, 1)

        with self.assertRaises(SystemExit) as wrapped_exit:
            acipolicygen_confcom(
                "fakepath/input.json", None, None, None, None, None, print_policy_to_terminal=True, outraw_pretty_print=True
            )
        self.assertEqual(wrapped_exit.exception.code, 1)

    def test_invalid_many_input_types(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            acipolicygen_confcom(
                "fakepath/input.json", "fakepath2/template.json", None, None, None, None
            )
        self.assertEqual(wrapped_exit.exception.code, 1)

    def test_diff_wrong_input_type(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            acipolicygen_confcom(
                "fakepath/input.json", None, None, None, None, None, diff=True
            )
        self.assertEqual(wrapped_exit.exception.code, 1)

        with self.assertRaises(SystemExit) as wrapped_exit:
            acipolicygen_confcom(None, None, None, "alpine", None, None, diff=True)
        self.assertEqual(wrapped_exit.exception.code, 1)

    def test_parameters_without_template(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            acipolicygen_confcom(
                None, None, "fakepath/parameters.json", None, None, None
            )
        self.assertEqual(wrapped_exit.exception.code, 1)
