# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_vmware.action import script_execution_named_outputs, script_execution_parameters


class TestAction:
    def test_value_execution_parameter(self):
        assert {"name": "dog", "value": {"value": "Fred"}} == script_execution_parameters(["type=value", "name=dog", "value=Fred"])

    def test_secure_value_execution_parameter(self):
        assert {"name": "cat", "secure_value": {"secure_value": "George"}} == script_execution_parameters(["type=SecureValue", "name=cat", "secureValue=George"])

    def test_credential_execution_parameter(self):
        assert {"name": "cow", "credential": {"username": "name", "password":"pwd"}} == script_execution_parameters(["type=Credential", "name=cow", "username=name", "password=pwd"])

    def test_named_outputs(self):
        assert {"dog": "Fred"} == script_execution_named_outputs(["dog=Fred"])
        assert {"dog": "Fred", "cat": "Tom"} == script_execution_named_outputs(["dog=Fred", "cat=Tom"])
