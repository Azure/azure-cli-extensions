# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from azure.ai.ml.entities import ServiceInstance
from azext_mlv2.manual.custom import _ssh_command


@pytest.fixture
def native_proxy_command(monkeypatch):
    monkeypatch.setattr(socket.socket, "connect", Mock(side_effect=AssertionError("Network forbidden")))
    monkeypatch.setattr(socket, "create_connection", Mock(side_effect=AssertionError("Network forbidden")))
    monkeypatch.setattr(socket, "getaddrinfo", Mock(side_effect=AssertionError("DNS forbidden")))
    with TemporaryDirectory(prefix="ml-ssh-parser-") as directory:
        root = Path(directory) / "CLI user's $HOME 100%h \u00e9 \u5de5\u5177"
        root.mkdir()
        executable = root / "Python runtime"
        if os.name != "nt":
            executable.symlink_to(sys.executable)
        connector = root / "_ssh_connector.py"
        # This is an argv recorder, not the network/credential-bearing SSH connector.
        connector.write_text("import json, sys\nprint(json.dumps(sys.argv[1:]))\n", encoding="utf-8")
        config = root / "empty.conf"
        config.touch()
        endpoint = "wss://proxy.example:443/run%20files"
        arguments = [
            "--is-compute", "argument with spaces", "O'Brien", 'quoted"value',
            "literal $HOME", "100%h", "%USERPROFILE%", "\u00e9", "", "trailing\\",
        ]
        ssh_arguments = ["-N", "-L", "8080:localhost:80", "-o", "ServerAliveInterval=17"]
        services = {"ssh": ServiceInstance(type="SSH", status="Running", properties={"ProxyEndpoint": endpoint})}
        monkeypatch.setattr(_ssh_command, "sys", SimpleNamespace(executable=str(executable)))
        monkeypatch.setattr(_ssh_command, "__file__", str(root / "_ssh_command.py"))
        command = _ssh_command.get_ssh_command(services, 0, None, ssh_args=ssh_arguments, connector_args=arguments)
        assert isinstance(command, list)
        assert command[-len(ssh_arguments) - 1:] == [*ssh_arguments, "azureuser@" + endpoint]
        proxy = command[command.index("-o") + 1].removeprefix("ProxyCommand=")
        environment = dict(os.environ, HOME=str(root))
        environment.pop("BASH_ENV", None)
        environment.pop("ENV", None)
        yield SimpleNamespace(
            command=command, proxy=proxy, config=config, environment=environment,
            arguments=[endpoint, *arguments],
        )


def test_native_openssh_validates_proxy_command_without_connecting(native_proxy_command):
    probe = native_proxy_command
    if not shutil.which(probe.command[0]):
        pytest.skip("Native OpenSSH is not installed")
    # -G and an empty owned config prevent a connection or execution of a ProxyCommand/Match directive.
    result = subprocess.run(
        [probe.command[0], "-G", "-F", str(probe.config), *probe.command[1:]],
        shell=False, capture_output=True, encoding="utf-8", env=probe.environment, timeout=30, check=False,
    )
    assert result.returncode == 0, result.stderr
    actual = next(line for line in result.stdout.splitlines() if line.startswith("proxycommand "))
    assert actual.removeprefix("proxycommand ") == probe.proxy
    assert "serveraliveinterval 17" in result.stdout.splitlines()
    assert any(line.startswith("localforward ") and "8080" in line for line in result.stdout.splitlines())


@pytest.mark.skipif(os.name == "nt", reason="Requires a native POSIX shell")
@pytest.mark.parametrize("shell_name", ["sh", "bash"])
def test_native_posix_shell_preserves_benign_recorder_arguments(native_proxy_command, shell_name):
    probe = native_proxy_command
    shell = shutil.which(shell_name)
    if not shell:
        pytest.skip(f"{shell_name} is not installed")

    def literal_percent(match):
        assert match.group(1) == "%", "Unexpected OpenSSH token expansion"
        return "%"

    expanded = re.sub(r"%(.)", literal_percent, probe.proxy)
    result = subprocess.run(
        [shell, "-c", "exec " + expanded],
        shell=False, capture_output=True, encoding="utf-8", env=probe.environment, timeout=30, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == probe.arguments
