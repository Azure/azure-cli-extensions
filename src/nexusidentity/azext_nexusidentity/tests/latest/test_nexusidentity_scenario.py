# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""Record and replay Graph key publication without requiring FIDO2 hardware."""

import os
import subprocess
import tempfile
from unittest.mock import patch

from azure.cli.testsdk import ScenarioTest

from azext_nexusidentity import custom


class NexusIdentityScenarioTest(ScenarioTest):
    """Exercise real Graph requests with simulated local key generation."""

    def test_nexusidentity_key_publication(self):
        self.kwargs.update(
            graph_resource="https://graph.microsoft.com",
            extensions_url="https://graph.microsoft.com/v1.0/me/extensions",
            extension_url=(
                "https://graph.microsoft.com/v1.0/me/extensions/"
                "com.nexusidentity.keys"
            ),
        )
        while True:
            extensions = self.cmd(
                "az rest --method get --resource {graph_resource} "
                "--url {extensions_url}"
            ).get_output_in_json()
            self.assertFalse(
                any(
                    extension.get("id") == "com.nexusidentity.keys"
                    for extension in extensions["value"]
                ),
                "Use an approved test account without an existing "
                "com.nexusidentity.keys extension; existing keys will not be replaced.",
            )
            next_link = extensions.get("@odata.nextLink")
            if not next_link:
                break
            self.kwargs["extensions_url"] = next_link

        expanduser = os.path.expanduser
        run = subprocess.run
        with tempfile.TemporaryDirectory() as key_directory:

            def isolated_home(path):
                if path in ("~/.ssh", "~\\.ssh"):
                    return key_directory
                return expanduser(path)

            def run_local_command(command, **kwargs):
                if command[0] == "ssh-keygen":
                    self.assertEqual(command[-2], "-f")
                    self.assertEqual(os.path.dirname(command[-1]), key_directory)
                    algorithm = command[command.index("-t") + 1]
                    with open(command[-1] + ".pub", "w", encoding="utf-8") as key_file:
                        key_file.write(f"nexusidentity-test-{algorithm}-public-key\n")
                    return subprocess.CompletedProcess(command, 0)
                self.assertEqual(
                    command[1:],
                    [
                        "account",
                        "get-access-token",
                        "--resource",
                        "https://graph.microsoft.com",
                        "--output",
                        "json",
                    ],
                )
                if self.is_live:
                    return run(command, **kwargs)
                return subprocess.CompletedProcess(
                    command, 0, stdout='{"accessToken": "playback-token"}'
                )

            with patch(
                "azure.cli.core.extension.DEV_EXTENSION_SOURCES",
                [os.path.dirname(os.path.dirname(os.path.abspath(custom.__file__)))],
            ), patch.object(
                custom, "get_windows_ssh_keygen_path", return_value="ssh-keygen"
            ), patch.object(
                custom.os.path, "expanduser", side_effect=isolated_home
            ), patch.object(
                custom.subprocess, "run", side_effect=run_local_command
            ):
                for index, (arguments, algorithm) in enumerate(
                    (
                        ("", "ed25519-sk"),
                        (" --algorithm ecdsa-sk", "ecdsa-sk"),
                        (" --algorithm ed25519-sk", "ed25519-sk"),
                    )
                ):
                    self.cmd("az nexusidentity gen-keys" + arguments)
                    if index == 0:
                        self.addCleanup(
                            self.cmd,
                            "az rest --method delete --resource {graph_resource} "
                            "--url {extension_url}",
                        )
                    self.cmd(
                        "az rest --method get --resource {graph_resource} "
                        "--url {extension_url}",
                        checks=self.check(
                            "publicKey",
                            f"nexusidentity-test-{algorithm}-public-key\n",
                        ),
                    )
