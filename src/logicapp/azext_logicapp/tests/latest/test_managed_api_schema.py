# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import copy
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from azure.cli.core.azclierror import HTTPError, InvalidArgumentValueError, ResourceNotFoundError, ValidationError

from azext_logicapp import _help, _managed_api, custom
from azext_logicapp._params import load_arguments


class _FakeCmd:
    cli_ctx = object()


class _FakeResponse:
    status_code = 200

    def __init__(self, content):
        self.content = content


class _ArgumentContext:
    def __init__(self, loader, command):
        self.loader = loader
        self.command = command

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def argument(self, name, **kwargs):
        self.loader.arguments[(self.command, name)] = kwargs


class _ArgumentLoader:
    def __init__(self):
        self.arguments = {}

    def argument_context(self, command):
        return _ArgumentContext(self, command)


class ManagedConnectorInputSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture_path = Path(__file__).parent / "fixtures" / "managed_connector_weather.swagger.json"
        with fixture_path.open(encoding="utf-8") as fixture:
            cls.swagger = json.load(fixture)

    def _show(self, swagger=None, include_input_schema=True, metadata=None):
        calls = []
        swagger = self.swagger if swagger is None else swagger
        if metadata is None:
            metadata = {"name": "CurrentWeather", "properties": {"summary": "Get current weather"}}

        def sender(_ctx, method, url, **_kwargs):
            calls.append((method, url))
            if url.endswith("export=true"):
                return _FakeResponse(json.dumps(swagger).encode("utf-8"))
            return _FakeResponse(json.dumps(metadata).encode("utf-8"))

        result = _managed_api.connector_managed_operation_show(
            _FakeCmd(), "msnweather", "CurrentWeather", location="eastus", subscription="sub1",
            sender=sender, include_input_schema=include_input_schema)
        return result, calls

    def test_opt_in_exports_and_preserves_input_schema_metadata(self):
        result, calls = self._show()

        schema = result["inputSchema"]
        self.assertEqual(2, len(calls))
        self.assertIn(
            "/managedApis/msnweather/apiOperations/CurrentWeather?api-version=2018-07-01-preview",
            calls[0][1])
        self.assertIn("/managedApis/msnweather?api-version=2018-07-01-preview&export=true", calls[1][1])
        self.assertEqual("CurrentWeather", schema["operationId"])
        self.assertEqual("/current", schema["path"])
        self.assertEqual("get", schema["method"])
        self.assertEqual("#/parameters/region", schema["pathParameters"][0]["$ref"])
        self.assertEqual("location", schema["operationParameters"][0]["name"])
        self.assertEqual("C", schema["operationParameters"][1]["default"])
        self.assertIn("WeatherResponse", schema["definitions"])
        self.assertEqual("region", schema["parameterDefinitions"]["region"]["name"])
        self.assertFalse(schema["dynamicMetadata"]["resolved"])
        self.assertEqual(
            ["x-ms-dynamic-values"],
            [extension["name"] for extension in schema["dynamicMetadata"]["extensions"]])
        self.assertFalse(schema["references"]["resolved"])
        self.assertEqual(
            ["https://schemas.example.test/weather.json#/definitions/Condition"],
            schema["references"]["external"])
        self.assertEqual(
            "https://schemas.example.test/weather.json#/definitions/Condition",
            schema["definitions"]["WeatherResponse"]["properties"]["condition"]["$ref"])

    def test_default_operation_show_does_not_fetch_swagger_or_change_shape(self):
        result, calls = self._show(include_input_schema=False)

        self.assertEqual(1, len(calls))
        self.assertNotIn("inputSchema", result)

    def test_opt_in_rejects_invalid_metadata_before_fetching_export(self):
        contents = (
            b"[]", b"null", b'"metadata"', b"false", b"not json", b"", b"\xff",
            b'{"name":"CurrentWeather","name":"CurrentWeather"}',
            b'{"name":"CurrentWeather","properties":{"value":1,"value":2}}',
            b'{"name":"CurrentWeather","value":NaN}',
            b'{"name":"CurrentWeather","value":Infinity}',
            b'{"name":"CurrentWeather","value":-Infinity}',
            b'{"name":"CurrentWeather","value":1e309}',
        )
        for content in contents:
            with self.subTest(content=content):
                sender = mock.Mock(return_value=_FakeResponse(content))

                with self.assertRaises(ValidationError):
                    _managed_api.connector_managed_operation_show(
                        _FakeCmd(), "msnweather", "CurrentWeather", location="eastus",
                        subscription="sub1", sender=sender, include_input_schema=True)

                sender.assert_called_once()

    def test_default_nonobject_and_malformed_metadata_behavior_is_preserved(self):
        for content, expected in ((b"[]", []), (b"null", None), (b"not json", {})):
            with self.subTest(content=content):
                sender = mock.Mock(return_value=_FakeResponse(content))

                result = _managed_api.connector_managed_operation_show(
                    _FakeCmd(), "msnweather", "CurrentWeather", location="eastus",
                    subscription="sub1", sender=sender)

                if isinstance(expected, dict):
                    expected = {
                        "connector": "/subscriptions/sub1/providers/Microsoft.Web/locations/"
                                     "eastus/managedApis/msnweather",
                        "operation": "CurrentWeather",
                    }
                self.assertEqual(expected, result)
                sender.assert_called_once()

    def test_schema_export_flag_is_an_explicit_cli_opt_in(self):
        loader = _ArgumentLoader()
        load_arguments(loader, None)

        argument = loader.arguments[("logicapp connector managed operation show", "include_input_schema")]
        self.assertEqual(["--include-input-schema"], argument["options_list"])
        self.assertEqual("store_true", argument["action"])

    def test_command_help_documents_schema_and_resolution_boundaries(self):
        help_text = _help.helps["logicapp connector managed operation show"]

        self.assertIn("--include-input-schema", help_text)
        self.assertIn("External references are never fetched", help_text)
        self.assertIn("dynamic metadata is preserved but not resolved", help_text)

    def test_command_forwards_schema_opt_in(self):
        cmd = _FakeCmd()
        with mock.patch.object(_managed_api, "connector_managed_operation_show") as show:
            custom.connector_managed_operation_show(
                cmd, "msnweather", "CurrentWeather", location="eastus", include_input_schema=True)

        show.assert_called_once_with(
            cmd, "msnweather", "CurrentWeather", location="eastus", include_input_schema=True)

    def test_duplicate_operation_ids_are_rejected(self):
        swagger = copy.deepcopy(self.swagger)
        swagger["x-ms-paths"] = {
            "/current?region={region}": {
                "get": {"operationId": "CurrentWeather", "parameters": []}
            }
        }

        with self.assertRaisesRegex(InvalidArgumentValueError, "ambiguous"):
            self._show(swagger)

    def test_api_operation_swagger_id_selects_the_exported_operation(self):
        metadata = {
            "name": "catalog-name",
            "properties": {"swaggerOperationId": "CurrentWeather"},
        }

        result, _ = self._show(metadata=metadata)

        self.assertEqual("CurrentWeather", result["inputSchema"]["operationId"])

    def test_missing_operation_id_is_not_silently_substituted(self):
        with self.assertRaisesRegex(ResourceNotFoundError, "was not found"):
            self._show({"swagger": "2.0", "paths": {}})

    def test_api_metadata_without_an_operation_id_is_rejected(self):
        with self.assertRaisesRegex(ValidationError, "no operation name or swaggerOperationId"):
            self._show(metadata={})

    def test_unresolved_path_item_references_are_not_followed(self):
        swagger = {
            "swagger": "2.0",
            "paths": {"/weather": {"$ref": "https://schemas.example.test/weather.json#/paths/~1current"}},
        }

        with self.assertRaisesRegex(ValidationError, "without following unresolved path-item references"):
            self._show(swagger)

    def test_selected_path_item_reference_blocks_inline_matching_operation(self):
        for reference in (
                "https://schemas.example.test/weather.json#/paths/~1current",
                "#/paths/~1shared", "", None):
            with self.subTest(reference=reference):
                swagger = copy.deepcopy(self.swagger)
                swagger["paths"]["/current"]["$ref"] = reference

                with self.assertRaisesRegex(ValidationError, "selected path item.*unresolved"):
                    self._show(swagger)

    def test_missing_paths_object_is_rejected_as_malformed(self):
        with self.assertRaisesRegex(ValidationError, "paths object"):
            self._show({"swagger": "2.0"})

    def test_malformed_or_unsupported_export_is_rejected(self):
        fixture_json = json.dumps(self.swagger).encode("utf-8")
        ambiguous_exports = tuple(
            fixture_json[:-1] + addition + b"}"
            for addition in (
                b',"swagger":"2.0"', b',"value":NaN', b',"value":Infinity',
                b',"value":-Infinity', b',"value":1e309',
            )
        )
        for content in (b"not json", b"", b"[]", b"null", b"\xff") + ambiguous_exports:
            with self.subTest(content=content):
                def sender(_ctx, _method, url, **_kwargs):
                    if url.endswith("export=true"):
                        return _FakeResponse(content)
                    return _FakeResponse(b'{"name":"CurrentWeather"}')

                with self.assertRaises(ValidationError):
                    _managed_api.connector_managed_operation_show(
                        _FakeCmd(), "msnweather", "CurrentWeather", location="eastus",
                        subscription="sub1", sender=sender, include_input_schema=True)

        with self.assertRaisesRegex(ValidationError, "Swagger 2.0"):
            self._show({"openapi": "3.0.0", "paths": {}})

    def test_invalid_operation_parameters_are_rejected(self):
        swagger = copy.deepcopy(self.swagger)
        swagger["paths"]["/current"]["get"]["parameters"] = {}

        with self.assertRaisesRegex(ValidationError, "arrays"):
            self._show(swagger)

    def test_authentication_and_http_errors_are_not_hidden(self):
        error = HTTPError(
            "authorization failed",
            response=SimpleNamespace(
                status_code=403,
                content=b'{"error":{"code":"AuthorizationFailed","message":"denied"}}'))

        def sender(_ctx, _method, url, **_kwargs):
            if url.endswith("export=true"):
                raise error
            return _FakeResponse(b'{"name":"CurrentWeather"}')

        with self.assertRaises(HTTPError) as raised:
            _managed_api.connector_managed_operation_show(
                _FakeCmd(), "msnweather", "CurrentWeather", location="eastus",
                subscription="sub1", sender=sender, include_input_schema=True)
        self.assertIs(error, raised.exception)

