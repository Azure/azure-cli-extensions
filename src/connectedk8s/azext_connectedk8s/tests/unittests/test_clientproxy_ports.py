# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import errno
import socket
from unittest.mock import MagicMock, call

import pytest
from azure.cli.core.azclierror import CLIInternalError

from azext_connectedk8s.clientproxyhelper import _utils


@pytest.fixture(autouse=True)
def macos(monkeypatch):
    monkeypatch.setattr(_utils.platform, "system", lambda: "Darwin")


@pytest.mark.parametrize("as_string", [False, True])
def test_darwin_detects_ipv4_listener_without_process_inspection(
    monkeypatch, as_string
):
    connections = MagicMock(side_effect=AssertionError("Must not inspect processes"))
    monkeypatch.setattr(_utils, "net_connections", connections)
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        port = listener.getsockname()[1]
        assert _utils.check_if_port_is_open(str(port) if as_string else port)
    connections.assert_not_called()


def test_darwin_detects_ipv6_only_listener():
    try:
        listener = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    except OSError as error:
        if error.errno in (errno.EAFNOSUPPORT, errno.EPROTONOSUPPORT):
            pytest.skip("IPv6 is unavailable")
        raise
    with listener:
        listener.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
        try:
            listener.bind(("::1", 0))
        except OSError as error:
            if error.errno == errno.EADDRNOTAVAIL:
                pytest.skip("IPv6 loopback is unavailable")
            raise
        listener.listen()
        assert _utils.check_if_port_is_open(listener.getsockname()[1])


@pytest.mark.parametrize("port", [47013, "47013"])
def test_darwin_unused_port_and_cli_string_conversion(monkeypatch, port):
    create_socket = MagicMock()
    monkeypatch.setattr(_utils.socket, "socket", create_socket)
    assert not _utils.check_if_port_is_open(port)
    assert create_socket.call_count == 2
    probe = create_socket.return_value.__enter__.return_value
    assert probe.bind.call_args_list == [
        call(("127.0.0.1", 47013)),
        call(("::1", 47013)),
    ]


@pytest.mark.parametrize(
    "error_number",
    [errno.EAFNOSUPPORT, errno.EADDRNOTAVAIL, errno.EPROTONOSUPPORT],
)
def test_darwin_missing_ipv6_support(monkeypatch, error_number):
    ipv4 = MagicMock()
    create_socket = MagicMock(
        side_effect=[ipv4, OSError(error_number, "IPv6 unavailable")]
    )
    monkeypatch.setattr(_utils.socket, "socket", create_socket)
    assert not _utils.check_if_port_is_open(47012)
    ipv4.__enter__.return_value.bind.assert_called_once_with(("127.0.0.1", 47012))


def test_darwin_unexpected_error_is_not_reported_as_available(monkeypatch):
    monkeypatch.setattr(
        _utils.socket,
        "socket",
        MagicMock(side_effect=PermissionError(errno.EACCES, "Permission denied")),
    )
    with pytest.raises(CLIInternalError, match="Failed to check local proxy port"):
        _utils.check_if_port_is_open(47012)


@pytest.mark.parametrize("system", ["Windows", "Linux"])
def test_other_platforms_keep_process_inspection(monkeypatch, system):
    monkeypatch.setattr(_utils.platform, "system", lambda: system)
    connections = MagicMock(return_value=[(0, 0, 0, ("127.0.0.1", 47010))])
    create_socket = MagicMock()
    monkeypatch.setattr(_utils, "net_connections", connections)
    monkeypatch.setattr(_utils.socket, "socket", create_socket)
    assert _utils.check_if_port_is_open(47010)
    connections.assert_called_once_with(kind="inet")
    create_socket.assert_not_called()


def test_other_platforms_unused_port(monkeypatch):
    monkeypatch.setattr(_utils.platform, "system", lambda: "Linux")
    monkeypatch.setattr(_utils, "net_connections", MagicMock(return_value=[]))
    assert not _utils.check_if_port_is_open(47012)
