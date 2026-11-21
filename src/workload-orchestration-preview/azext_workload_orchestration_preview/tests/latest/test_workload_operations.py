# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from types import SimpleNamespace
import unittest
from unittest import mock

from azext_workload_orchestration_preview.aaz.latest.workload_orchestration.context import (
    _create as context_create_module,
)
from azext_workload_orchestration_preview.aaz.latest.workload_orchestration.context._create import (
    Create as ContextCreate,
)


class ContextCreateCompatibilityTest(unittest.TestCase):

    @staticmethod
    def _create_case(capabilities_marker):
        data = {
            "context_name": "ctx",
            "resource_group": "rg",
            "location": "eastus",
            "hierarchies": [{"name": "country", "description": "Country"}],
        }
        if capabilities_marker is not None:
            data["capabilities"] = capabilities_marker

        schema = ContextCreate._build_arguments_schema()
        args = schema._ValueCls(schema, schema.process_data(data))
        ctx = SimpleNamespace(args=args, get_http_client=mock.Mock())
        command = object.__new__(ContextCreate)
        command.callbacks = {}
        command.ctx = ctx
        operation = ContextCreate.ContextsCreateOrUpdate(ctx=ctx)
        return command, operation

    def test_omitted_capabilities_use_current_api_without_warning(self):
        command, operation = self._create_case(None)

        with mock.patch.object(context_create_module.logger, "warning") as warning:
            command.pre_operations()

        self.assertEqual(operation.query_parameters, {"api-version": "2026-06-01"})
        self.assertEqual(operation.content["properties"]["capabilities"], [])
        warning.assert_not_called()

    def test_empty_capabilities_use_current_api_with_warning(self):
        command, operation = self._create_case([])

        with mock.patch.object(context_create_module.logger, "warning") as warning:
            command.pre_operations()

        self.assertEqual(operation.query_parameters, {"api-version": "2026-06-01"})
        self.assertEqual(operation.content["properties"]["capabilities"], [])
        warning.assert_called_once()

    def test_non_empty_capabilities_use_legacy_api_with_warning(self):
        capabilities = [{"name": "cap", "description": "Cap"}]
        command, operation = self._create_case(capabilities)

        with mock.patch.object(context_create_module.logger, "warning") as warning:
            command.pre_operations()

        self.assertEqual(operation.query_parameters, {"api-version": "2025-08-01"})
        self.assertEqual(operation.content["properties"]["capabilities"], capabilities)
        warning.assert_called_once()