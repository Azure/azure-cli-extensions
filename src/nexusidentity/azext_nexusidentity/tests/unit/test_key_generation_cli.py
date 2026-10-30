# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Offline Nexus Identity SSH key generation CLI unit tests.
"""

import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import Mock, call, patch

from azure.cli.core.mock import DummyCli

from azext_nexusidentity import custom


class TestKeyGenerationCLI(unittest.TestCase):
    """Exercise CLI dispatch without hardware, credentials, or Graph access."""

    def test_key_generation_command_dispatch(self):
        cli = DummyCli()
        public_key = "test-public-key"
        user = Mock()
        user.json.return_value = {"mail": "user@example.invalid"}
        extensions = Mock()
        extensions.json.return_value = {"value": []}
        expanduser = os.path.expanduser

        with tempfile.TemporaryDirectory() as key_directory:
            for key_name in ("id_ed25519_sk", "id_ecdsa_sk"):
                with open(
                    os.path.join(key_directory, key_name + ".pub"),
                    "w",
                    encoding="utf-8",
                ) as key_file:
                    key_file.write(public_key)

            def isolated_home(path):
                if path in ("~/.ssh", "~\\.ssh"):
                    return key_directory
                return expanduser(path)

            with patch(
                "azure.cli.core.extension.DEV_EXTENSION_SOURCES",
                [os.path.dirname(os.path.dirname(os.path.abspath(custom.__file__)))],
            ), patch.object(
                custom, "get_windows_ssh_keygen_path", return_value="ssh-keygen"
            ), patch.object(
                custom.os.path, "expanduser", side_effect=isolated_home
            ), patch.object(
                custom.subprocess,
                "run",
                return_value=subprocess.CompletedProcess(
                    [], 0, stdout='{"accessToken": "test-token"}'
                ),
            ) as run, patch(
                "shutil.which", return_value="az"
            ), patch(
                "requests.get"
            ) as get, patch(
                "requests.post"
            ) as post, patch(
                "requests.patch"
            ) as update:
                for arguments, algorithm, key_name in (
                    ((), "ed25519-sk", "id_ed25519_sk"),
                    (("--algorithm", "ecdsa-sk"), "ecdsa-sk", "id_ecdsa_sk"),
                    (("--algorithm", "ed25519-sk"), "ed25519-sk", "id_ed25519_sk"),
                ):
                    with self.subTest(algorithm=arguments or "default"):
                        run.reset_mock()
                        get.reset_mock()
                        post.reset_mock()
                        get.side_effect = [user, extensions]

                        output = StringIO()
                        with redirect_stdout(output):
                            exit_code = cli.invoke(
                                ["nexusidentity", "gen-keys", *arguments],
                                out_file=output,
                            )
                        self.assertEqual(exit_code, 0, output.getvalue())
                        self.assertIn(
                            "Successfully uploaded public key", output.getvalue()
                        )

                        self.assertEqual(
                            run.call_args_list,
                            [
                                call(
                                    [
                                        "ssh-keygen",
                                        "-t",
                                        algorithm,
                                        "-O",
                                        "resident",
                                        "-O",
                                        "verify-required",
                                        "-C",
                                        "NexusIdentitySSHKey",
                                        "-f",
                                        os.path.join(key_directory, key_name),
                                    ],
                                    check=True,
                                    shell=False,
                                ),
                                call(
                                    [
                                        "az",
                                        "account",
                                        "get-access-token",
                                        "--resource",
                                        "https://graph.microsoft.com",
                                        "--output",
                                        "json",
                                    ],
                                    capture_output=True,
                                    text=True,
                                    check=True,
                                ),
                            ],
                        )
                        self.assertEqual(
                            [request.args[0] for request in get.call_args_list],
                            [
                                "https://graph.microsoft.com/v1.0/me",
                                "https://graph.microsoft.com/v1.0/me/extensions",
                            ],
                        )
                        post.assert_called_once()
                        self.assertEqual(
                            post.call_args.args[0],
                            "https://graph.microsoft.com/v1.0/me/extensions",
                        )
                        self.assertEqual(
                            json.loads(post.call_args.kwargs["data"])["publicKey"],
                            public_key,
                        )
                        update.assert_not_called()
