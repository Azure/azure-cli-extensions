# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import base64
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock
import zipfile

import pytest
from knack.util import CLIError

from azext_edge_action.custom import EdgeActionSwapDefaultMgmtClient, deploy_edge_action_version


HANDLER = b"function handler(event) { return event; }"


@pytest.fixture
def deploy(monkeypatch):
    generated = Mock()
    monkeypatch.setattr(
        "azext_edge_action.aaz.latest.edge_action.version._deploy_version_code.DeployVersionCode", generated)
    cmd = SimpleNamespace(cli_ctx=Mock())
    return cmd, generated


@pytest.mark.parametrize("deployment_type", [None, "file"])
def test_javascript_deployment_encodes_original_bytes(deploy, tmp_path, deployment_type):
    cmd, generated = deploy
    path = tmp_path / "file with spaces.js"
    path.write_bytes(HANDLER)
    result = deploy_edge_action_version(cmd, "rg", "action", "v1", str(path), deployment_type)
    generated.assert_called_once_with(cli_ctx=cmd.cli_ctx)
    generated.return_value.assert_called_once_with(command_args={
        "resource_group": "rg", "edge_action_name": "action", "version": "v1",
        "content": base64.b64encode(HANDLER).decode("ascii"), "name": "v1", "no_wait": False,
    })
    assert result is generated.return_value.return_value


@pytest.mark.parametrize("deployment_type", [None, "zip"])
def test_zip_deployment_preserves_archive_bytes(deploy, tmp_path, deployment_type):
    cmd, generated = deploy
    path = tmp_path / "package.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("handler.js", HANDLER)
    deploy_edge_action_version(cmd, "rg", "action", "v1", str(path), deployment_type, no_wait=True)
    args = generated.return_value.call_args.kwargs["command_args"]
    assert base64.b64decode(args["content"], validate=True) == path.read_bytes()
    assert args["no_wait"] is True


def test_javascript_auto_zip_contains_only_source_file(deploy, tmp_path):
    cmd, generated = deploy
    path = tmp_path / "handler.js"
    path.write_bytes(HANDLER)
    deploy_edge_action_version(cmd, "rg", "action", "v1", str(path), "zip")
    args = generated.return_value.call_args.kwargs["command_args"]
    with zipfile.ZipFile(BytesIO(base64.b64decode(args["content"], validate=True))) as archive:
        assert archive.namelist() == ["handler.js"]
        assert archive.read("handler.js") == HANDLER


@pytest.mark.parametrize("filename,deployment_type,message", [
    ("handler.txt", None, "Cannot determine deployment type"),
    ("handler.zip", "file", "requires a JavaScript"),
    ("handler.txt", "zip", "requires a JavaScript"),
    ("handler.js", "invalid", "Invalid deployment type"),
])
def test_invalid_deployment_rejected_before_generated_command(
        deploy, tmp_path, filename, deployment_type, message):
    cmd, generated = deploy
    path = tmp_path / filename
    path.write_bytes(HANDLER)
    with pytest.raises(CLIError, match=message):
        deploy_edge_action_version(cmd, "rg", "action", "v1", str(path), deployment_type)
    generated.assert_not_called()


def test_missing_file_rejected_before_generated_command(deploy, tmp_path):
    cmd, generated = deploy
    with pytest.raises(CLIError, match="File not found"):
        deploy_edge_action_version(cmd, "rg", "action", "v1", str(tmp_path / "missing.js"))
    generated.assert_not_called()


def test_generated_command_failure_propagates(deploy, tmp_path):
    cmd, generated = deploy
    path = tmp_path / "handler.js"
    path.write_bytes(HANDLER)
    generated.return_value.side_effect = CLIError("Deployment rejected")
    with pytest.raises(CLIError, match="Deployment rejected"):
        deploy_edge_action_version(cmd, "rg", "action", "v1", str(path))


@pytest.mark.parametrize("has_deserializer", [False, True])
def test_swap_default_client_preserves_existing_deserializer(monkeypatch, has_deserializer):
    build_polling = Mock()
    monkeypatch.setattr("azure.cli.core.aaz._client.AAZMgmtClient.build_lro_polling", build_polling)
    client = object.__new__(EdgeActionSwapDefaultMgmtClient)
    session, error_callback = Mock(), Mock()
    deserialize = Mock() if has_deserializer else None
    options = {"final-state-via": "location"}
    result = client.build_lro_polling(False, session, deserialize, error_callback, lro_options=options)
    assert result is build_polling.return_value
    no_wait, actual_session, actual_deserialize, actual_error = build_polling.call_args.args
    assert no_wait is False
    assert actual_session is session
    assert actual_error is error_callback
    assert build_polling.call_args.kwargs == {"lro_options": options, "path_format_arguments": None}
    if has_deserializer:
        assert actual_deserialize is deserialize
        deserialize.assert_not_called()
    else:
        response = Mock()
        assert actual_deserialize(response) is None
        assert response.mock_calls == []
