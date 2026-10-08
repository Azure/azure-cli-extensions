# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import asyncio
import shlex
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

from azext_aks_preview.bastion import bastion as commands
from azext_aks_preview.bastion.bastion import (
    BastionResource,
    _aks_bastion_launch_tunnel,
    aks_bastion_parse_bastion_resource,
)
from azext_aks_preview.custom import aks_bastion_tunnel
from azure.cli.core.azclierror import CLIInternalError


class TestAksBastionParseResource(unittest.TestCase):
    def test_cross_subscription_resource_id_preserves_bastion_subscription(self):
        # the bastion lives in a different (hub) subscription than the cluster
        bastion_id = (
            "/subscriptions/hub-sub-id/resourceGroups/bastion-rg/"
            "providers/Microsoft.Network/bastionHosts/my-bastion"
        )
        resource = aks_bastion_parse_bastion_resource(
            bastion_id, ["node-rg"], subscription_id="aks-sub-id"
        )
        self.assertEqual(resource.name, "my-bastion")
        self.assertEqual(resource.resource_group, "bastion-rg")
        # the subscription from the bastion resource ID must win over the cluster subscription
        self.assertEqual(resource.subscription, "hub-sub-id")

    def test_resource_id_without_subscription_falls_back_to_cluster_subscription(self):
        # parse_resource_id may not yield a subscription; fall back to the cluster one
        bastion_id = (
            "/subscriptions/hub-sub-id/resourceGroups/bastion-rg/"
            "providers/Microsoft.Network/bastionHosts/my-bastion"
        )
        with patch(
            "azext_aks_preview.bastion.bastion.parse_resource_id",
            return_value={"name": "my-bastion", "resource_group": "bastion-rg"},
        ):
            resource = aks_bastion_parse_bastion_resource(
                bastion_id,
                ["node-rg"],
                subscription_id="aks-sub-id",
            )
        self.assertEqual(resource.subscription, "aks-sub-id")


class TestAksBastionLaunchTunnel(unittest.IsolatedAsyncioTestCase):
    async def test_tunnel_uses_bastion_subscription(self):
        # regression guard: the inner `az network bastion tunnel` must be scoped to the
        # bastion's subscription, not the cluster subscription (see azure-cli#33579)
        bastion_resource = BastionResource(
            name="my-bastion",
            resource_group="bastion-rg",
            subscription="hub-sub-id",
        )
        mock_process = MagicMock()
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.returncode = 0

        with patch(
            "azext_aks_preview.bastion.bastion.asyncio.create_subprocess_exec",
            new=AsyncMock(return_value=mock_process),
        ) as mock_exec, patch.object(
            commands, "_aks_bastion_get_az_cmd_name", return_value="/installed tools/az"
        ):
            await _aks_bastion_launch_tunnel(
                bastion_resource,
                port=12345,
                mc_id="/subscriptions/aks-sub-id/resourceGroups/aks-rg/"
                "providers/Microsoft.ContainerService/managedClusters/cluster",
                subscription_id="aks-sub-id",
            )

        args = mock_exec.call_args.args
        self.assertEqual(args[0], "/installed tools/az")
        self.assertIn("--subscription", args)
        sub_index = args.index("--subscription")
        self.assertEqual(args[sub_index + 1], "hub-sub-id")
        self.assertNotIn("aks-sub-id", args[sub_index + 1])

    async def test_tunnel_falls_back_to_cluster_subscription(self):
        # when the bastion has no subscription of its own (name-based discovery in the
        # node resource group), the cluster subscription is used
        bastion_resource = BastionResource(
            name="my-bastion",
            resource_group="node-rg",
            subscription=None,
        )
        mock_process = MagicMock()
        mock_process.wait = AsyncMock(return_value=0)
        mock_process.returncode = 0

        with patch(
            "azext_aks_preview.bastion.bastion.asyncio.create_subprocess_exec",
            new=AsyncMock(return_value=mock_process),
        ) as mock_exec, patch.object(
            commands, "_aks_bastion_get_az_cmd_name", return_value="/installed tools/az"
        ):
            await _aks_bastion_launch_tunnel(
                bastion_resource,
                port=12345,
                mc_id="/subscriptions/aks-sub-id/resourceGroups/aks-rg/"
                "providers/Microsoft.ContainerService/managedClusters/cluster",
                subscription_id="aks-sub-id",
            )

        args = mock_exec.call_args.args
        self.assertEqual(args[0], "/installed tools/az")
        self.assertIn("--subscription", args)
        sub_index = args.index("--subscription")
        self.assertEqual(args[sub_index + 1], "aks-sub-id")


class TestBastionExecutablePaths(unittest.TestCase):
    def test_powershell_returns_selected_path_and_preserves_preference(self):
        pwsh = r"C:\Program Files\PowerShell\7\pwsh.exe"
        powershell = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
        for results, expected, calls in (
            ([pwsh], pwsh, [call("pwsh")]),
            ([None, powershell], powershell, [call("pwsh"), call("powershell")]),
            ([None, None], None, [call("pwsh"), call("powershell")]),
        ):
            with self.subTest(results=results), patch.object(commands, "which", side_effect=results) as resolve:
                self.assertEqual(commands._get_powershell_executable_from_path(), expected)
                self.assertEqual(resolve.call_args_list, calls)

    def test_powershell_parent_executable_fallback_is_preserved(self):
        parent = MagicMock()
        parent.exe.return_value = r"C:\Custom Tools\pwsh.exe"
        with patch.object(commands, "_get_powershell_executable_from_path", return_value=None):
            self.assertEqual(commands._get_powershell_executable(parent), parent.exe.return_value)
            self.assertEqual(
                commands._handle_powershell_parent(parent.exe.return_value, "pwsh.exe"),
                parent.exe.return_value,
            )

    def test_windows_shell_commands_keep_quoted_absolute_executables(self):
        for executable, expected in (
            (r"C:\Program Files\PowerShell\7\pwsh.exe", '-NoExit -Command'),
            (r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", '-NoExit -Command'),
            (r"C:\Windows\System32\cmd.exe", '/k'),
        ):
            with self.subTest(executable=executable), patch.object(
                commands, "_aks_bastion_get_current_shell_cmd", return_value=executable
            ), patch.object(commands, "which", return_value=executable), patch.object(
                commands.sys, "platform", "win32"
            ):
                shell, command = commands._aks_bastion_prepare_shell_cmd(r"C:\test config\config")
                self.assertEqual(shell, executable)
                self.assertTrue(command.startswith(f'"{executable}" {expected}'))
                self.assertIn(r"C:\test config\config", command)

    def test_posix_powershell_command_does_not_expand_environment_in_outer_shell(self):
        executable = "/installed tools/pwsh"
        kubeconfig = "/test config/user's config"
        with patch.object(
            commands, "_aks_bastion_get_current_shell_cmd", return_value="pwsh"
        ), patch.object(commands, "which", return_value=executable), patch.object(
            commands.sys, "platform", "linux"
        ):
            shell, command = commands._aks_bastion_prepare_shell_cmd(kubeconfig)
        self.assertEqual(shell, executable)
        self.assertEqual(
            shlex.split(command),
            [executable, "-NoExit", "-Command", "$env:KUBECONFIG='/test config/user''s config'"],
        )

    def test_bash_rcfile_preserves_absolute_executable_and_quoting(self):
        executable = "/installed tools/bash"
        with patch.object(
            commands, "_aks_bastion_get_current_shell_cmd", return_value="bash"
        ), patch.object(commands, "which", return_value=executable), patch.object(
            commands.os.path, "exists", return_value=True
        ), patch.object(commands.sys, "platform", "linux"):
            shell, command = commands._aks_bastion_prepare_shell_cmd("/test config/user's config")
        self.assertEqual(shell, executable)
        arguments = shlex.split(command)
        self.assertEqual(arguments[:2], [executable, "-c"])
        self.assertTrue(arguments[2].startswith(shlex.quote(executable) + " --rcfile"))

    def test_bash_without_rcfile_launches_selected_shell_directly(self):
        executable = "/installed tools/bash"
        with patch.object(
            commands, "_aks_bastion_get_current_shell_cmd", return_value="bash"
        ), patch.object(commands, "which", return_value=executable), patch.object(
            commands.os.path, "exists", return_value=False
        ), patch.object(commands.sys, "platform", "linux"):
            shell, command = commands._aks_bastion_prepare_shell_cmd("test-kubeconfig")
        self.assertEqual(shell, executable)
        self.assertEqual(shlex.split(command), [executable])

    def test_missing_shell_fails_instead_of_executing_bare_name(self):
        with patch.object(commands, "_aks_bastion_get_current_shell_cmd", return_value="pwsh"), patch.object(
            commands, "which", return_value=None
        ):
            with self.assertRaisesRegex(CLIInternalError, "shell executable"):
                commands._aks_bastion_prepare_shell_cmd("test-kubeconfig")

    def test_azure_cli_is_resolved_for_each_platform(self):
        for platform, name in (("win32", "az.cmd"), ("linux", "az")):
            with self.subTest(platform=platform), patch.object(commands.sys, "platform", platform), patch.object(
                commands, "which", return_value="/installed tools/" + name
            ) as resolve:
                self.assertEqual(commands._aks_bastion_get_az_cmd_name(), "/installed tools/" + name)
                resolve.assert_called_once_with(name)

    def test_missing_azure_cli_fails_instead_of_executing_bare_name(self):
        with patch.object(commands, "which", return_value=None):
            with self.assertRaisesRegex(CLIInternalError, "Azure CLI executable"):
                commands._aks_bastion_get_az_cmd_name()

    def test_windows_process_cleanup_uses_resolved_taskkill(self):
        process = MagicMock(pid=12345)
        executable = r"C:\Windows\System32\taskkill.exe"
        with patch.object(commands.sys, "platform", "win32"), patch.object(
            commands, "which", return_value=executable
        ) as resolve, patch.object(commands.subprocess, "run") as run:
            commands._aks_bastion_kill_process_tree(process)
        resolve.assert_called_once_with("taskkill.exe")
        run.assert_called_once_with(
            [executable, "/T", "/F", "/PID", "12345"], capture_output=True, check=False
        )
        process.terminate.assert_not_called()

    def test_missing_taskkill_warns_and_uses_process_handle(self):
        process = MagicMock(pid=12345)
        with patch.object(commands.sys, "platform", "win32"), patch.object(
            commands, "which", return_value=None
        ), patch.object(commands.subprocess, "run") as run, patch.object(commands.logger, "warning") as warning:
            commands._aks_bastion_kill_process_tree(process)
        run.assert_not_called()
        process.terminate.assert_called_once()
        warning.assert_called_once()


class TestBastionSubprocessPaths(unittest.IsolatedAsyncioTestCase):
    async def test_windows_subshell_pins_outer_command_processor(self):
        process = MagicMock()
        process.wait = AsyncMock()
        command_processor = r"C:\Windows\System32\cmd.exe"
        with patch.object(commands, "_aks_bastion_validate_tunnel", return_value=True), patch.object(
            commands, "_aks_bastion_prepare_shell_cmd", return_value=("pwsh.exe", '"selected pwsh.exe" -NoExit')
        ), patch.object(commands.sys, "platform", "win32"), patch.object(
            commands, "which", return_value=command_processor
        ) as resolve, patch.object(
            commands.asyncio.subprocess, "create_subprocess_shell", return_value=process
        ) as run:
            await commands._aks_bastion_launch_subshell("test-kubeconfig", 12345)
        resolve.assert_called_once_with("cmd.exe")
        self.assertEqual(run.call_args.kwargs["executable"], command_processor)
        self.assertEqual(run.call_args.kwargs["env"]["KUBECONFIG"], "test-kubeconfig")
        self.assertEqual(run.call_args.kwargs["cmd"], '"selected pwsh.exe" -NoExit')
        self.assertTrue(run.call_args.kwargs["shell"])

    async def test_missing_windows_command_processor_fails_before_launch(self):
        with patch.object(commands, "_aks_bastion_validate_tunnel", return_value=True), patch.object(
            commands, "_aks_bastion_prepare_shell_cmd", return_value=("pwsh.exe", '"selected pwsh.exe" -NoExit')
        ), patch.object(commands.sys, "platform", "win32"), patch.object(
            commands, "which", return_value=None
        ), patch.object(commands.asyncio.subprocess, "create_subprocess_shell") as run:
            with self.assertRaisesRegex(CLIInternalError, "command processor executable"):
                await commands._aks_bastion_launch_subshell("test-kubeconfig", 12345)
        run.assert_not_called()

    async def test_posix_subshell_preserves_inherited_streams_and_environment(self):
        process = MagicMock()
        process.wait = AsyncMock()
        with patch.object(commands, "_aks_bastion_validate_tunnel", return_value=True), patch.object(
            commands, "_aks_bastion_prepare_shell_cmd", return_value=("/bin/bash", "/bin/bash")
        ), patch.object(commands.sys, "platform", "linux"), patch.object(
            commands, "which"
        ) as resolve, patch.object(
            commands.asyncio.subprocess, "create_subprocess_shell", return_value=process
        ) as run:
            await commands._aks_bastion_launch_subshell("test-kubeconfig", 12345)
        resolve.assert_not_called()
        self.assertIsNone(run.call_args.kwargs["executable"])
        for stream in ("stdin", "stdout", "stderr"):
            self.assertIsNone(run.call_args.kwargs[stream])
        self.assertEqual(run.call_args.kwargs["env"]["KUBECONFIG"], "test-kubeconfig")

    async def test_test_hook_uses_explicit_path_and_argument_list(self):
        process = MagicMock(returncode=0)
        process.wait = AsyncMock()
        executable = "/installed tools/kubectl"
        with patch.object(commands, "_aks_bastion_validate_tunnel", return_value=True), patch.object(
            commands, "which", return_value=executable
        ) as resolve, patch.object(commands.asyncio, "create_subprocess_exec", return_value=process) as run:
            await commands._aks_bastion_test_hook("/test config/config", 12345, executable)
        resolve.assert_called_once_with(executable)
        self.assertEqual(
            run.call_args.args, (executable, "--kubeconfig", "/test config/config", "get", "nodes")
        )
        self.assertFalse(run.call_args.kwargs["shell"])

    async def test_missing_test_hook_executable_fails_before_launch(self):
        with patch.object(commands, "_aks_bastion_validate_tunnel", return_value=True), patch.object(
            commands, "which", return_value=None
        ), patch.object(commands.asyncio, "create_subprocess_exec") as run:
            with self.assertRaisesRegex(CLIInternalError, "kubectl executable"):
                await commands._aks_bastion_test_hook("test-kubeconfig", 12345, "/missing/kubectl")
        run.assert_not_called()

    async def test_runner_propagates_failures_after_cancelling_other_task(self):
        cancelled = asyncio.Event()

        async def wait_for_cancellation(*args):
            try:
                await asyncio.Event().wait()
            finally:
                cancelled.set()

        with patch.object(
            commands, "_aks_bastion_launch_tunnel", side_effect=CLIInternalError("executable not found")
        ), patch.object(
            commands, "_aks_bastion_launch_subshell", side_effect=wait_for_cancellation
        ):
            with self.assertRaisesRegex(CLIInternalError, "executable not found"):
                await commands.aks_bastion_runner(
                    BastionResource("bastion", "rg"), 12345, "test-cluster-id", "test-kubeconfig"
                )
        self.assertTrue(cancelled.is_set())

    async def test_runner_propagates_nonzero_tunnel_exit_after_cancelling_subshell(self):
        for returncode in (1, 17, -15):
            with self.subTest(returncode=returncode):
                started = asyncio.Event()
                cancelled = asyncio.Event()
                process = MagicMock(returncode=returncode)

                async def wait_for_exit():
                    await started.wait()
                    return returncode

                process.wait = AsyncMock(side_effect=wait_for_exit)

                async def wait_for_cancellation(*args):
                    try:
                        started.set()
                        await asyncio.Event().wait()
                    finally:
                        cancelled.set()

                with patch.object(
                    commands, "_aks_bastion_get_az_cmd_name", return_value="/installed tools/az"
                ), patch.object(
                    commands.asyncio, "create_subprocess_exec", return_value=process
                ), patch.object(
                    commands, "_aks_bastion_launch_subshell", side_effect=wait_for_cancellation
                ):
                    with self.assertRaisesRegex(CLIInternalError, f"Bastion tunnel exited with code {returncode}"):
                        await commands.aks_bastion_runner(
                            BastionResource("bastion", "rg"), 12345, "test-cluster-id", "test-kubeconfig"
                        )
                process.wait.assert_awaited_once()
                self.assertTrue(cancelled.is_set())

    async def test_runner_cancels_tunnel_normally_when_subshell_exits(self):
        started = asyncio.Event()
        process = MagicMock(returncode=-15)

        async def wait_for_exit():
            if process.wait.await_count == 1:
                started.set()
                await asyncio.Event().wait()
            return process.returncode

        process.wait = AsyncMock(side_effect=wait_for_exit)

        async def exit_subshell(*args):
            await started.wait()

        with patch.object(
            commands, "_aks_bastion_get_az_cmd_name", return_value="/installed tools/az"
        ), patch.object(
            commands.asyncio, "create_subprocess_exec", return_value=process
        ), patch.object(
            commands, "_aks_bastion_launch_subshell", side_effect=exit_subshell
        ), patch.object(commands, "_aks_bastion_kill_process_tree") as kill_tree:
            await commands.aks_bastion_runner(
                BastionResource("bastion", "rg"), 12345, "test-cluster-id", "test-kubeconfig"
            )
        kill_tree.assert_called_once_with(process)
        self.assertEqual(process.wait.await_count, 2)


class TestAksBastionTunnel(unittest.TestCase):
    def _run_tunnel(self, bastion_profile, bastion=None):
        cmd = SimpleNamespace(cli_ctx=MagicMock())
        client = MagicMock()
        client.get.return_value = SimpleNamespace(
            id="cluster-id",
            node_resource_group="node-rg",
            network_profile=SimpleNamespace(bastion_profile=bastion_profile),
        )
        bastion_resource = BastionResource("bastion", "bastion-rg", "sub-id")

        with patch("azext_aks_preview.custom.aks_bastion_extension"), patch(
            "azext_aks_preview.custom.os.path.exists", return_value=True
        ), patch(
            "azext_aks_preview.custom.get_subscription_id", return_value="sub-id"
        ), patch(
            "azext_aks_preview.custom.aks_bastion_parse_bastion_resource",
            return_value=bastion_resource,
        ) as mock_parse, patch(
            "azext_aks_preview.custom.aks_bastion_get_local_port", return_value=12345
        ), patch(
            "azext_aks_preview.custom.aks_bastion_set_kubeconfig"
        ), patch(
            "azext_aks_preview.custom.aks_bastion_runner", new=AsyncMock()
        ), patch(
            "azext_aks_preview.custom.aks_batsion_clean_up"
        ):
            aks_bastion_tunnel(
                cmd,
                client,
                "rg",
                "cluster",
                bastion=bastion,
                kubeconfig_path="/tmp/kubeconfig",
            )

        return mock_parse

    def test_uses_enabled_managed_bastion_by_default(self):
        mock_parse = self._run_tunnel(
            SimpleNamespace(enabled=True, bastion_id="managed-bastion-id")
        )

        mock_parse.assert_called_once_with(
            "managed-bastion-id", ["node-rg"], "sub-id"
        )

    def test_explicit_bastion_takes_precedence(self):
        mock_parse = self._run_tunnel(
            SimpleNamespace(enabled=True, bastion_id="managed-bastion-id"),
            bastion="explicit-bastion-id",
        )

        mock_parse.assert_called_once_with(
            "explicit-bastion-id", ["node-rg"], "sub-id"
        )

    def test_disabled_managed_bastion_uses_discovery(self):
        mock_parse = self._run_tunnel(
            SimpleNamespace(enabled=False, bastion_id="managed-bastion-id")
        )

        mock_parse.assert_called_once_with(None, ["node-rg"], "sub-id")


if __name__ == "__main__":
    unittest.main()
