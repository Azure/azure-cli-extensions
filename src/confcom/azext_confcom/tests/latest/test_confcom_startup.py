# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import ScenarioTest
from azext_confcom.custom import acipolicygen_confcom

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class InitialErrors(ScenarioTest):
    def test_invalid_output_flags(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --outraw --outraw-pretty-print")
        self.assertEqual(wrapped_exit.exception.code, 1)

        with self.assertRaises(SystemExit) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --outraw --print-policy")
        self.assertEqual(wrapped_exit.exception.code, 1)

        with self.assertRaises(SystemExit) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --print-policy --outraw-pretty-print")
        self.assertEqual(wrapped_exit.exception.code, 1)

    def test_invalid_many_input_types(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json -a fakepath2/template.json")
        self.assertEqual(wrapped_exit.exception.code, 1)

    def test_diff_wrong_input_type(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --diff")
        self.assertEqual(wrapped_exit.exception.code, 1)

        with self.assertRaises(SystemExit) as wrapped_exit:
            self.cmd("az confcom acipolicygen --image alpine --diff")
        self.assertEqual(wrapped_exit.exception.code, 1)

    def test_parameters_without_template(self):
        with self.assertRaises(SystemExit) as wrapped_exit:
            self.cmd("az confcom acipolicygen -p fakepath/parameters.json")
            acipolicygen_confcom(
                None, None, "fakepath/parameters.json", None, None, None
            )
        self.assertEqual(wrapped_exit.exception.code, 1)
