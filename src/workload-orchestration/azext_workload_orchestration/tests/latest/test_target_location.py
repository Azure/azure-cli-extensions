# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os
import tempfile
import unittest
from unittest import mock

from azure.cli.core import get_default_cli
from azure.cli.core.aaz._command_ctx import AAZCommandCtx
from azure.cli.core.azclierror import InvalidArgumentValueError
from azure.cli.core.parser import AzCliCommandParser

from azext_workload_orchestration.aaz.latest.workload_orchestration.target._create import Create
from azext_workload_orchestration.aaz.latest.workload_orchestration.target._show import Show
from azext_workload_orchestration.aaz.latest.workload_orchestration.target._update import Update


class TargetLocationTest(unittest.TestCase):

    def setUp(self):
        self.cli_ctx = get_default_cli()
        self.resource_id = (
            "/subscriptions/00000000-0000-0000-0000-000000000000"
            "/resourceGroups/test-rg"
        )
        self.create_args = {
            "resource_group": "test-rg",
            "target_name": "test-target",
            "location": "eastus",
            "capabilities": ["test"],
            "context_id": self.resource_id + "/providers/Microsoft.Edge/contexts/test-context",
            "description": "Original description",
            "display_name": "Test target",
            "hierarchy_level": "line",
            "target_specification": {},
        }
        client_patch = mock.patch.object(AAZCommandCtx, "get_http_client")
        client_patch.start()
        self.addCleanup(client_patch.stop)

    def _parse_location(self, name, value):
        argument = getattr(Create.get_arguments_schema(), name).to_cmd_arg(name)
        parser = AzCliCommandParser(cli_ctx=self.cli_ctx)
        parser.add_argument(
            *argument.options_list,
            action=argument.options["action"],
            nargs=argument.options["nargs"],
        )
        return vars(parser.parse_args([argument.options_list[0], value]))

    def _context(self, command_type, arguments):
        context = AAZCommandCtx(
            self.cli_ctx, command_type.get_arguments_schema(), arguments
        )
        context.format_args()
        return context

    def _create_content(self, **arguments):
        context = self._context(Create, dict(self.create_args, **arguments))
        return Create.TargetsCreateOrUpdate(ctx=context).content

    def _machine_location(self, machine_type):
        provider = (
            "Microsoft.HybridCompute" if machine_type == "ArcMachine"
            else "Microsoft.Edge"
        )
        return {
            "name": self.resource_id + "/providers/" + provider + "/machines/test-machine",
            "type": machine_type,
        }

    def test_create_serializes_machine_location(self):
        for machine_type in ("ArcMachine", "EdgeMachine"):
            with self.subTest(machine_type=machine_type):
                location = self._machine_location(machine_type)
                arguments = self._parse_location("target_location", json.dumps(location))
                content = self._create_content(**arguments)

                self.assertEqual(content["properties"]["targetLocation"], location)
                self.assertNotIn("extendedLocation", content)

    def test_create_reads_target_location_from_json_file(self):
        location = self._machine_location("ArcMachine")
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "machine.json")
            with open(path, "w", encoding="utf-8") as machine_file:
                json.dump(location, machine_file)
            arguments = self._parse_location("target_location", "@" + path)
            content = self._create_content(**arguments)

        self.assertEqual(content["properties"]["targetLocation"], location)

    def test_create_rejects_incomplete_machine_location(self):
        for missing_field in ("name", "type"):
            with self.subTest(missing_field=missing_field):
                location = self._machine_location("ArcMachine")
                del location[missing_field]
                arguments = self._parse_location("target_location", json.dumps(location))

                with self.assertRaisesRegex(
                    InvalidArgumentValueError, "Missing required field: " + missing_field
                ):
                    self._create_content(**arguments)

    def test_create_rejects_unsupported_machine_type(self):
        location = self._machine_location("ArcMachine")
        location["type"] = "CustomLocation"

        with self.assertRaisesRegex(InvalidArgumentValueError, "unrecognized value"):
            self._parse_location("target_location", json.dumps(location))

    def test_create_preserves_extended_location_support(self):
        location = {
            "name": self.resource_id + "/providers/Microsoft.ExtendedLocation/customLocations/test-location",
            "type": "CustomLocation",
        }
        arguments = self._parse_location("extended_location", json.dumps(location))
        content = self._create_content(**arguments)

        self.assertEqual(content["extendedLocation"], location)
        self.assertNotIn("targetLocation", content["properties"])

    def test_show_returns_machine_location(self):
        for machine_type in ("ArcMachine", "EdgeMachine"):
            with self.subTest(machine_type=machine_type):
                location = self._machine_location(machine_type)
                resource = self._create_content()
                resource["properties"]["targetLocation"] = location
                command = Show(cli_ctx=self.cli_ctx)
                command.ctx = self._context(
                    Show, {"resource_group": "test-rg", "target_name": "test-target"}
                )
                command.ctx.set_var(
                    "instance", resource, schema_builder=Show.TargetsGet._build_schema_on_200
                )

                self.assertEqual(
                    command._output()["properties"]["targetLocation"], location
                )

    def test_update_preserves_machine_location(self):
        for machine_type in ("ArcMachine", "EdgeMachine"):
            with self.subTest(machine_type=machine_type):
                location = self._machine_location(machine_type)
                resource = self._create_content()
                resource["properties"]["targetLocation"] = location
                context = self._context(
                    Update,
                    {
                        "resource_group": "test-rg",
                        "target_name": "test-target",
                        "description": "Updated description",
                    },
                )
                context.set_var(
                    "instance", resource, schema_builder=Update.TargetsGet._build_schema_on_200
                )
                Update.InstanceUpdateByJson(ctx=context)()
                Update.InstanceUpdateByGeneric(ctx=context)()
                content = Update.TargetsCreateOrUpdate(ctx=context).content

                self.assertEqual(content["properties"]["targetLocation"], location)
                self.assertEqual(content["properties"]["description"], "Updated description")
