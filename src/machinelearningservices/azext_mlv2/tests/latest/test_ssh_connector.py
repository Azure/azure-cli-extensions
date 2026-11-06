# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import importlib.util
import io
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
from knack import CLI
from knack.util import CommandResultItem


@pytest.fixture
def connector(monkeypatch):
    # These CLI-output tests do not use the optional WebSocket transport.
    websockets = ModuleType("websockets")
    websockets.client = ModuleType("websockets.client")
    websockets.client.connect = Mock(side_effect=AssertionError("Unexpected WebSocket connection"))
    websockets.exceptions = ModuleType("websockets.exceptions")
    for module in (websockets, websockets.client, websockets.exceptions):
        monkeypatch.setitem(sys.modules, module.__name__, module)

    # Load the ProxyCommand script without importing the extension's command table.
    path = Path(__file__).resolve().parents[2] / "manual" / "custom" / "_ssh_connector.py"
    spec = importlib.util.spec_from_file_location("_ssh_connector", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_az_cli_keeps_token_output_off_transport(connector, monkeypatch, capfd):
    token = {"accessToken": "synthetic-token-not-a-credential", "tokenType": "Bearer"}
    cli = SimpleNamespace(result=SimpleNamespace(result=token, error=None))

    def invoke(args, out_file=None):
        print(json.dumps(token), file=out_file)

    cli.invoke = Mock(side_effect=invoke)
    monkeypatch.setattr(connector, "get_default_cli", Mock(return_value=cli))
    args = ["account", "get-access-token", "--scope", "https://management.core.windows.net/.default"]

    assert connector.run_az_cli(args) is token

    cli.invoke.assert_called_once()
    assert cli.invoke.call_args.args == (args,)
    output = cli.invoke.call_args.kwargs["out_file"]
    assert isinstance(output, io.StringIO)
    assert json.loads(output.getvalue()) == token
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_run_az_cli_captures_knack_output(connector, monkeypatch, capfd, tmp_path):
    token = {"accessToken": "synthetic-token-not-a-credential", "tokenType": "Bearer"}
    invocation = Mock(data={"output": "json"})
    invocation.execute.return_value = CommandResultItem(token)
    cli = CLI(
        config_dir=str(tmp_path),
        out_file=sys.stdout,
        invocation_cls=Mock(return_value=invocation),
        logging_cls=Mock(),
        completion_cls=Mock(return_value=Mock(get_completion_args=Mock(return_value=None))),
    )
    monkeypatch.setattr(connector, "get_default_cli", Mock(return_value=cli))
    args = ["account", "get-access-token"]

    # Exercise the real formatter and establish that the default output leaks the token.
    assert cli.invoke(args) == 0
    assert json.loads(capfd.readouterr().out) == token

    assert connector.run_az_cli(args) is token
    captured = capfd.readouterr()
    assert captured.out == ""
    assert captured.err == ""


@pytest.mark.parametrize("result", [None, SimpleNamespace(result=None, error=None)])
def test_run_az_cli_rejects_missing_result(connector, monkeypatch, result):
    cli = Mock(result=result)
    monkeypatch.setattr(connector, "get_default_cli", Mock(return_value=cli))

    with pytest.raises(Exception, match="^az cli failed$"):
        connector.run_az_cli(["account", "get-access-token"])


def test_run_az_cli_preserves_command_error(connector, monkeypatch):
    error = RuntimeError("synthetic CLI failure")
    cli = Mock(result=SimpleNamespace(result=None, error=error))
    monkeypatch.setattr(connector, "get_default_cli", Mock(return_value=cli))

    with pytest.raises(RuntimeError) as raised:
        connector.run_az_cli(["account", "get-access-token"])

    assert raised.value is error
