# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_load.data_plane.utils import validators
from azure.cli.core.commands import CliCommandType

admin_custom_sdk = CliCommandType(
    operations_tmpl="azext_load.data_plane.load_test.custom#{}"
)


def load_test_commands(self, _):
    with self.command_group(
        "load test", custom_command_type=admin_custom_sdk, is_preview=True
    ) as g:
        g.custom_command("create", "create_test")
        g.custom_command("update", "update_test")
        g.custom_command("delete", "delete_test", confirmation=True)
        g.custom_command("list", "list_tests")
        g.custom_show_command("show", "get_test")
        g.custom_command(
            "download-files",
            "download_test_files",
            validator=validators.validate_download,
        )

    with self.command_group(
        "load test app-component",
        custom_command_type=admin_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("add", "add_test_app_component")
        g.custom_command("list", "list_test_app_component")
        g.custom_command("remove", "remove_test_app_component", confirmation=True)

    with self.command_group(
        "load test server-metric",
        custom_command_type=admin_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("list", "list_test_server_metric")
        g.custom_command("add", "add_test_server_metric")
        g.custom_command("remove", "remove_test_server_metric", confirmation=True)

    with self.command_group(
        "load test file",
        custom_command_type=admin_custom_sdk,
        is_preview=True,
    ) as g:
        g.custom_command("upload", "upload_test_file", supports_no_wait=True)
        g.custom_command("list", "list_test_file")
        g.custom_command("delete", "delete_test_file", confirmation=True)
        g.custom_command(
            "download", "download_test_file", validator=validators.validate_download
        )
