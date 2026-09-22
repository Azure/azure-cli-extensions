# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import ctypes
import ntpath
import os
import pathlib
import posixpath
import re
import shlex
import socket
import subprocess
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from knack.util import CLIError

from azure.ai.ml.entities import ServiceInstance
from azure.ai.ml.exceptions import JobException, ValidationException
from azext_mlv2.manual.custom import _ssh_command, compute, job


ENDPOINT = "wss://node-0.eastus.instances.azureml.ms"
VALID_ENDPOINTS = [
    ENDPOINT,
    "ws://localhost:8080",
    "wss://proxy.example:443",
    "wss://proxy.example:00443",
    "wss://proxy.example:65535",
    "wss://proxy.example.",
    "WSS://PROXY.EXAMPLE/service-prefix/node_0",
    "wss://127.0.0.1:8443",
    "wss://[::1]:443",
    "wss://[2001:db8::1]/service/node-0",
    "wss://proxy.example/",
    "wss://proxy.example/service-prefix/node_0.1~test",
    "wss://proxy.example/run%20files/%25id/%E2%82%AC",
    "wss://xn--caf-dma.example",
    "wss://caf\u00e9.example",
]
INVALID_ENDPOINTS = [
    None,
    "",
    False,
    True,
    0,
    443,
    [],
    ["wss://proxy.example"],
    {},
    {"host": "proxy.example"},
    b"wss://proxy.example",
    " ",
    "proxy.example",
    "proxy.example:443",
    "//proxy.example",
    "http://proxy.example",
    "file:///local/path",
    "ssh://proxy.example",
    "wss://",
    "wss:///missing-host",
    "wss://user@proxy.example",
    "wss://user:password@proxy.example",
    "wss://proxy.example@other.example",
    "wss://-proxy.example",
    "wss://proxy-.example",
    "wss://proxy..example",
    "wss://proxy_example",
    "wss://" + "a" * 64 + ".example",
    "wss://" + ".".join(["a" * 63] * 4),
    "wss://999.1.2.3",
    "wss://proxy.example:",
    "wss://proxy.example:0",
    "wss://proxy.example:65536",
    "wss://proxy.example:-1",
    "wss://proxy.example:+443",
    "wss://proxy.example:443suffix",
    "wss://proxy.example:443:22",
    "wss://proxy.example:\u0664\u0664\u0663",
    "wss://[::1",
    "wss://[not-an-ipv6-address]",
    "wss://[::1]suffix",
    "wss://[::1]:",
    "wss://[::1]:65536",
    "wss://2001:db8::1",
    "wss://[fe80::1%25eth0]",
    "wss://proxy.example?query=value",
    "wss://proxy.example?",
    "wss://proxy.example#fragment",
    "wss://proxy.example#",
    "wss://proxy.example/path with spaces",
    "wss://proxy.example/path\\segment",
    "wss://proxy.example/path%invalid",
    "wss://proxy.example/path%2",
    "wss://proxy.example/%h",
    "wss://proxy.example/%00",
    "wss://proxy.example/%0a",
    "wss://proxy.example/%0D",
    "wss://proxy.example/%7f",
    "wss://proxy.example/<unknown>",
    'wss://proxy.example" & unexpected & "',
    "wss://proxy.example;unexpected",
    "wss://proxy.example|unexpected",
    "wss://proxy.example/$(unexpected)",
    "wss://proxy.example/`unexpected`",
    "wss://proxy.example/'quoted'",
    "wss://proxy.example/<redirect>",
    "-oProxyCommand=unexpected",
]
CONTROL_CHARACTERS = [chr(value) for value in range(32)] + [
    "\x7f", "\x85", "\xa0", "\u200b", "\u2028", "\u2029", "\u202e"
]


def _services(endpoint=ENDPOINT):
    return {"ssh": ServiceInstance(type="SSH", status="Running", properties={"ProxyEndpoint": endpoint})}


@pytest.fixture(autouse=True)
def no_external_io(monkeypatch):
    for name in ("Popen", "call", "check_call", "check_output", "run"):
        monkeypatch.setattr(subprocess, name, Mock(side_effect=AssertionError("Unexpected subprocess")))
    monkeypatch.setattr(socket.socket, "connect", Mock(side_effect=AssertionError("Unexpected network connection")))
    monkeypatch.setattr(socket, "create_connection", Mock(side_effect=AssertionError("Unexpected network connection")))
    monkeypatch.setattr(socket, "getaddrinfo", Mock(side_effect=AssertionError("Unexpected DNS lookup")))
    monkeypatch.setattr(_ssh_command.platform, "architecture", Mock(return_value=("64bit", "")))


@pytest.fixture(params=["posix", "nt"])
def target_platform(request, monkeypatch):
    windows = request.param == "nt"
    path_type = pathlib.PureWindowsPath if windows else pathlib.PurePosixPath
    root = "C:\\CLI user's 100%h \u00e9\\tools" if windows else "/opt/CLI user's 100%h \u00e9/tools"
    python_path = str(path_type(root) / "Python runtime" / ("python.exe" if windows else "python"))
    module_path = str(path_type(root) / "ML extension" / "_ssh_command.py")
    monkeypatch.setattr(
        _ssh_command, "os",
        SimpleNamespace(name=request.param, path=ntpath if windows else posixpath, environ={"SystemRoot": root}),
    )
    monkeypatch.setattr(_ssh_command, "pathlib", SimpleNamespace(Path=path_type))
    monkeypatch.setattr(_ssh_command, "sys", SimpleNamespace(executable=python_path))
    monkeypatch.setattr(_ssh_command, "__file__", module_path)
    return SimpleNamespace(
        name=request.param,
        root=root,
        python=python_path,
        connector=str(path_type(module_path).parent / "_ssh_connector.py"),
    )


def _expand_proxy_tokens(command):
    # OpenSSH expands these tokens before either the POSIX shell or CreateProcess.
    substitutions = {"%": "%", "h": "expanded-host", "n": "original-host", "p": "22", "r": "azureuser"}
    return re.sub(r"%(.)", lambda match: substitutions[match.group(1)], command)


def _windows_split(command):
    if os.name != "nt":
        pytest.skip("Native Windows command-line parser is only available on Windows")
    shell32 = ctypes.WinDLL("shell32", use_last_error=True)
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    shell32.CommandLineToArgvW.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
    shell32.CommandLineToArgvW.restype = ctypes.POINTER(ctypes.c_wchar_p)
    kernel32.LocalFree.argtypes = [ctypes.c_void_p]
    kernel32.LocalFree.restype = ctypes.c_void_p
    count = ctypes.c_int()
    arguments = shell32.CommandLineToArgvW(command, ctypes.byref(count))
    if not arguments:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return list(arguments[:count.value])
    finally:
        kernel32.LocalFree(arguments)


def _assert_openssh_option_quotes(command):
    # OpenSSH recognizes backslash-escaped quotes even inside single quotes.
    quote = None
    index = 0
    while index < len(command):
        character = command[index]
        if character == "\\" and index + 1 < len(command) and command[index + 1] in ("'", '"', "\\"):
            index += 2
            continue
        if quote is None and character in ("'", '"'):
            quote = character
        elif character == quote:
            quote = None
        index += 1
    assert quote is None, "OpenSSH would reject this ProxyCommand as invalid quotes"


def _proxy_arguments(command, target_platform):
    assert isinstance(command, list)
    option = command[command.index("-o") + 1]
    assert option.startswith("ProxyCommand=")
    proxy = option[len("ProxyCommand="):]
    _assert_openssh_option_quotes(proxy)
    expanded = _expand_proxy_tokens(proxy)
    if target_platform.name == "nt":
        return _windows_split(expanded)
    # Unlike shlex, the POSIX shell consumes these escapes inside double quotes.
    return [argument.replace("\\$", "$").replace("\\`", "`") for argument in shlex.split(expanded)]


@pytest.mark.parametrize("endpoint", VALID_ENDPOINTS)
def test_valid_endpoint_is_one_proxy_argument(endpoint, target_platform):
    command = _ssh_command.get_ssh_command(_services(endpoint), 0, None)

    assert _proxy_arguments(command, target_platform) == [
        target_platform.python, target_platform.connector, endpoint
    ]
    assert command[-1] == "azureuser@" + endpoint
    assert command[1:3] == ["-v", "-o"]
    assert "-p" not in command


@pytest.mark.parametrize("endpoint", INVALID_ENDPOINTS + ["https://proxy.example"])
def test_invalid_endpoint_is_rejected(endpoint):
    with pytest.raises((JobException, ValidationException), match="ProxyEndpoint"):
        _ssh_command.get_ssh_command(_services(endpoint), 0, None)
    subprocess.Popen.assert_not_called()
    subprocess.check_output.assert_not_called()


@pytest.mark.parametrize("character", CONTROL_CHARACTERS)
@pytest.mark.parametrize("position", ["prefix", "host", "path", "suffix"])
def test_raw_controls_are_rejected_before_url_parsing(character, position):
    endpoint = {
        "prefix": character + ENDPOINT,
        "host": "wss://proxy" + character + ".example",
        "path": ENDPOINT + "/path" + character + "segment",
        "suffix": ENDPOINT + character,
    }[position]
    with pytest.raises(ValidationException, match="ProxyEndpoint"):
        _ssh_command.get_ssh_command(_services(endpoint), 0, None)


@pytest.mark.parametrize("node_index", [0, 1, 27])
@pytest.mark.parametrize("endpoint", [
    "wss://node-<nodeIndex>.example:443/service",
    "wss://proxy.example/nodes/<nodeIndex>",
    ENDPOINT,
])
def test_node_substitution_is_preserved(endpoint, node_index, target_platform):
    expected = endpoint.replace("<nodeIndex>", str(node_index))
    command = _ssh_command.get_ssh_command(_services(endpoint), node_index, None)
    assert _proxy_arguments(command, target_platform)[2] == expected
    assert command[-1] == "azureuser@" + expected


def test_substitution_cannot_introduce_invalid_endpoint():
    with pytest.raises(ValidationException, match="ProxyEndpoint"):
        _ssh_command.get_ssh_command(_services("wss://node-<nodeIndex>.example"), "0;unexpected", None)


@pytest.mark.parametrize("architecture,system_directory", [("32bit", "SysNative"), ("64bit", "System32")])
def test_windows_ssh_executable_selection(architecture, system_directory, target_platform, monkeypatch):
    if target_platform.name != "nt":
        pytest.skip("Windows executable selection")
    monkeypatch.setattr(_ssh_command.platform, "architecture", Mock(return_value=(architecture, "")))
    command = _ssh_command.get_ssh_command(_services(), 0, None)
    assert command[0] == ntpath.join(target_platform.root, system_directory, "OpenSSH", "ssh.exe")


def test_posix_ssh_executable_selection(target_platform):
    if target_platform.name != "posix":
        pytest.skip("POSIX executable selection")
    command = _ssh_command.get_ssh_command(_services(), 0, None)
    assert command[0] == "ssh"


def test_key_and_extra_arguments_keep_boundaries(target_platform, tmp_path):
    key = tmp_path / "private key \u00e9 %h"
    key.write_text("test-only key placeholder", encoding="utf-8")
    ssh_args = ["-L", "8080:localhost:80", "-o", "ServerAliveInterval=30", "remote argument"]
    connector_args = ["--is-compute", "one argument", "", "literal $HOME; & ' \" ` ( )", "100%h %r %%"]
    command = _ssh_command.get_ssh_command(_services(), 0, str(key), ssh_args, connector_args)

    assert command[command.index("-i") + 1] == str(key)
    assert command[-len(ssh_args):] == ssh_args
    assert _proxy_arguments(command, target_platform) == [
        target_platform.python, target_platform.connector, ENDPOINT, *connector_args
    ]
    assert ssh_args == ["-L", "8080:localhost:80", "-o", "ServerAliveInterval=30", "remote argument"]
    assert connector_args[-1] == "100%h %r %%"
    if os.name == "nt":
        assert _windows_split(subprocess.list2cmdline(command)) == command


def test_nested_percent_expansion_does_not_change_literals(target_platform):
    endpoint = ENDPOINT + "/path%20with%25escapes"
    connector_args = ["%h", "%n", "%p", "%r", "%", "%%", "%USERPROFILE%"]
    command = _ssh_command.get_ssh_command(_services(endpoint), 0, None, connector_args=connector_args)
    assert _proxy_arguments(command, target_platform) == [
        target_platform.python, target_platform.connector, endpoint, *connector_args
    ]


def test_posix_nested_arguments_are_shell_quoted(target_platform):
    if target_platform.name != "posix":
        pytest.skip("POSIX shell quoting")
    arguments = ["$HOME", "$(literal)", "`literal`", "literal;value", "'quoted'", "", "a\nb", "*"]
    command = _ssh_command.get_ssh_command(_services(), 0, None, connector_args=arguments)
    option = command[command.index("-o") + 1]
    assert '"\\$HOME"' in option
    assert '"\\$(literal)"' in option
    assert '"\\`literal\\`"' in option
    assert '"literal;value"' in option
    assert '"*"' in option
    assert _proxy_arguments(command, target_platform)[3:] == arguments


def test_windows_nested_backslashes_and_quotes(target_platform):
    if target_platform.name != "nt":
        pytest.skip("Windows argument quoting")
    arguments = ["C:\\path with spaces\\", 'value"with"quotes', "trailing\\\\", ""]
    command = _ssh_command.get_ssh_command(_services(), 0, None, connector_args=arguments)
    assert _proxy_arguments(command, target_platform)[3:] == arguments


@pytest.mark.parametrize("argument", [
    "trailing\\",
    "trailing\\\\",
    "O'Brien",
    "backslash\\'quote",
    'backslash\\"quote',
    "#not-a-comment",
    "\\$HOME",
    "\\`literal`",
])
def test_proxy_command_passes_both_openssh_and_platform_parsers(argument, target_platform):
    command = _ssh_command.get_ssh_command(_services(), 0, None, connector_args=[argument])
    assert _proxy_arguments(command, target_platform)[3:] == [argument]


def test_apostrophes_in_paths_without_spaces(target_platform, monkeypatch):
    path_type = pathlib.PureWindowsPath if target_platform.name == "nt" else pathlib.PurePosixPath
    root = path_type("C:\\O'Brien\\\u00e9" if target_platform.name == "nt" else "/opt/O'Brien/\u00e9")
    executable = str(root / "python")
    monkeypatch.setattr(_ssh_command.sys, "executable", executable)
    monkeypatch.setattr(_ssh_command, "__file__", str(root / "_ssh_command.py"))
    command = _ssh_command.get_ssh_command(_services(), 0, None)
    assert _proxy_arguments(command, target_platform)[:2] == [executable, str(root / "_ssh_connector.py")]


@pytest.mark.parametrize("services,error_type,message", [
    ({}, ValidationException, "does not have services"),
    (None, ValidationException, "does not have services"),
    ({"jupyter": ServiceInstance(type="Jupyter")}, ValidationException, "ssh enabled"),
    ({"ssh": ServiceInstance(type="SSH", status="Starting")}, ValidationException, "Running"),
    ({"ssh": ServiceInstance(type="SSH", status="Running")}, JobException, "missing ProxyEndpoint"),
    ({"ssh": ServiceInstance(type="SSH", status="Running", properties={})}, JobException, "missing ProxyEndpoint"),
])
def test_service_validation_is_preserved(services, error_type, message):
    with pytest.raises(error_type, match=message):
        _ssh_command.get_ssh_command(services, 3, None)


def test_first_ssh_service_is_selected(target_platform):
    services = {
        "jupyter": ServiceInstance(type="Jupyter", status="Running"),
        **_services(ENDPOINT),
        "another-ssh": ServiceInstance(type="SSH", status="Running", properties={"ProxyEndpoint": "invalid"}),
    }
    command = _ssh_command.get_ssh_command(services, 0, None)
    assert _proxy_arguments(command, target_platform)[2] == ENDPOINT


@pytest.fixture(params=[job, compute], ids=["job", "compute"])
def caller(request, monkeypatch):
    module = request.param
    client = Mock()
    dependencies = Mock(return_value=True)
    launch = Mock(return_value=0)
    monkeypatch.setattr(module, "get_ml_client", Mock(return_value=(client, False)))
    monkeypatch.setattr(module, "has_ssh_dependencies_installed", dependencies)
    monkeypatch.setattr(module.subprocess, "call", launch)
    return SimpleNamespace(
        module=module,
        client=client,
        dependencies=dependencies,
        launch=launch,
        invoke=module.ml_job_connect_ssh if module is job else module.ml_compute_connect_ssh,
    )


def _set_caller_endpoint(caller, endpoint):
    if caller.module is job:
        caller.client.jobs.show_services.return_value = _services(endpoint)
    else:
        caller.client.compute.get.return_value = SimpleNamespace(
            type=compute.ComputeType.COMPUTEINSTANCE,
            services=[{"display_name": "Jupyter", "endpoint_uri": endpoint}],
        )


@pytest.mark.parametrize("endpoint", INVALID_ENDPOINTS)
def test_callers_reject_invalid_endpoint_before_any_process(caller, endpoint):
    _set_caller_endpoint(caller, endpoint)
    with pytest.raises((CLIError, JobException, ValidationException)):
        caller.invoke(SimpleNamespace(cli_ctx=Mock()), "group", "workspace", "name")
    caller.dependencies.assert_not_called()
    caller.launch.assert_not_called()
    subprocess.Popen.assert_not_called()
    subprocess.check_call.assert_not_called()
    subprocess.check_output.assert_not_called()


def test_callers_launch_argv_without_shell(caller, target_platform, tmp_path):
    key = tmp_path / "private key \u00e9"
    key.write_text("test-only key placeholder", encoding="utf-8")
    endpoint = ENDPOINT if caller.module is job else ENDPOINT.replace("wss://", "https://") + "/tree/"
    _set_caller_endpoint(caller, endpoint)
    caller.invoke(SimpleNamespace(cli_ctx=Mock()), "group", "workspace", "name", private_key_file_path=str(key))

    caller.dependencies.assert_called_once_with()
    caller.launch.assert_called_once()
    arguments, options = caller.launch.call_args
    assert options == {"shell": False}
    assert len(arguments) == 1
    command = arguments[0]
    expected_connector_args = [] if caller.module is job else ["--is-compute"]
    assert _proxy_arguments(command, target_platform) == [
        target_platform.python, target_platform.connector, ENDPOINT, *expected_connector_args
    ]
    assert command[command.index("-i") + 1] == str(key)
    assert command[-1] == "azureuser@" + ENDPOINT
    subprocess.Popen.assert_not_called()


def test_job_caller_forwards_node_selection(monkeypatch, target_platform):
    client = Mock()
    client.jobs.show_services.return_value = _services("wss://node-<nodeIndex>.example")
    monkeypatch.setattr(job, "get_ml_client", Mock(return_value=(client, False)))
    monkeypatch.setattr(job, "has_ssh_dependencies_installed", Mock(return_value=True))
    launch = Mock(return_value=0)
    monkeypatch.setattr(job.subprocess, "call", launch)
    job.ml_job_connect_ssh(SimpleNamespace(cli_ctx=Mock()), "group", "workspace", "name", node_index=7)
    client.jobs.show_services.assert_called_once_with("name", 7)
    assert _proxy_arguments(launch.call_args.args[0], target_platform)[2] == "wss://node-7.example"


def test_declining_dependencies_does_not_launch_ssh(caller, target_platform):
    _set_caller_endpoint(caller, ENDPOINT)
    caller.dependencies.return_value = False
    caller.invoke(SimpleNamespace(cli_ctx=Mock()), "group", "workspace", "name")
    caller.dependencies.assert_called_once_with()
    caller.launch.assert_not_called()


def test_missing_key_does_not_launch_process(caller, tmp_path):
    with pytest.raises((CLIError, ValidationException), match="There is no file on target path"):
        caller.invoke(
            SimpleNamespace(cli_ctx=Mock()), "group", "workspace", "name",
            private_key_file_path=str(tmp_path / "missing key"),
        )
    caller.dependencies.assert_not_called()
    caller.launch.assert_not_called()
    caller.client.jobs.show_services.assert_not_called()
    caller.client.compute.get.assert_not_called()


def test_dependency_detection_uses_argument_list(monkeypatch):
    freeze = Mock(return_value=b"websockets==12.0\nother==1.0\n")
    monkeypatch.setattr(_ssh_command.subprocess, "check_output", freeze)
    assert _ssh_command.has_ssh_dependencies_installed()
    freeze.assert_called_once_with([_ssh_command.sys.executable, "-m", "pip", "freeze"])
    subprocess.check_call.assert_not_called()


@pytest.mark.parametrize("consent", [False, True])
def test_dependency_installation_requires_confirmation(monkeypatch, consent):
    freeze = Mock(return_value=b"other==1.0\n")
    install = Mock()
    monkeypatch.setattr(_ssh_command.subprocess, "check_output", freeze)
    monkeypatch.setattr(_ssh_command.subprocess, "check_call", install)
    monkeypatch.setattr(_ssh_command, "_confirm", Mock(return_value=consent))
    assert _ssh_command.has_ssh_dependencies_installed() is consent
    if consent:
        install.assert_called_once_with([_ssh_command.sys.executable, "-m", "pip", "install", "websockets"])
    else:
        install.assert_not_called()
