# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import unittest
from unittest.mock import Mock

from azure.cli.core import get_default_cli
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.aaz.exceptions import AAZUnknownFieldError
from azure.cli.core.azclierror import InvalidArgumentValueError

from azext_workload_manager.custom import RuntimeBindingCreate


class RuntimeBindingCreateTest(unittest.TestCase):

    _RESOURCE_ID = (
        "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/runtime-rg/"
        "providers/Microsoft.ContainerService/managedClusters/runtime"
    )
    _IDENTITY_ID = (
        "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/identity-rg/"
        "providers/Microsoft.ManagedIdentity/userAssignedIdentities/runtime"
    )

    def _create_command(self, **overrides):
        command_args = {
            "subscription": "00000000-0000-0000-0000-000000000000",
            "resource_group": "workload-rg",
            "space_name": "workload-space",
            "binding_name": "runtime-binding",
            "location": "eastus2",
            "kind": "Kubernetes",
            **overrides,
        }
        command = RuntimeBindingCreate(cli_ctx=get_default_cli())
        command.ctx = AAZCommandCtx(
            command.cli_ctx,
            command.get_arguments_schema(),
            command_args,
            no_wait_arg="no_wait",
        )
        command.ctx.format_args()
        return command

    def _serialize_content(self, command):
        command.pre_operations()
        command.ctx.get_http_client = Mock(return_value=Mock())
        operation = command.RuntimeBindingsCreateOrUpdate(ctx=command.ctx)
        return operation.content

    def test_managed_binding_serialization(self):
        content = self._serialize_content(self._create_command(
            managed={"managed_profile": {"offering": "Automatic"}},
        ))

        self.assertEqual("Managed", content["properties"]["provisioningMode"])
        self.assertEqual(
            {"offering": "Automatic"},
            content["properties"]["managedProfile"],
        )
        self.assertNotIn("resourceId", content["properties"])

    def test_referenced_binding_serialization(self):
        content = self._serialize_content(self._create_command(
            referenced={"resource_id": self._RESOURCE_ID},
        ))

        self.assertEqual("Referenced", content["properties"]["provisioningMode"])
        self.assertEqual(self._RESOURCE_ID, content["properties"]["resourceId"])
        self.assertNotIn("managedProfile", content["properties"])

    def test_referenced_execution_identity_serialization(self):
        content = self._serialize_content(self._create_command(
            managed={"managed_profile": {"offering": "Automatic"}},
            identity_profile={
                "execution_identity": {
                    "referenced": {
                        "user_assigned_identity_resource_id": self._IDENTITY_ID,
                    },
                    "scope": "SandboxGroup",
                },
            },
        ))

        execution_identity = content["properties"]["identityProfile"]["executionIdentity"]
        self.assertEqual("Referenced", execution_identity["provisioningMode"])
        self.assertEqual(
            self._IDENTITY_ID,
            execution_identity["userAssignedIdentityResourceId"],
        )

    def test_service_managed_execution_identity_serialization(self):
        content = self._serialize_content(self._create_command(
            managed={"managed_profile": {"offering": "Automatic"}},
            identity_profile={
                "execution_identity": {
                    "service_managed": {},
                    "scope": "SandboxGroup",
                },
            },
        ))

        execution_identity = content["properties"]["identityProfile"]["executionIdentity"]
        self.assertEqual("ServiceManaged", execution_identity["provisioningMode"])
        self.assertEqual("SandboxGroup", execution_identity["scope"])

    def test_both_binding_variants_are_rejected(self):
        command = self._create_command(
            managed={"managed_profile": {"offering": "Automatic"}},
            referenced={"resource_id": self._RESOURCE_ID},
        )

        with self.assertRaisesRegex(InvalidArgumentValueError, "exactly one of --managed or --referenced"):
            command.pre_operations()

    def test_neither_binding_variant_is_rejected(self):
        with self.assertRaises(AAZUnknownFieldError):
            self._serialize_content(self._create_command())

    def test_both_execution_identity_variants_are_rejected(self):
        command = self._create_command(
            managed={"managed_profile": {"offering": "Automatic"}},
            identity_profile={
                "execution_identity": {
                    "referenced": {
                        "user_assigned_identity_resource_id": self._IDENTITY_ID,
                    },
                    "service_managed": {},
                    "scope": "SandboxGroup",
                },
            },
        )

        with self.assertRaisesRegex(InvalidArgumentValueError, "exactly one execution identity variant"):
            command.pre_operations()

    def test_neither_execution_identity_variant_is_rejected(self):
        command = self._create_command(
            managed={"managed_profile": {"offering": "Automatic"}},
            identity_profile={
                "execution_identity": {
                    "scope": "SandboxGroup",
                },
            },
        )

        with self.assertRaises(AAZUnknownFieldError):
            self._serialize_content(command)


if __name__ == "__main__":
    unittest.main()