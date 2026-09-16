# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import pytest
from azure.cli.testsdk import ScenarioTest

pytestmark = pytest.mark.azdev

HELP_COMMANDS = (
    ("apr",),
    ("apr", "registry"),
    ("apr", "registry", "create"),
    ("apr", "registry", "delete"),
    ("apr", "registry", "list"),
    ("apr", "registry", "show"),
    ("apr", "registry", "update"),
    ("apr", "repository"),
    ("apr", "repository", "create"),
    ("apr", "repository", "delete"),
    ("apr", "repository", "list"),
    ("apr", "repository", "publish"),
    ("apr", "repository", "show"),
    ("apr", "repository", "sync"),
    ("apr", "repository", "update"),
    ("apr", "repository", "release"),
    ("apr", "repository", "release", "create"),
    ("apr", "repository", "release", "delete"),
    ("apr", "repository", "release", "list"),
    ("apr", "repository", "release", "component"),
    ("apr", "repository", "release", "component", "create"),
    ("apr", "repository", "release", "component", "delete"),
    ("apr", "repository", "release", "component", "list"),
    ("apr", "repository", "package"),
    ("apr", "repository", "package", "add"),
    ("apr", "repository", "package", "remove"),
    ("apr", "package"),
    ("apr", "package", "upload"),
    ("apr", "package", "deb"),
    ("apr", "package", "deb", "list"),
    ("apr", "package", "deb", "show"),
    ("apr", "package", "debsrc"),
    ("apr", "package", "debsrc", "list"),
    ("apr", "package", "debsrc", "show"),
    ("apr", "package", "rpm"),
    ("apr", "package", "rpm", "list"),
    ("apr", "package", "rpm", "show"),
    ("apr", "package", "file"),
    ("apr", "package", "file", "list"),
    ("apr", "package", "file", "show"),
    ("apr", "distro"),
    ("apr", "distro", "create"),
    ("apr", "distro", "delete"),
    ("apr", "distro", "list"),
    ("apr", "distro", "show"),
    ("apr", "distro", "update"),
    ("apr", "remote"),
    ("apr", "remote", "create"),
    ("apr", "remote", "delete"),
    ("apr", "remote", "list"),
    ("apr", "remote", "show"),
    ("apr", "remote", "update"),
    ("apr", "publication"),
    ("apr", "publication", "delete"),
    ("apr", "publication", "list"),
    ("apr", "publication", "show"),
    ("apr", "task"),
    ("apr", "task", "cancel"),
    ("apr", "task", "list"),
    ("apr", "task", "show"),
    ("apr", "task", "wait"),
)

REQUIRED_ARGUMENT_COMMANDS = (
    ("apr", "repository", "show"),
    ("apr", "package", "upload"),
    ("apr", "task", "wait"),
)


class AprCommandScenarioTest(ScenarioTest):
    def _assert_help_loads(self, command: tuple[str, ...]) -> None:
        with self.assertRaises(SystemExit) as raised:
            self.cli_ctx.invoke([*command, "--help"])

        self.assertEqual(raised.exception.code, 0)

    def test_extension_command_surface_loads(self) -> None:
        for command in HELP_COMMANDS:
            with self.subTest(command=" ".join(command)):
                self._assert_help_loads(command)

    def test_representative_commands_validate_required_arguments(self) -> None:
        for command in REQUIRED_ARGUMENT_COMMANDS:
            with self.subTest(command=" ".join(command)):
                with self.assertRaises(SystemExit) as raised:
                    self.cli_ctx.invoke(list(command))

                self.assertEqual(raised.exception.code, 2)
