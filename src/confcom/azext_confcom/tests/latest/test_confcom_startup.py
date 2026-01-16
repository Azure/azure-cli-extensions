# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
from azure.cli.testsdk import ScenarioTest
from knack.util import CLIError

TEST_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), ".."))


class InitialErrors(ScenarioTest):
    def test_invalid_output_flags(self):
        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --outraw --outraw-pretty-print")
        self.assertEqual(wrapped_exit.exception.args[0], "Can only print in one format at a time")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --outraw --print-policy")
        self.assertEqual(wrapped_exit.exception.args[0], "Can only print in one format at a time")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --print-policy --outraw-pretty-print")
        self.assertEqual(wrapped_exit.exception.args[0], "Can only print in one format at a time")

    def test_invalid_many_input_types(self):
        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json -a fakepath2/template.json")
        self.assertEqual(wrapped_exit.exception.args[0], "Can only generate CCE policy from one source at a time")

    def test_diff_wrong_input_type(self):
        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --diff")
        self.assertEqual(wrapped_exit.exception.args[0], "Can only diff CCE policy from ARM Template or YAML File")

        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acipolicygen --image alpine --diff")
        self.assertEqual(wrapped_exit.exception.args[0], "Can only diff CCE policy from ARM Template or YAML File")

    def test_parameters_without_template(self):
        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acipolicygen -p fakepath/parameters.json -i fakepath/input.json")
        self.assertEqual(wrapped_exit.exception.args[0], "Can only use ARM Template Parameters if ARM Template is also present")

    def test_input_and_virtual_node(self):
        with self.assertRaises(CLIError) as wrapped_exit:
            self.cmd("az confcom acipolicygen -i fakepath/input.json --virtual-node-yaml fakepath/virtual-node.yaml")
        self.assertEqual(wrapped_exit.exception.args[0], "Can only generate CCE policy from one source at a time")
