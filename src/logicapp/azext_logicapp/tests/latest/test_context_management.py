# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import copy
import errno
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from azure.cli.core import get_default_cli
from azure.cli.core.azclierror import (
    CLIError, InvalidArgumentValueError, MutuallyExclusiveArgumentError, RequiredArgumentMissingError,
    ResourceNotFoundError, ValidationError)
from azure.cli.core.util import user_confirmation

from azext_logicapp import COMMAND_LOADER_CLS, _context, _identity, _runtime_client, custom


UNSAFE_CLOUD_COORDINATES = (".", "..", "rg%2Fother", "rg%2fother", "app%5cother",
                            "rg%252fother", "app%3fquery", "app%23fragment", "app\u2028name")


class ContextManagementTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.store = self.root / "state" / "contexts.json"
        store_patch = patch.object(_context, "store_path", return_value=str(self.store))
        store_patch.start()
        self.addCleanup(store_patch.stop)
        self.cmd = SimpleNamespace(cli_ctx=get_default_cli())
        confirmation_patch = patch.object(_context, "user_confirmation")
        self.confirm = confirmation_patch.start()
        self.addCleanup(confirmation_patch.stop)
        failure = patch.object(custom, "build_runtime_client",
                               side_effect=AssertionError("Context CRUD contacted a runtime"))
        failure.start()
        self.addCleanup(failure.stop)

    def create(self, name="local", use=False):
        return custom.context_create(self.cmd, name, path=str(self.root / "project"), port=17071, use=use)

    def cloud(self, name="cloud", use=False):
        return custom.context_create(self.cmd, name, resource_group_name="rg", logic_app_name="app", use=use)

    def write(self, data):
        self.store.parent.mkdir(parents=True, exist_ok=True)
        self.store.write_text(json.dumps(data), encoding="utf-8")

    def original(self):
        return self.store.read_bytes()

    def test_missing_store_list_is_empty_and_inspection_creates_nothing(self):
        self.assertEqual([], custom.context_list(self.cmd))
        for name in (None, "missing"):
            with self.assertRaises(ResourceNotFoundError):
                custom.context_show(self.cmd, name)
        self.assertFalse(self.store.parent.exists())
        self.confirm.assert_not_called()

    def test_empty_existing_store_is_readonly_and_does_not_add_active_field(self):
        self.write({"contexts": {}})
        before = self.original()
        self.assertEqual([], custom.context_list(self.cmd))
        self.assertEqual(before, self.original())
        self.assertEqual(["contexts.json"], [item.name for item in self.store.parent.iterdir()])

    def test_sorted_list_named_show_and_active_show_share_original_shape(self):
        self.create("z-local", use=True)
        self.cloud("a-cloud")
        before = self.original()
        with patch.object(_context, "load_store", wraps=_context.load_store) as reader:
            result = custom.context_list(self.cmd)
        reader.assert_called_once()
        self.assertEqual(["a-cloud", "z-local"], [item["name"] for item in result])
        self.assertEqual([False, True], [item["active"] for item in result])
        self.assertEqual({"name", "active", "store", "target"}, set(result[0]))
        self.assertEqual(set(_context.TARGET_FIELDS), set(result[0]["target"]))
        self.assertEqual(result[1], custom.context_show(self.cmd))
        self.assertEqual(result[0], custom.context_show(self.cmd, "a-cloud"))
        self.assertEqual(before, self.original())
        self.assertEqual(["Name", "Active", "Kind", "Path", "Port", "ResourceGroup", "LogicAppName"],
                         list(_context.context_show_table_format(result[0])))

    def test_corrupt_storage_never_becomes_empty_or_is_rewritten(self):
        self.store.parent.mkdir()
        for text in ("{", "null", "[]", '{"contexts":{},"contexts":{}}',
                     '{"contexts":{},"extra":NaN}'):
            with self.subTest(text=text):
                self.store.write_text(text, encoding="utf-8")
                before = self.original()
                for operation in (
                        lambda: custom.context_list(self.cmd),
                        lambda: custom.context_show(self.cmd),
                        lambda: self.create(),
                        lambda: custom.context_use(self.cmd, "local"),
                        lambda: custom.context_update(self.cmd, "local", port=7079, yes=True),
                        lambda: custom.context_delete(self.cmd, "local", yes=True)):
                    with self.assertRaises(CLIError):
                        operation()
                    self.assertEqual(before, self.original())
        self.confirm.assert_not_called()

    def test_unreadable_store_errors_without_creating_lock(self):
        self.write({"contexts": {}})
        before = self.original()
        with patch("builtins.open", side_effect=PermissionError("private input")):
            with self.assertRaisesRegex(CLIError, "unreadable"):
                custom.context_list(self.cmd)
            with self.assertRaises(CLIError):
                self.create()
        self.assertEqual(before, self.original())
        self.assertFalse(Path(str(self.store) + ".lock").exists())

    def test_numeric_overflow_in_unknown_metadata_is_rejected_before_any_write(self):
        for number in ("1e9999", "-1e9999"):
            for location in ("store", "record", "target"):
                with self.subTest(number=number, location=location):
                    data = {"active": "local", "contexts": {"local": {
                        "name": "local", "target": {"kind": "local", "path": str(self.root), "port": 7071}}}}
                    selected = data if location == "store" else data["contexts"]["local"]
                    if location == "target":
                        selected = selected["target"]
                    selected["future"] = number
                    self.store.parent.mkdir(parents=True, exist_ok=True)
                    self.store.write_text(json.dumps(data).replace('"' + number + '"', number), encoding="utf-8")
                    before = self.original()
                    for operation in (
                            lambda: custom.context_list(self.cmd),
                            lambda: custom.context_show(self.cmd),
                            lambda: self.create(),
                            lambda: custom.context_use(self.cmd, "local"),
                            lambda: custom.context_update(self.cmd, "local", port=7079, yes=True),
                            lambda: custom.context_delete(self.cmd, "local", yes=True)):
                        with self.assertRaises(CLIError):
                            operation()
                        self.assertEqual(before, self.original())
                    self.assertFalse(Path(str(self.store) + ".lock").exists())
        self.confirm.assert_not_called()

    def test_deep_context_store_is_sanitized_without_writes_or_cwd_fallback(self):
        for depth in (_context._MAX_STORE_DEPTH + 1, 10000):
            with self.subTest(depth=depth):
                self.store.parent.mkdir(parents=True, exist_ok=True)
                self.store.write_text(
                    '{"contexts":{},"future":' + "[" * depth + '"private-author-value"' + "]" * depth + "}",
                    encoding="utf-8")
                before = self.original()
                for operation in (
                        lambda: custom.context_list(self.cmd),
                        lambda: self.create(),
                        lambda: custom._project_path_from_context(None, None)):
                    with self.assertRaises(CLIError) as caught:
                        operation()
                    self.assertNotIn("private-author-value", str(caught.exception))
                    self.assertEqual(before, self.original())
                self.assertFalse(Path(str(self.store) + ".lock").exists())
        self.confirm.assert_not_called()

    def test_save_rejects_nonfinite_metadata_before_creating_directory(self):
        for value in (float("inf"), float("-inf"), float("nan")):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                _context.save_store({"contexts": {}, "future": value}, expected={"contexts": {}})
        self.assertFalse(self.store.parent.exists())

    def test_finite_numeric_metadata_and_supported_depth_remain_preserved(self):
        nested = 1.25
        for _ in range(_context._MAX_STORE_DEPTH - 1):
            nested = [nested]
        self.write({"contexts": {}, "future": nested, "numbers": [1e308, -1e308, 1e-300]})
        before = self.original()
        self.assertEqual([], custom.context_list(self.cmd))
        self.assertEqual(before, self.original())
        self.create()
        after = _context.load_store()
        self.assertEqual(nested, after["future"])
        self.assertEqual([1e308, -1e308, 1e-300], after["numbers"])

    def test_directory_or_link_store_is_rejected(self):
        self.store.mkdir(parents=True)
        with self.assertRaises(CLIError):
            custom.context_list(self.cmd)
        self.store.rmdir()
        with patch.object(_context.os, "lstat", return_value=SimpleNamespace(st_mode=0o120777)):
            with self.assertRaises(CLIError):
                custom.context_list(self.cmd)

    def test_schema_record_name_active_version_and_target_types_are_validated(self):
        self.create()
        valid = _context.load_store()
        variants = [
            {"contexts": []}, {"contexts": {"local": None}},
            {"contexts": {"local": []}}, {"contexts": {"": valid["contexts"]["local"]}},
            {**valid, "version": 0}, {**valid, "version": 2}, {**valid, "version": True},
            {**valid, "version": "1"}, {**valid, "active": "missing"},
            {**valid, "active": []}, {**valid, "active": True},
        ]
        for record in (
                {"name": "wrong", "target": valid["contexts"]["local"]["target"]},
                {"name": "local", "target": None},
                {"name": "local", "target": {"kind": "future"}},
                {"name": "local", "target": {"kind": "cloud", "resourceGroup": "rg"}}):
            variants.append({"contexts": {"local": record}})
        local_target = valid["contexts"]["local"]["target"]
        for field, value in (("path", ""), ("path", "relative"), ("path", 7), ("path", "bad\n"),
                             ("port", True), ("port", "7071"), ("port", 0), ("port", 65536),
                             ("port", None), ("port", 7071.0), ("resourceGroup", "rg"),
                             ("logicAppName", "app"), ("kind", ["local"])):
            variants.append({"contexts": {"local": {"name": "local", "target": {**local_target, field: value}}}})
        for invalid in variants:
            with self.subTest(invalid=invalid):
                self.write(invalid)
                before = self.original()
                with self.assertRaisesRegex(CLIError, "schema"):
                    custom.context_list(self.cmd)
                self.assertEqual(before, self.original())

    def test_supported_explicit_version_and_unknown_metadata_survive_all_writers(self):
        self.create()
        self.cloud()
        data = _context.load_store()
        data.update({"version": 1, "future": {"nested": [1, None, True]}})
        data["contexts"]["local"]["future"] = {"opaque": "kept"}
        data["contexts"]["local"]["target"]["future"] = ["not-returned"]
        data["contexts"]["cloud"]["target"]["future"] = 12
        self.write(data)
        expected_metadata = copy.deepcopy(data)
        self.create()
        custom.context_use(self.cmd, "local")
        result = custom.context_update(self.cmd, "local", port=17079, yes=True)
        self.assertNotIn("future", json.dumps(result))
        after = _context.load_store()
        self.assertEqual(expected_metadata["future"], after["future"])
        self.assertEqual(expected_metadata["contexts"]["local"]["future"], after["contexts"]["local"]["future"])
        self.assertEqual(expected_metadata["contexts"]["local"]["target"]["future"],
                         after["contexts"]["local"]["target"]["future"])
        self.assertEqual(expected_metadata["contexts"]["cloud"], after["contexts"]["cloud"])
        custom.context_delete(self.cmd, "cloud", yes=True)
        final = _context.load_store()
        self.assertEqual(after["contexts"]["local"], final["contexts"]["local"])
        self.assertEqual(after["future"], final["future"])
        self.assertEqual(1, final["version"])

    def test_cloud_stored_coordinates_are_validated_without_exposing_values(self):
        self.cloud()
        valid = _context.load_store()
        target = valid["contexts"]["cloud"]["target"]
        for field, value in (("resourceGroup", None), ("resourceGroup", []), ("resourceGroup", ""),
                             ("resourceGroup", "rg/other"), ("logicAppName", ""),
                             ("logicAppName", "https://example"), ("logicAppName", "access_token=private"),
                             ("logicAppName", "app\nname"), ("path", "project"), ("port", 7071)):
            with self.subTest(field=field, value=value):
                self.write({"contexts": {"cloud": {"name": "cloud", "target": {**target, field: value}}}})
                before = self.original()
                with self.assertRaisesRegex(CLIError, "schema") as caught:
                    custom.context_show(self.cmd, "cloud")
                self.assertNotIn("private", str(caught.exception))
                self.assertEqual(before, self.original())

    def test_original_create_use_relative_path_and_cloud_default_port_behavior(self):
        created = custom.context_create(self.cmd, "dev", path="does-not-exist", use=True)
        self.assertEqual(os.path.abspath("does-not-exist"), created["target"]["path"])
        self.assertEqual(7071, created["target"]["port"])
        self.assertTrue(created["active"])
        self.assertEqual(created, custom.context_create(self.cmd, "dev", path="does-not-exist"))
        cloud = self.cloud()
        self.assertIsNone(cloud["target"]["port"])
        self.assertTrue(custom.context_use(self.cmd, "cloud")["active"])
        self.assertFalse(custom.context_show(self.cmd, "dev")["active"])

    def test_cloud_coordinate_mutations_refuse_encoded_and_dot_segments(self):
        self.cloud(use=True)
        before = self.original()
        for field in ("resource_group_name", "logic_app_name"):
            for value in UNSAFE_CLOUD_COORDINATES:
                for operation in ("create", "update"):
                    with self.subTest(field=field, value=value, operation=operation):
                        self.store.write_bytes(before)
                        arguments = {field: value}
                        with self.assertRaises(ValidationError):
                            if operation == "create":
                                arguments = {"resource_group_name": "rg", "logic_app_name": "app"}
                                arguments[field] = value
                                custom.context_create(self.cmd, "unsafe", **arguments)
                            else:
                                custom.context_update(self.cmd, "cloud", **arguments)
                        self.assertEqual(before, self.original())

    def test_cloud_coordinate_loading_refuses_unsafe_names_without_rewrite(self):
        self.cloud(use=True)
        valid = _context.load_store()
        for field in ("resourceGroup", "logicAppName"):
            for value in UNSAFE_CLOUD_COORDINATES:
                with self.subTest(field=field, value=value):
                    document = copy.deepcopy(valid)
                    document["contexts"]["cloud"]["target"][field] = value
                    self.write(document)
                    before = self.original()
                    with self.assertRaisesRegex(CLIError, "schema"):
                        custom.context_show(self.cmd, "cloud")
                    self.assertEqual(before, self.original())

    def test_cloud_arm_sinks_refuse_unsafe_coordinates_before_subscription_lookup(self):
        for field in ("resource_group_name", "name"):
            for value in UNSAFE_CLOUD_COORDINATES:
                for build in (_runtime_client._site_resource_id, _identity.site_url):
                    with self.subTest(field=field, value=value, build=build.__name__), \
                            patch("azure.cli.core.commands.client_factory.get_subscription_id") as subscription:
                        arguments = {"resource_group_name": "rg", "name": "app"}
                        arguments[field] = value
                        with self.assertRaises(ValidationError):
                            build(self.cmd, **arguments)
                        subscription.assert_not_called()
                site = "/subscriptions/sub/resourceGroups/{}/providers/Microsoft.Web/sites/{}".format(
                    value if field == "resource_group_name" else "rg", value if field == "name" else "app")
                with self.subTest(field=field, value=value, build="normalize"):
                    with self.assertRaises(InvalidArgumentValueError):
                        _runtime_client._normalize_site_resource_id(site)

    def test_cloud_literal_coordinate_paths_are_preserved(self):
        for group, app in (("rg.prod_1-(x)", "app-1"), ("rg with space", "app_2")):
            with self.subTest(group=group, app=app), \
                    patch("azure.cli.core.commands.client_factory.get_subscription_id", return_value="sub"):
                site = "/subscriptions/sub/resourceGroups/{}/providers/Microsoft.Web/sites/{}".format(group, app)
                self.assertEqual(site, _runtime_client._site_resource_id(self.cmd, group, app))
                self.assertEqual(site + "?api-version=" + _identity.SITE_API_VERSION,
                                 _identity.site_url(self.cmd, group, app))
                self.assertEqual(site, _runtime_client._normalize_site_resource_id(site))

    def test_runtime_site_targets_are_exact_roots_not_child_routes(self):
        site = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Web/sites/app"
        for value in (site + "/slots/other", site + "/hostruntime/path", site + "?query=injected",
                      site + "#fragment", site.replace("/rg/", "//"),
                      site.replace("Microsoft.Web", "Microsoft.Other")):
            with self.subTest(value=value):
                with self.assertRaises(CLIError):
                    _runtime_client._normalize_site_resource_id(value)
        self.assertEqual(site, _runtime_client._normalize_site_resource_id(site + "/"))

    def test_create_different_target_and_missing_use_are_not_upserts(self):
        self.create()
        before = self.original()
        with self.assertRaises(ValidationError):
            custom.context_create(self.cmd, "local", path="elsewhere")
        with self.assertRaises(ResourceNotFoundError):
            custom.context_use(self.cmd, "missing")
        self.assertEqual(before, self.original())

    def test_missing_show_update_delete_fail_without_state_or_confirmation(self):
        for operation in (
                lambda: custom.context_show(self.cmd, "missing"),
                lambda: custom.context_update(self.cmd, "missing", port=7079),
                lambda: custom.context_delete(self.cmd, "missing", yes=True)):
            with self.assertRaises(ResourceNotFoundError):
                operation()
        self.assertFalse(self.store.parent.exists())
        self.confirm.assert_not_called()

    def test_invalid_names_and_secret_shaped_inputs_never_write_or_echo_values(self):
        for name in ("", " padded ", "line\nbreak", 7, "Bearer fake-token"):
            with self.subTest(name=name):
                with self.assertRaises(ValidationError):
                    self.create(name)
        for kwargs in (
                {"path": ""}, {"path": 7}, {"path": "AccountKey=fake-value"},
                {"path": "x", "port": True}, {"path": "x", "port": 7071.5},
                {"resource_group_name": "rg", "logic_app_name": "https://example"},
                {"resource_group_name": "rg/app", "logic_app_name": "app"},
                {"resource_group_name": "rg", "logic_app_name": "password=fake-value"}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValidationError) as caught:
                    custom.context_create(self.cmd, "dev", **kwargs)
                self.assertNotIn("fake-value", str(caught.exception))
        self.assertFalse(self.store.parent.exists())

    def test_local_partial_update_preserves_path_other_records_and_active_selection(self):
        self.create()
        self.cloud(use=True)
        original = _context.load_store()
        result = custom.context_update(self.cmd, "local", port=17079)
        self.assertEqual("updated", result["action"])
        self.assertFalse(result["active"])
        self.assertEqual(original["contexts"]["local"]["target"]["path"], result["target"]["path"])
        self.assertEqual(original["contexts"]["cloud"], _context.load_store()["contexts"]["cloud"])
        self.assertEqual("cloud", _context.load_store()["active"])
        self.confirm.assert_not_called()

    def test_cloud_partial_update_preserves_other_coordinate(self):
        self.cloud()
        result = custom.context_update(self.cmd, "cloud", logic_app_name="new-app")
        self.assertEqual("rg", result["target"]["resourceGroup"])
        result = custom.context_update(self.cmd, "cloud", resource_group_name="new-rg")
        self.assertEqual("new-app", result["target"]["logicAppName"])
        self.assertIsNone(result["target"]["path"])
        self.assertIsNone(result["target"]["port"])

    def test_active_update_confirms_exact_target_without_switching_name(self):
        self.create(use=True)
        result = custom.context_update(self.cmd, "local", port=17079)
        self.assertTrue(result["active"])
        self.assertEqual("local", _context.load_store()["active"])
        self.confirm.assert_called_once()
        message = self.confirm.call_args.args[0]
        self.assertIn("active", message)
        self.assertIn("17079", message)
        self.assertIn("project", message)
        self.assertFalse(self.confirm.call_args.kwargs["yes"])

    def test_yes_is_passed_to_repository_confirmation_for_active_update_and_delete(self):
        self.create(use=True)
        custom.context_update(self.cmd, "local", port=17079, yes=True)
        self.assertTrue(self.confirm.call_args.kwargs["yes"])
        custom.context_delete(self.cmd, "local", yes=True)
        self.assertTrue(self.confirm.call_args.kwargs["yes"])

    def test_real_cli_confirmation_signature_supports_noninteractive_yes(self):
        self.create(use=True)
        with patch.object(_context, "user_confirmation", wraps=user_confirmation):
            updated = custom.context_update(self.cmd, "local", port=17079, yes=True)
            deleted = custom.context_delete(self.cmd, "local", yes=True)
        self.assertEqual("updated", updated["action"])
        self.assertEqual("deleted", deleted["action"])

    def test_noop_update_has_no_prompt_or_json_replacement(self):
        self.create(use=True)
        before = self.original()
        with patch.object(_context, "_publish_store", side_effect=AssertionError("no-op published")):
            result = custom.context_update(self.cmd, "local", port=17071)
        self.assertEqual("unchanged", result["action"])
        self.assertEqual(before, self.original())
        self.confirm.assert_not_called()

    def test_complete_explicit_transitions_clear_only_old_known_coordinates(self):
        self.create(use=True)
        data = _context.load_store()
        data["contexts"]["local"]["target"]["future"] = {"retain": 1}
        self.write(data)
        cloud = custom.context_update(self.cmd, "local", kind="cloud", resource_group_name="rg",
                                      logic_app_name="app", yes=True)
        self.assertEqual({"kind": "cloud", "path": None, "port": None,
                          "resourceGroup": "rg", "logicAppName": "app"}, cloud["target"])
        local = custom.context_update(self.cmd, "local", kind="local", path="new-project", port=17073, yes=True)
        self.assertEqual("local", local["target"]["kind"])
        self.assertEqual(17073, local["target"]["port"])
        self.assertEqual(os.path.abspath("new-project"), local["target"]["path"])
        self.assertIsNone(local["target"]["resourceGroup"])
        self.assertIsNone(local["target"]["logicAppName"])
        self.assertEqual({"retain": 1}, _context.load_store()["contexts"]["local"]["target"]["future"])
        self.assertEqual("local", _context.load_store()["active"])

    def test_invalid_partial_or_implicit_transitions_preserve_exact_store_bytes(self):
        self.create()
        self.cloud()
        before = self.original()
        cases = [
            ("local", {}), ("local", {"port": 0}), ("local", {"port": True}),
            ("local", {"port": "7071"}), ("local", {"path": ""}),
            ("local", {"kind": "future"}), ("local", {"kind": "cloud"}),
            ("local", {"kind": "cloud", "resource_group_name": "rg"}),
            ("local", {"resource_group_name": "rg", "logic_app_name": "app"}),
            ("local", {"path": "x", "resource_group_name": "rg"}),
            ("cloud", {"kind": "local", "path": "x"}),
            ("cloud", {"kind": "local", "port": 7071}),
            ("cloud", {"kind": "local", "path": "x", "port": None}),
            ("cloud", {"path": "x", "port": 7071}),
            ("cloud", {"logic_app_name": ""}), ("cloud", {"resource_group_name": None}),
        ]
        for name, kwargs in cases:
            with self.subTest(name=name, kwargs=kwargs):
                with self.assertRaises((ValidationError, RequiredArgumentMissingError, MutuallyExclusiveArgumentError)):
                    custom.context_update(self.cmd, name, **kwargs)
                self.assertEqual(before, self.original())
        self.confirm.assert_not_called()

    def test_declined_confirmation_preserves_bytes_for_update_and_delete(self):
        self.create(use=True)
        before = self.original()
        self.confirm.side_effect = CLIError("Operation cancelled.")
        for operation in (
                lambda: custom.context_update(self.cmd, "local", port=17079),
                lambda: custom.context_delete(self.cmd, "local")):
            with self.assertRaisesRegex(CLIError, "cancelled"):
                operation()
            self.assertEqual(before, self.original())

    def test_inactive_delete_preserves_active_and_never_touches_project(self):
        self.create()
        self.cloud(use=True)
        project = self.root / "project"
        project.mkdir()
        file = project / "keep.txt"
        file.write_text("keep")
        result = custom.context_delete(self.cmd, "local", yes=True)
        self.assertEqual("deleted", result["action"])
        self.assertFalse(result["active"])
        self.assertFalse(result["wasActive"])
        self.assertEqual("cloud", result["activeContext"])
        self.assertEqual("keep", file.read_text())
        self.assertEqual(["cloud"], list(_context.load_store()["contexts"]))

    def test_active_delete_clears_selection_without_substitute_and_runtime_requires_target(self):
        self.create(use=True)
        self.cloud()
        result = custom.context_delete(self.cmd, "local", yes=True)
        self.assertTrue(result["wasActive"])
        self.assertIsNone(result["activeContext"])
        self.assertIsNone(_context.load_store()["active"])
        with self.assertRaises(ResourceNotFoundError):
            custom.context_show(self.cmd)
        with self.assertRaises(RequiredArgumentMissingError):
            custom._client_from_target(self.cmd)
        self.assertEqual(os.path.abspath(os.curdir), custom._project_path_from_context(None, None))
        self.assertFalse(custom.context_show(self.cmd, "cloud")["active"])

    def test_last_active_delete_keeps_a_valid_empty_store(self):
        self.create(use=True)
        custom.context_delete(self.cmd, "local", yes=True)
        self.assertEqual({"active": None, "contexts": {}}, _context.load_store())
        self.assertEqual([], custom.context_list(self.cmd))

    def test_invalid_active_store_never_silently_falls_back_to_current_directory(self):
        self.write({"active": "missing", "contexts": {}})
        with self.assertRaises(CLIError):
            custom._project_path_from_context(None, None)
        self.assertEqual(str(self.root), custom._project_path_from_context(str(self.root), None))

    def test_save_requires_snapshot_and_validates_before_creating_directory(self):
        with self.assertRaises(ValidationError):
            _context.save_store({"active": None, "contexts": {}})
        with self.assertRaises(ValidationError):
            _context.save_store({"contexts": []}, expected={"contexts": {}})
        self.assertFalse(self.store.parent.exists())

    def test_changed_store_during_confirmation_is_not_overwritten(self):
        for operation in ("update", "delete"):
            with self.subTest(operation=operation):
                self.create(use=True)

                def change_store(*_args, **_kwargs):
                    data = _context.load_store()
                    data["future"] = operation
                    self.write(data)
                self.confirm.side_effect = change_store
                with self.assertRaisesRegex(CLIError, "changed"):
                    if operation == "update":
                        custom.context_update(self.cmd, "local", port=17079)
                    else:
                        custom.context_delete(self.cmd, "local")
                data = _context.load_store()
                self.assertEqual(operation, data["future"])
                self.assertEqual("local", data["active"])
                self.assertEqual(17071, data["contexts"]["local"]["target"]["port"])
                self.confirm.side_effect = None

    def test_all_writers_recheck_shared_snapshot_under_lock(self):
        self.create(use=True)
        self.cloud()
        for operation in (
                lambda: custom.context_create(self.cmd, "third", path="project"),
                lambda: custom.context_use(self.cmd, "cloud"),
                lambda: custom.context_update(self.cmd, "local", port=17079, yes=True),
                lambda: custom.context_delete(self.cmd, "cloud", yes=True)):
            with self.subTest(operation=operation):
                real_reader = _context.load_store
                snapshot = real_reader()
                calls = []

                def changed_reader():
                    calls.append(True)
                    if len(calls) == 1:
                        return copy.deepcopy(snapshot)
                    return {**snapshot, "future": "changed"}
                before = self.original()
                with patch.object(_context, "load_store", side_effect=changed_reader):
                    with self.assertRaisesRegex(CLIError, "changed"):
                        operation()
                self.assertEqual(before, self.original())

    def test_all_writers_reject_type_only_concurrent_metadata_changes(self):
        self.create(use=True)
        self.cloud()
        template = _context.load_store()
        real_reader = _context.load_store
        operations = (
            ("create", lambda: custom.context_create(self.cmd, "third", path="project")),
            ("unchanged-create", lambda: self.create()),
            ("use", lambda: custom.context_use(self.cmd, "cloud")),
            ("update", lambda: custom.context_update(self.cmd, "local", port=17079, yes=True)),
            ("delete", lambda: custom.context_delete(self.cmd, "cloud", yes=True)),
        )
        for label, operation in operations:
            for location in ("store", "record", "target"):
                for old, new in ((True, 1), (1, True), (1, 1.0), (1.0, 1)):
                    with self.subTest(operation=label, location=location,
                                      old_type=type(old), new_type=type(new)):
                        snapshot = copy.deepcopy(template)
                        selected = snapshot if location == "store" else snapshot["contexts"]["local"]
                        if location == "target":
                            selected = selected["target"]
                        selected["future"] = {"nested": [old]}
                        self.write(snapshot)
                        concurrent = copy.deepcopy(snapshot)
                        selected = concurrent if location == "store" else concurrent["contexts"]["local"]
                        if location == "target":
                            selected = selected["target"]
                        selected["future"]["nested"][0] = new
                        reads, concurrent_bytes = [], []

                        def changed_reader():
                            if reads:
                                self.write(concurrent)
                                concurrent_bytes.append(self.original())
                            reads.append(True)
                            return real_reader()

                        with patch.object(_context, "load_store", side_effect=changed_reader), \
                                patch.object(_context, "_publish_store") as publish:
                            with self.assertRaisesRegex(CLIError, "changed"):
                                operation()
                        publish.assert_not_called()
                        self.assertEqual(2, len(reads))
                        self.assertEqual(concurrent_bytes[0], self.original())

    def test_type_only_proposed_metadata_changes_are_published_not_noops(self):
        self.create()
        template = _context.load_store()
        for location in ("store", "record", "target"):
            for old, new in ((True, 1), (1, True), (1, 1.0), (1.0, 1)):
                with self.subTest(location=location, old_type=type(old), new_type=type(new)):
                    snapshot = copy.deepcopy(template)
                    selected = snapshot if location == "store" else snapshot["contexts"]["local"]
                    if location == "target":
                        selected = selected["target"]
                    selected["future"] = {"nested": [old]}
                    self.write(snapshot)
                    proposed = copy.deepcopy(snapshot)
                    selected = proposed if location == "store" else proposed["contexts"]["local"]
                    if location == "target":
                        selected = selected["target"]
                    selected["future"]["nested"][0] = new
                    with patch.object(_context, "_publish_store", wraps=_context._publish_store) as publish:
                        _context.save_store(proposed, expected=snapshot)
                    publish.assert_called_once()
                    observed = _context.load_store()
                    selected = observed if location == "store" else observed["contexts"]["local"]
                    if location == "target":
                        selected = selected["target"]
                    self.assertIs(type(new), type(selected["future"]["nested"][0]))
                    self.assertEqual(proposed, observed)

    def test_reordered_identical_snapshot_is_noop_without_replacing_bytes(self):
        self.create(use=True)
        snapshot = _context.load_store()
        snapshot["future"] = {"first": [True, 1, 1.0], "second": None}
        self.write(snapshot)
        before = self.original()
        proposed = dict(reversed(list(snapshot.items())))
        proposed["future"] = dict(reversed(list(snapshot["future"].items())))
        with patch.object(_context, "_publish_store") as publish:
            _context.save_store(proposed, expected=snapshot)
        publish.assert_not_called()
        self.assertEqual(before, self.original())

    def test_atomic_replace_failure_preserves_bytes_and_cleans_temporary_file(self):
        self.create()
        before = self.original()
        with patch.object(_context.os, "replace", side_effect=PermissionError("write blocked")):
            with self.assertRaisesRegex(CLIError, "previous store was not replaced"):
                custom.context_update(self.cmd, "local", port=17079)
        self.assertEqual(before, self.original())
        self.assertEqual([], list(self.store.parent.glob(".contexts-*.tmp")))

    def test_failed_publication_and_cleanup_keep_sanitized_preservation_error(self):
        self.create()
        before = self.original()
        with patch.object(_context.os, "replace", side_effect=PermissionError("PRIVATE-PUBLISH-REASON")), \
                patch.object(_context.os, "unlink", side_effect=PermissionError("PRIVATE-CLEANUP-REASON")):
            with self.assertRaisesRegex(CLIError, "previous store was not replaced") as caught:
                custom.context_update(self.cmd, "local", port=17079)
        self.assertIn("temporary", str(caught.exception).lower())
        self.assertNotIn("PRIVATE-", str(caught.exception))
        self.assertEqual(before, self.original())
        self.assertEqual(1, len(list(self.store.parent.glob(".contexts-*.tmp"))))

    def test_already_removed_publish_temporary_preserves_original_error(self):
        self.create()
        before = self.original()
        actual_unlink = os.unlink

        def remove_then_report_absent(path):
            actual_unlink(path)
            raise FileNotFoundError("PRIVATE-ALREADY-REMOVED")
        with patch.object(_context.os, "replace", side_effect=PermissionError("PRIVATE-PUBLISH-REASON")), \
                patch.object(_context.os, "unlink", side_effect=remove_then_report_absent):
            with self.assertRaisesRegex(CLIError, "previous store was not replaced") as caught:
                custom.context_update(self.cmd, "local", port=17079)
        self.assertNotIn("PRIVATE-", str(caught.exception))
        self.assertEqual(before, self.original())
        self.assertEqual([], list(self.store.parent.glob(".contexts-*.tmp")))

    def test_successful_publication_never_unlinks_replacement(self):
        self.create()
        with patch.object(_context.os, "unlink", side_effect=PermissionError("Must not remove published data")) as unlink:
            result = custom.context_update(self.cmd, "local", port=17079)
        self.assertEqual(17079, result["target"]["port"])
        unlink.assert_not_called()

    def test_publish_uses_same_directory_flush_then_atomic_replace(self):
        self.create()
        before = self.original()
        actual_replace = os.replace
        observed = []

        def replace(source, destination):
            self.assertEqual(self.store.parent, Path(source).parent)
            self.assertEqual(self.store, Path(destination))
            self.assertEqual(before, self.original())
            payload = json.loads(Path(source).read_text(encoding="utf-8"))
            self.assertEqual(17079, payload["contexts"]["local"]["target"]["port"])
            observed.append(True)
            actual_replace(source, destination)
        with patch.object(_context.os, "replace", side_effect=replace), \
                patch.object(_context.os, "fsync", wraps=os.fsync) as sync:
            custom.context_update(self.cmd, "local", port=17079)
        self.assertEqual([True], observed)
        sync.assert_called_once()

    def test_busy_lock_has_bounded_explicit_failure_and_preserves_store(self):
        self.create()
        before = self.original()
        with patch.object(_context, "_lock_file", side_effect=OSError(errno.EACCES, "locked")), \
                patch.object(_context.time, "monotonic", side_effect=[0, 6]):
            with self.assertRaisesRegex(CLIError, "busy"):
                custom.context_update(self.cmd, "local", port=17079)
        self.assertEqual(before, self.original())

    def test_unexpected_lock_error_is_not_retried_or_published(self):
        self.create()
        before = self.original()
        with patch.object(_context, "_lock_file", side_effect=OSError(errno.EIO, "failed")) as lock:
            with self.assertRaisesRegex(CLIError, "Could not lock"):
                custom.context_update(self.cmd, "local", port=17079)
        lock.assert_called_once()
        self.assertEqual(before, self.original())

    def test_native_lock_blocks_an_independent_process_without_lost_update(self):
        self.create()
        script = (
            "from azext_logicapp import _context\n"
            "import json,sys\n"
            "_context.store_path=lambda:sys.argv[1]\n"
            "_context.LOCK_TIMEOUT=0.1\n"
            "try:\n"
            " _context.use_context('local')\n"
            "except _context.CLIError as error:\n"
            " print(str(error)); sys.exit(3)\n"
            "sys.exit(0)\n"
        )
        before = self.original()
        with _context._store_lock(str(self.store)):
            completed = subprocess.run([sys.executable, "-c", script, str(self.store)],
                                       capture_output=True, text=True, timeout=20, check=False)
        self.assertEqual(3, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("busy", completed.stdout)
        self.assertEqual(before, self.original())
        self.assertTrue(custom.context_use(self.cmd, "local")["active"])

    def test_actual_saved_local_and_cloud_records_route_existing_consumers(self):
        self.create(use=True)
        self.cloud()
        with patch.object(custom, "build_runtime_client", return_value=object()) as builder:
            custom._client_from_target(self.cmd)
            self.assertEqual({"local": True, "port": 17071, "host_key": None}, builder.call_args.kwargs)
            custom._client_from_target(self.cmd, context="cloud")
            self.assertEqual({"resource_group_name": "rg", "name": "app", "host_key": None},
                             builder.call_args.kwargs)
            self.assertEqual(str(self.root / "project"), custom._project_path_from_context(None, "local"))
            custom.context_use(self.cmd, "cloud")
            custom._client_from_target(self.cmd)
            self.assertEqual("app", builder.call_args.kwargs["name"])
        self.assertEqual("cloud", _context.load_store()["active"])

    def test_named_and_active_local_contexts_accept_ephemeral_host_keys(self):
        self.create(use=True)
        before = self.original()
        with patch.object(custom, "build_runtime_client", side_effect=_runtime_client.build_runtime_client), \
                patch.object(_runtime_client, "_site_resource_id", side_effect=AssertionError("No cloud lookup")):
            for name in (None, "local"):
                with self.subTest(context=name):
                    client, target = custom._client_from_target(self.cmd, context=name, host_key="ephemeral-key")
                    self.assertTrue(client.is_local)
                    self.assertEqual("http://localhost:17071", client.site_resource_id)
                    self.assertEqual("ephemeral-key", client.host_key)
                    self.assertEqual("local", target["kind"])
        self.assertEqual(before, self.original())
        self.assertNotIn(b"ephemeral-key", self.original())

    def test_cloud_or_missing_context_rejects_host_key_and_active_port_stays_gated(self):
        self.create(use=True)
        self.cloud()
        with patch.object(custom, "build_runtime_client", side_effect=_runtime_client.build_runtime_client), \
                patch.object(_runtime_client, "_site_resource_id", side_effect=AssertionError("No cloud lookup")):
            with self.assertRaises(RequiredArgumentMissingError):
                custom._client_from_target(self.cmd, port=17079, host_key="ephemeral-key")
            for name in (None, "cloud"):
                if name is None:
                    custom.context_use(self.cmd, "cloud")
                with self.subTest(context=name), self.assertRaises(RequiredArgumentMissingError):
                    custom._client_from_target(self.cmd, context=name, host_key="ephemeral-key")
            custom.context_delete(self.cmd, "cloud", yes=True)
            with self.assertRaises(RequiredArgumentMissingError):
                custom._client_from_target(self.cmd, host_key="ephemeral-key")

    def test_context_commands_registration_flags_do_not_shadow_app_name(self):
        for suffix in ("list", "show", "update", "delete"):
            name = "logicapp context " + suffix
            cli = get_default_cli()
            cli.invocation = SimpleNamespace(data={"command_string": name})
            loader = COMMAND_LOADER_CLS(cli_ctx=cli)
            self.assertIn(name, loader.load_command_table([]))
            loader.load_arguments([])
            arguments = loader.argument_registry.arguments[name]
            if suffix == "list":
                self.assertFalse(set(arguments) & {"name", "yes", "path", "port"})
                continue
            self.assertEqual(["--name"], arguments["name"].settings["options_list"])
            if suffix == "show":
                self.assertFalse(arguments["name"].settings.get("required", False))
            else:
                self.assertTrue(arguments["name"].settings["required"])
                self.assertEqual(["--yes", "-y"], arguments["yes"].settings["options_list"])
            if suffix == "update":
                self.assertEqual(["--logic-app-name"], arguments["logic_app_name"].settings["options_list"])
                self.assertIsNone(arguments["port"].settings.get("default"))


if __name__ == "__main__":
    unittest.main()
