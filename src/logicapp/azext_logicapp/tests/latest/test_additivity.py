# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from __future__ import annotations

import logging
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from azure.cli.core import get_default_cli
from azure.cli.core.commands import ExtensionCommandSource
from azure.cli.testsdk import ScenarioTest

import azure.cli.command_modules.appservice as appservice
from azext_logicapp import COMMAND_LOADER_CLS


PINNED_GA_LOGICAPP_COMMANDS = {
    "logicapp create",
    "logicapp delete",
    "logicapp list",
    "logicapp restart",
    "logicapp scale",
    "logicapp show",
    "logicapp start",
    "logicapp stop",
    "logicapp update",
    "logicapp config appsettings list",
    "logicapp config appsettings set",
    "logicapp config appsettings delete",
    "logicapp deployment source config-zip",
}

REQUIRED_EXTENSION_COMMANDS = {
    "logicapp test create",
    "logicapp test plan",
    "logicapp test run",
    "logicapp test results show",
    "logicapp context create",
    "logicapp context use",
    "logicapp context list",
    "logicapp context show",
    "logicapp context update",
    "logicapp context delete",
    "logicapp run wait",
    "logicapp run cancel",
    "logicapp run resubmit",
    "logicapp trigger history resubmit",
    "logicapp connection managed create",
    "logicapp workflow list",
    "logicapp workflow show",
    "logicapp workflow export",
    "logicapp workflow set",
    "logicapp workflow delete",
    "logicapp workflow enable",
    "logicapp workflow disable",
    "logicapp runtime doctor",
    "logicapp deployment package",
    "logicapp connector managed list",
    "logicapp connector managed show",
    "logicapp connector managed operation list",
    "logicapp connector managed operation show",
    "logicapp connection list",
    "logicapp connection show",
    "logicapp connection test",
    "logicapp connection create",
    "logicapp connection delete",
    "logicapp connection acl list",
    "logicapp connection acl show",
    "logicapp connection acl add",
    "logicapp connection acl remove",
}


def _extension_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_cli_command_table():
    cli = get_default_cli()
    invoker = cli.invocation_cls(cli_ctx=cli, commands_loader_cls=cli.commands_loader_cls)
    # A fresh CLI index only knows the core group. Load the complete catalog
    # rather than depending on a prior extension invocation warming that index.
    command_table = invoker.commands_loader.load_command_table(args=[])
    return invoker, command_table


def _core_logicapp_commands(invoker, command_table):
    core_commands = set()
    for name in command_table:
        if not name.startswith("logicapp"):
            continue
        owners = invoker.commands_loader.cmd_to_loader_map.get(name, ())
        if any(isinstance(owner, appservice.COMMAND_LOADER_CLS) for owner in owners):
            core_commands.add(name)
    return core_commands


def _extension_loader_surface():
    loader = COMMAND_LOADER_CLS(cli_ctx=get_default_cli())
    command_table = loader.load_command_table(args=[])
    return set(command_table), set(loader.command_group_table)


def _az_help_text(*args: str, environment=None) -> str:
    completed = subprocess.run(
        [sys.executable, "-m", "azure.cli", *args, "--help"],
        env=environment, capture_output=True, text=True, timeout=60, check=False)
    if completed.returncode != 0:
        raise AssertionError("az {} --help failed with {}\nSTDOUT:\n{}\nSTDERR:\n{}".format(
            " ".join(args), completed.returncode, completed.stdout, completed.stderr))
    return completed.stdout


def _stock_help_text(*args: str) -> str:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for name in ("config", "extensions", "system-extensions"):
            (root / name).mkdir()
        environment = dict(
            os.environ,
            AZURE_CONFIG_DIR=str(root / "config"),
            AZURE_EXTENSION_DIR=str(root / "extensions"),
            AZURE_EXTENSION_SYS_DIR=str(root / "system-extensions"),
            AZURE_EXTENSION_USE_DYNAMIC_INSTALL="no",
            AZURE_CORE_COLLECT_TELEMETRY="0",
            AZURE_CORE_CHECK_VERSION="0",
        )
        environment.pop("PYTHONPATH", None)
        return _az_help_text(*args, environment=environment)


def _help_group_summary(help_text: str, command: str) -> str:
    match = re.search(r"^\s+az {}\s+:\s+(.+)$".format(re.escape(command)), help_text, flags=re.MULTILINE)
    if not match:
        raise AssertionError("loaded help missing group summary for az {}\n{}".format(command, help_text))
    return match.group(1).strip()


class _CaptureWarnings:
    def __enter__(self):
        self.records = []
        self.logger = logging.getLogger("azure.cli.core.commands")
        self.old_level = self.logger.level
        self.logger.setLevel(logging.WARNING)
        handler = logging.Handler()
        handler.emit = self.records.append
        self.handler = handler
        self.logger.addHandler(handler)
        return self.records

    def __exit__(self, exc_type, exc, tb):
        self.logger.removeHandler(self.handler)
        self.logger.setLevel(self.old_level)
        return False


class LogicAppAdditivityTests(ScenarioTest):
    def test_ga_logicapp_commands_remain_loaded_with_extension(self):
        invoker, command_table = _load_cli_command_table()
        missing_core = sorted(PINNED_GA_LOGICAPP_COMMANDS - set(command_table))
        self.assertEqual([], missing_core, "GA logicapp commands disappeared from the loaded command table")
        self.assertEqual(PINNED_GA_LOGICAPP_COMMANDS, _core_logicapp_commands(invoker, command_table))

        missing_extension = sorted(REQUIRED_EXTENSION_COMMANDS - set(command_table))
        self.assertEqual([], missing_extension, "logicapp extension is not loaded in the command table")

    def test_extension_source_never_declares_bare_logicapp_group(self):
        commands_py = _extension_root() / "azext_logicapp" / "commands.py"
        source = commands_py.read_text(encoding="utf-8")
        bare_group = re.compile(r"\.command_group\(\s*(['\"])logicapp\1\s*(?:,|\))")
        self.assertIsNone(bare_group.search(source), "extension commands.py must not declare self.command_group('logicapp')")

    def test_deployment_core_and_extension_leaves_both_resolve(self):
        _, command_table = _load_cli_command_table()
        self.assertIn("logicapp deployment source config-zip", command_table)
        self.assertIn("logicapp deployment package", command_table)

    def test_core_group_help_summary_is_unchanged(self):
        logicapp_help = _az_help_text("logicapp")
        deployment_help = _az_help_text("logicapp", "deployment")
        self.assertEqual(
            _help_group_summary(_stock_help_text("logicapp"), "logicapp"),
            _help_group_summary(logicapp_help, "logicapp"),
        )
        self.assertEqual(
            _help_group_summary(_stock_help_text("logicapp", "deployment"), "logicapp deployment"),
            _help_group_summary(deployment_help, "logicapp deployment"),
        )

    def test_no_collision_override_warning_for_logicapp_commands(self):
        invoker, command_table = _load_cli_command_table()
        logicapp_command_names = sorted(name for name in command_table if name.startswith("logicapp"))
        self.assertIn("logicapp deployment package", logicapp_command_names)

        with _CaptureWarnings() as records:
            for name in logicapp_command_names:
                invoker._resolve_extension_override_warning(command_table[name])  # pylint: disable=protected-access

        messages = [record.getMessage() for record in records]
        self.assertEqual([], messages, "logicapp command-table collision warning(s) emitted")

        overridden = sorted(
            name for name in logicapp_command_names
            if isinstance(command_table[name].command_source, ExtensionCommandSource)
            and command_table[name].command_source.overrides_command
        )
        self.assertEqual([], overridden, "logicapp extension command(s) override core commands")

    def test_complete_extension_surface_is_preserved(self):
        commands, _ = _extension_loader_surface()
        self.assertEqual(59, len(commands))
        self.assertTrue(REQUIRED_EXTENSION_COMMANDS.issubset(commands))
        self.assertTrue(PINNED_GA_LOGICAPP_COMMANDS.isdisjoint(commands))

    def test_repeatable_arguments_actually_accumulate(self):
        # nargs='+' alone makes a repeated flag overwrite the earlier occurrence,
        # so 'connection create --parameter a=1 --parameter b=2' silently wrote a
        # single parameter and exited zero. The behavioural tests call the
        # implementation directly and cannot see the declaration, so guard the
        # declaration itself: every flag documented as repeatable needs
        # action='append' alongside nargs='+'.
        # Maps command -> {argument: expected nargs}. Two correct shapes exist:
        # action='append' with nargs='+' (space-separated values also allowed) and
        # action='append' alone (one value per occurrence). What is never correct is
        # nargs='+' without action='append'.
        expected = {
            "logicapp connection create": {"parameter": "+", "app_setting": "+"},
            "logicapp connection managed create": {"parameter": "+"},
            "logicapp identity assign": {"user_assigned": "+"},
            "logicapp identity remove": {"user_assigned": "+"},
            "logicapp dependency check": {"kind": None},
            "logicapp dependency install": {"kind": None},
            "logicapp dependency uninstall": {"kind": None},
        }
        invoker, command_table = _load_cli_command_table()
        loader = invoker.commands_loader
        invoker.cli_ctx.invocation = invoker

        for command_name, arg_specs in expected.items():
            self.assertIn(command_name, command_table)
            invoker.data["command_string"] = command_name
            loader.load_arguments(command_name)
            arguments = command_table[command_name].arguments
            for arg_name, expected_nargs in arg_specs.items():
                self.assertIn(arg_name, arguments, "{} lost argument {}".format(command_name, arg_name))
                options = arguments[arg_name].options
                self.assertEqual(
                    "append", options.get("action"),
                    "{} --{} is repeatable but drops all but the last occurrence".format(
                        command_name, arg_name.replace("_", "-")))
                self.assertEqual(expected_nargs, options.get("nargs"))


if __name__ == "__main__":
    unittest.main()
